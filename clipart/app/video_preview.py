"""
video_preview.py — Виджет превью видео с наложением CTA-элементов.

Использует OpenCV для чтения кадров и QPainter для отрисовки оверлеев.
Поддерживает:
  • воспроизведение / пауза
  • перемотка через слайдер
  • размещение элементов кликом
  • перетаскивание (drag) размещённых элементов
  • масштабирование угловыми маркерами
  • контекстное меню (удаление)
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional, List, Dict

import cv2
import numpy as np
from PIL import Image as PILImage

from PyQt6.QtCore import (
    Qt, QTimer, QPointF, QRectF, QSize, pyqtSignal, QThread
)
from PyQt6.QtGui import (
    QImage, QPixmap, QPainter, QColor, QPen, QCursor, QAction,
    QBrush, QFont, QMovie
)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton,
    QSizePolicy, QMenu, QFrame
)

from app.models import OverlayElement, Project


# ---------------------------------------------------------------------------
# Кеш кадров GIF-анимаций
# ---------------------------------------------------------------------------
class GifCache:
    """
    Загружает все кадры GIF / APNG и хранит их как QPixmap.
    Для статичных изображений хранит один кадр.
    """

    def __init__(self):
        self._cache: Dict[str, List[QPixmap]] = {}
        self._durations: Dict[str, List[int]] = {}  # мс на кадр

    def load(self, path: str) -> None:
        if path in self._cache:
            return
        ext = Path(path).suffix.lower()
        if ext in ('.gif', '.apng'):
            self._load_animated(path)
        else:
            self._load_static(path)

    def _load_animated(self, path: str) -> None:
        frames: List[QPixmap] = []
        durations: List[int] = []
        try:
            pil_img = PILImage.open(path)
            n = getattr(pil_img, 'n_frames', 1)
            for i in range(n):
                pil_img.seek(i)
                frame_rgba = pil_img.convert("RGBA")
                data = frame_rgba.tobytes("raw", "RGBA")
                qimg = QImage(data, frame_rgba.width, frame_rgba.height,
                              QImage.Format.Format_RGBA8888).copy()
                frames.append(QPixmap.fromImage(qimg))
                dur = pil_img.info.get('duration', 100)
                durations.append(dur if dur > 0 else 100)
        except Exception:
            frames = []
            durations = []

        if not frames:
            # Фоллбэк — статичная загрузка
            self._load_static(path)
            return

        self._cache[path] = frames
        self._durations[path] = durations

    def _load_static(self, path: str) -> None:
        pm = QPixmap(path)
        if pm.isNull():
            # Пустой пиксмап-заглушка
            pm = QPixmap(64, 64)
            pm.fill(QColor(255, 0, 0, 128))
        self._cache[path] = [pm]
        self._durations[path] = [0]

    def get_frame(self, path: str, time_ms: int) -> Optional[QPixmap]:
        """Получить нужный кадр для заданного момента времени (мс)."""
        if path not in self._cache:
            self.load(path)
        frames = self._cache.get(path)
        if not frames:
            return None
        if len(frames) == 1:
            return frames[0]

        # Определяем кадр по суммарной длительности
        durations = self._durations[path]
        total_dur = sum(durations)
        if total_dur == 0:
            return frames[0]
        t = time_ms % total_dur
        accum = 0
        for i, dur in enumerate(durations):
            accum += dur
            if t < accum:
                return frames[i]
        return frames[-1]

    def clear(self) -> None:
        self._cache.clear()
        self._durations.clear()


# Глобальный кеш
gif_cache = GifCache()


# ---------------------------------------------------------------------------
# Основной виджет превью
# ---------------------------------------------------------------------------
class VideoPreviewWidget(QWidget):
    """Центральная область: показ видео-кадра + оверлеи."""

    # Сигналы
    element_placed = pyqtSignal(float, float)       # (x%, y%) — клик для размещения
    element_moved = pyqtSignal(str, float, float)    # (id, new_x%, new_y%)
    element_scaled = pyqtSignal(str, float)           # (id, new_scale)
    element_selected = pyqtSignal(str)                # id
    element_delete_requested = pyqtSignal(str)        # id
    time_changed = pyqtSignal(float)                  # текущее время (сек)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(480, 270)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)

        # Состояние видео
        self._cap: Optional[cv2.VideoCapture] = None
        self._fps: float = 30.0
        self._total_frames: int = 0
        self._current_frame: int = 0
        self._video_w: int = 0
        self._video_h: int = 0
        self._duration: float = 0.0
        self._playing: bool = False

        # Текущий кадр (QPixmap)
        self._frame_pixmap: Optional[QPixmap] = None
        self._display_rect: QRectF = QRectF()  # прямоугольник видео на виджете

        # Наложенные элементы
        self._project: Optional[Project] = None
        self._overlay_mode: bool = True  # показывать ли оверлеи

        # Режим размещения: если True — следующий клик помещает элемент
        self._placing: bool = False

        # Перетаскивание
        self._dragging_id: Optional[str] = None
        self._drag_offset: QPointF = QPointF()

        # Масштабирование угловым маркером
        self._scaling_id: Optional[str] = None
        self._scale_start_dist: float = 0.0
        self._scale_start_val: float = 100.0

        # Выделенный элемент
        self._selected_id: Optional[str] = None

        # Таймер воспроизведения
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer)

    # --- Открытие видео ---
    def open_video(self, path: str) -> bool:
        """Открыть видео-файл. Возвращает True при успехе."""
        self.stop()
        if self._cap:
            self._cap.release()

        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            return False

        self._cap = cap
        self._fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        self._total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._video_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._video_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._duration = self._total_frames / self._fps if self._fps > 0 else 0.0
        self._current_frame = 0

        self._read_current_frame()
        self.update()
        return True

    # --- Управление проектом ---
    def set_project(self, project: Project):
        self._project = project
        self.update()

    # --- Управление воспроизведением ---
    def play(self):
        if self._cap and not self._playing:
            self._playing = True
            interval = max(1, int(1000 / self._fps))
            self._timer.start(interval)

    def pause(self):
        self._playing = False
        self._timer.stop()

    def stop(self):
        self.pause()
        self._current_frame = 0
        if self._cap:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self._read_current_frame()
        self.update()

    def toggle_play(self):
        if self._playing:
            self.pause()
        else:
            self.play()

    def seek(self, frame: int):
        """Перемотка к указанному кадру."""
        if not self._cap:
            return
        frame = max(0, min(frame, self._total_frames - 1))
        self._current_frame = frame
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
        self._read_current_frame()
        self.time_changed.emit(self.current_time)
        self.update()

    def seek_time(self, t: float):
        """Перемотка к указанному времени (сек)."""
        if self._fps > 0:
            self.seek(int(t * self._fps))

    @property
    def current_time(self) -> float:
        return self._current_frame / self._fps if self._fps > 0 else 0.0

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def total_frames(self) -> int:
        return self._total_frames

    @property
    def video_size(self) -> tuple:
        return (self._video_w, self._video_h)

    @property
    def is_playing(self) -> bool:
        return self._playing

    # --- Режимы ---
    def set_overlay_mode(self, on: bool):
        self._overlay_mode = on
        self.update()

    def set_placing_mode(self, on: bool):
        self._placing = on
        if on:
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def set_selected(self, elem_id: Optional[str]):
        self._selected_id = elem_id
        self.update()

    # --- Внутренние методы ---
    def _read_current_frame(self):
        """Читает текущий кадр из OpenCV и конвертирует в QPixmap."""
        if not self._cap:
            return
        ret, frame = self._cap.read()
        if not ret:
            self.pause()
            return
        # BGR → RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
        self._frame_pixmap = QPixmap.fromImage(qimg)

    def _on_timer(self):
        """Вызывается таймером при воспроизведении."""
        if not self._cap:
            self.pause()
            return
        self._current_frame += 1
        if self._current_frame >= self._total_frames:
            self._current_frame = 0
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        self._read_current_frame()
        self.time_changed.emit(self.current_time)
        self.update()

    def _compute_display_rect(self) -> QRectF:
        """Рассчитывает прямоугольник видео с сохранением пропорций."""
        if not self._frame_pixmap or self._video_w == 0 or self._video_h == 0:
            return QRectF(0, 0, self.width(), self.height())

        widget_w = self.width()
        widget_h = self.height()
        video_aspect = self._video_w / self._video_h
        widget_aspect = widget_w / widget_h

        if video_aspect > widget_aspect:
            # Видео шире — ограничено по ширине
            dw = widget_w
            dh = widget_w / video_aspect
        else:
            dh = widget_h
            dw = widget_h * video_aspect

        dx = (widget_w - dw) / 2
        dy = (widget_h - dh) / 2
        return QRectF(dx, dy, dw, dh)

    def _video_to_widget(self, x_pct: float, y_pct: float) -> QPointF:
        """Процент видео → координаты виджета."""
        r = self._display_rect
        return QPointF(r.x() + r.width() * x_pct / 100.0,
                       r.y() + r.height() * y_pct / 100.0)

    def _widget_to_video(self, pos: QPointF) -> tuple:
        """Координаты виджета → проценты видео (x%, y%)."""
        r = self._display_rect
        if r.width() == 0 or r.height() == 0:
            return (50.0, 50.0)
        x_pct = (pos.x() - r.x()) / r.width() * 100.0
        y_pct = (pos.y() - r.y()) / r.height() * 100.0
        return (max(0, min(100, x_pct)), max(0, min(100, y_pct)))

    def _element_rect(self, elem: OverlayElement) -> QRectF:
        """Прямоугольник элемента на виджете."""
        center = self._video_to_widget(elem.x_percent, elem.y_percent)
        # Базовый размер элемента — пропорционален размеру видео
        base_size = min(self._display_rect.width(), self._display_rect.height()) * 0.15
        size = base_size * elem.scale / 100.0

        # Если есть кеш изображения, используем его пропорции
        px = gif_cache.get_frame(elem.file_path, int(self.current_time * 1000))
        if px and not px.isNull():
            aspect = px.width() / max(px.height(), 1)
            w = size * aspect
            h = size
        else:
            w = size
            h = size

        return QRectF(center.x() - w / 2, center.y() - h / 2, w, h)

    def _handle_rect(self, elem_rect: QRectF) -> QRectF:
        """Маркер масштабирования в правом нижнем углу."""
        s = 10
        return QRectF(elem_rect.right() - s, elem_rect.bottom() - s, s * 2, s * 2)

    def _element_at(self, pos: QPointF) -> Optional[str]:
        """Найти элемент под курсором."""
        if not self._project:
            return None
        t = self.current_time
        # Проходим в обратном порядке (верхний элемент — последний)
        for elem in reversed(self._project.elements):
            if elem.is_visible_at(t):
                if self._element_rect(elem).contains(pos):
                    return elem.id
        return None

    # --- Отрисовка ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Фон
        painter.fillRect(self.rect(), QColor("#11111b"))

        self._display_rect = self._compute_display_rect()

        # Кадр видео
        if self._frame_pixmap:
            painter.drawPixmap(self._display_rect.toRect(), self._frame_pixmap)
        else:
            # Нет видео — подсказка
            painter.setPen(QColor("#6c7086"))
            painter.setFont(QFont("Segoe UI", 16))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "Откройте видеофайл\n(Файл → Открыть видео)")

        # Оверлеи
        if self._overlay_mode and self._project:
            t = self.current_time
            for elem in self._project.elements:
                self._draw_overlay(painter, elem, t)

        painter.end()

    def _draw_overlay(self, painter: QPainter, elem: OverlayElement, t: float):
        """Рисует один оверлейный элемент."""
        if not elem.is_visible_at(t):
            # Показываем полупрозрачно, если выделен
            if elem.id == self._selected_id:
                opacity = 0.15
            else:
                return
        else:
            opacity = elem.opacity_at(t)

        rect = self._element_rect(elem)

        # Загружаем кадр из кеша
        if elem.file_path and os.path.exists(elem.file_path):
            gif_cache.load(elem.file_path)
            elapsed_ms = int((t - elem.start_time) * 1000)
            px = gif_cache.get_frame(elem.file_path, max(0, elapsed_ms))
        else:
            px = None

        painter.save()
        painter.setOpacity(opacity)

        if px and not px.isNull():
            painter.drawPixmap(rect.toRect(), px)
        else:
            # Заглушка — цветной прямоугольник с текстом
            painter.setBrush(QBrush(QColor(137, 180, 250, int(opacity * 180))))
            painter.setPen(QPen(QColor(205, 214, 244), 1))
            painter.drawRoundedRect(rect, 6, 6)
            painter.setFont(QFont("Segoe UI", 9))
            painter.setPen(QColor(205, 214, 244))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, elem.name)

        painter.restore()

        # Рамка выделения
        if elem.id == self._selected_id:
            painter.save()
            pen = QPen(QColor("#f9e2af"), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)

            # Маркер масштабирования
            handle = self._handle_rect(rect)
            painter.setBrush(QBrush(QColor("#f9e2af")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(handle)
            painter.restore()

    # --- События мыши ---
    def mousePressEvent(self, event):
        pos = QPointF(event.position())

        if event.button() == Qt.MouseButton.LeftButton:
            # Режим размещения?
            if self._placing:
                x_pct, y_pct = self._widget_to_video(pos)
                self.element_placed.emit(x_pct, y_pct)
                self._placing = False
                self.setCursor(Qt.CursorShape.ArrowCursor)
                return

            # Проверяем маркер масштабирования
            if self._selected_id and self._project:
                elem = self._project.get_element(self._selected_id)
                if elem:
                    handle = self._handle_rect(self._element_rect(elem))
                    if handle.contains(pos):
                        self._scaling_id = elem.id
                        center = self._element_rect(elem).center()
                        self._scale_start_dist = (pos - center).manhattanLength()
                        self._scale_start_val = elem.scale
                        return

            # Проверяем клик по элементу
            elem_id = self._element_at(pos)
            if elem_id:
                self._selected_id = elem_id
                self._dragging_id = elem_id
                elem = self._project.get_element(elem_id)
                if elem:
                    center = self._video_to_widget(elem.x_percent, elem.y_percent)
                    self._drag_offset = center - pos
                self.element_selected.emit(elem_id)
                self.update()
            else:
                self._selected_id = None
                self.update()

        elif event.button() == Qt.MouseButton.RightButton:
            # Контекстное меню
            elem_id = self._element_at(pos)
            if elem_id:
                self._show_context_menu(event.position(), elem_id)

    def mouseMoveEvent(self, event):
        pos = QPointF(event.position())

        # Перетаскивание
        if self._dragging_id and self._project:
            new_pos = pos + self._drag_offset
            x_pct, y_pct = self._widget_to_video(new_pos)
            elem = self._project.get_element(self._dragging_id)
            if elem:
                elem.x_percent = x_pct
                elem.y_percent = y_pct
                self.element_moved.emit(elem.id, x_pct, y_pct)
                self.update()
            return

        # Масштабирование
        if self._scaling_id and self._project:
            elem = self._project.get_element(self._scaling_id)
            if elem:
                center = self._element_rect(elem).center()
                dist = (pos - center).manhattanLength()
                if self._scale_start_dist > 0:
                    ratio = dist / self._scale_start_dist
                    new_scale = max(10, min(500, self._scale_start_val * ratio))
                    elem.scale = round(new_scale, 1)
                    self.element_scaled.emit(elem.id, elem.scale)
                    self.update()
            return

        # Курсор
        elem_id = self._element_at(pos)
        if elem_id:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        elif not self._placing:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging_id = None
            self._scaling_id = None

    def _show_context_menu(self, pos, elem_id: str):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background: #1e1e2e; color: #cdd6f4; border: 1px solid #313244; border-radius: 6px; }
            QMenu::item:selected { background: #45475a; }
        """)

        act_select = menu.addAction("✎ Выбрать / Редактировать")
        act_delete = menu.addAction("✕ Удалить элемент")

        action = menu.exec(self.mapToGlobal(pos.toPoint()))
        if action == act_select:
            self._selected_id = elem_id
            self.element_selected.emit(elem_id)
            self.update()
        elif action == act_delete:
            self.element_delete_requested.emit(elem_id)


# ---------------------------------------------------------------------------
# Панель управления воспроизведением (кнопки + слайдер + время)
# ---------------------------------------------------------------------------
class PlaybackControlBar(QFrame):
    """
    Горизонтальная полоса под превью:
      [⏮] [▶/⏸] [⏭]  ──────────  0:05.2 / 1:23.0
    """

    seek_requested = pyqtSignal(int)   # номер кадра

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        # Кнопки
        self.btn_back = QPushButton("⏮")
        self.btn_play = QPushButton("▶")
        self.btn_forward = QPushButton("⏭")
        for btn in (self.btn_back, self.btn_play, self.btn_forward):
            btn.setFixedSize(36, 36)
            btn.setStyleSheet("font-size: 16px;")
            layout.addWidget(btn)

        # Слайдер
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        layout.addWidget(self.slider, stretch=1)

        # Время
        self.time_label = QLabel("0:00.0 / 0:00.0")
        self.time_label.setObjectName("videoTimeLabel")
        self.time_label.setMinimumWidth(160)
        layout.addWidget(self.time_label)

        # Подключения
        self.slider.sliderMoved.connect(lambda val: self.seek_requested.emit(val))

    def set_duration(self, total_frames: int, fps: float):
        self.slider.setMaximum(max(0, total_frames - 1))
        self._fps = fps
        self._total_frames = total_frames

    def update_time(self, current_time: float, duration: float, frame: int):
        self.slider.blockSignals(True)
        self.slider.setValue(frame)
        self.slider.blockSignals(False)
        self.time_label.setText(
            f"{self._fmt(current_time)} / {self._fmt(duration)}"
        )

    def set_playing(self, playing: bool):
        self.btn_play.setText("⏸" if playing else "▶")

    @staticmethod
    def _fmt(t: float) -> str:
        minutes = int(t) // 60
        seconds = t - minutes * 60
        return f"{minutes}:{seconds:05.2f}"
