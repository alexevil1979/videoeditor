"""
sidebar.py — Левый сайдбар: библиотека элементов + свойства выбранного элемента.

Содержит:
  • ElementLibrary  — список доступных CTA-элементов (из папки assets/)
  • ElementProperties — панель редактирования свойств выбранного элемента
  • SidebarWidget — объединяет обе панели
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap, QImage, QColor, QPainter, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QDoubleSpinBox, QSlider, QGroupBox, QFormLayout,
    QFileDialog, QScrollArea, QFrame, QCheckBox, QSizePolicy, QSpinBox
)

from app.models import OverlayElement


# ---------------------------------------------------------------------------
# Библиотека элементов
# ---------------------------------------------------------------------------
class ElementLibrary(QGroupBox):
    """
    Показывает все файлы из папки assets/.
    По клику активируется режим размещения.
    """

    element_activated = pyqtSignal(str, str)  # (name, file_path)
    custom_file_loaded = pyqtSignal(str)       # file_path

    def __init__(self, assets_dir: str, parent=None):
        super().__init__("БИБЛИОТЕКА ЭЛЕМЕНТОВ", parent)
        self._assets_dir = assets_dir
        self.setObjectName("sectionTitle")

        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        self._list = QListWidget()
        self._list.setIconSize(QSize(48, 48))
        self._list.itemDoubleClicked.connect(self._on_item_activated)
        layout.addWidget(self._list)

        # Кнопка загрузки пользовательского файла
        btn_load = QPushButton("📁 Загрузить свой файл…")
        btn_load.clicked.connect(self._load_custom)
        layout.addWidget(btn_load)

        self._refresh()

    def _refresh(self):
        """Перечитывает файлы из assets/."""
        self._list.clear()
        assets = Path(self._assets_dir)
        if not assets.exists():
            assets.mkdir(parents=True, exist_ok=True)

        supported = {'.gif', '.png', '.jpg', '.jpeg', '.bmp', '.webp', '.apng', '.svg'}
        files = sorted(assets.iterdir())
        for f in files:
            if f.suffix.lower() in supported:
                item = QListWidgetItem(f.name)
                item.setData(Qt.ItemDataRole.UserRole, str(f))
                # Превью
                icon = self._make_icon(str(f))
                if icon:
                    item.setIcon(icon)
                item.setToolTip(f"Двойной клик — разместить\n{f.name}")
                self._list.addItem(item)

        # Заглушка «Текстовый CTA»
        item = QListWidgetItem("📝 Текст (CTA)")
        item.setData(Qt.ItemDataRole.UserRole, "__TEXT__")
        item.setToolTip("Текстовый призыв к действию")
        self._list.addItem(item)

    def _make_icon(self, path: str) -> Optional[QIcon]:
        """Создаёт иконку из файла."""
        pm = QPixmap(path)
        if pm.isNull():
            return None
        return QIcon(pm.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation))

    def _on_item_activated(self, item: QListWidgetItem):
        fp = item.data(Qt.ItemDataRole.UserRole)
        name = item.text()
        self.element_activated.emit(name, fp)

    def _load_custom(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл элемента",
            "", "Изображения и GIF (*.gif *.png *.jpg *.jpeg *.webp *.bmp *.apng);;Все файлы (*)"
        )
        if path:
            # Копируем в assets
            import shutil
            dest = Path(self._assets_dir) / Path(path).name
            if not dest.exists():
                shutil.copy2(path, dest)
            self._refresh()
            self.custom_file_loaded.emit(str(dest))

    def refresh_assets(self):
        self._refresh()


# ---------------------------------------------------------------------------
# Панель свойств выбранного элемента
# ---------------------------------------------------------------------------
class ElementProperties(QGroupBox):
    """
    Показывает/редактирует свойства выбранного OverlayElement.
    """

    property_changed = pyqtSignal()  # общий сигнал «что-то поменялось»

    def __init__(self, parent=None):
        super().__init__("СВОЙСТВА ЭЛЕМЕНТА", parent)
        self._element: Optional[OverlayElement] = None
        self._updating = False  # флаг, чтобы избежать рекурсии
        self.setMinimumWidth(280)

        form = QFormLayout(self)
        form.setSpacing(8)
        form.setContentsMargins(10, 20, 10, 10)

        # Название
        self.lbl_name = QLabel("—")
        self.lbl_name.setObjectName("sectionTitle")
        form.addRow("Элемент:", self.lbl_name)

        # Начало (сек)
        self.spin_start = QDoubleSpinBox()
        self.spin_start.setRange(0, 99999)
        self.spin_start.setDecimals(1)
        self.spin_start.setSuffix(" сек")
        self.spin_start.setSingleStep(0.5)
        self.spin_start.valueChanged.connect(self._on_change)
        form.addRow("Начало:", self.spin_start)

        # Длительность (сек) + галка «до конца»
        self.spin_duration = QDoubleSpinBox()
        self.spin_duration.setRange(0.1, 99999)
        self.spin_duration.setDecimals(1)
        self.spin_duration.setSuffix(" сек")
        self.spin_duration.setSingleStep(0.5)
        self.spin_duration.valueChanged.connect(self._on_change)

        from PyQt6.QtWidgets import QCheckBox
        self.chk_until_end = QCheckBox("До конца видео")
        self.chk_until_end.setToolTip("Элемент будет виден до конца видео")
        self.chk_until_end.stateChanged.connect(self._on_until_end_changed)

        dur_row = QHBoxLayout()
        dur_row.addWidget(self.spin_duration)
        dur_row.addWidget(self.chk_until_end)
        form.addRow("Длительность:", dur_row)

        # Прозрачность (%)
        self.slider_opacity = QSlider(Qt.Orientation.Horizontal)
        self.slider_opacity.setRange(0, 100)
        self.slider_opacity.setValue(100)
        self.slider_opacity.valueChanged.connect(self._on_change)
        self.lbl_opacity = QLabel("100%")
        opacity_row = QHBoxLayout()
        opacity_row.addWidget(self.slider_opacity)
        opacity_row.addWidget(self.lbl_opacity)
        form.addRow("Прозрачность:", opacity_row)

        # Масштаб (%)
        self.spin_scale = QDoubleSpinBox()
        self.spin_scale.setRange(10, 500)
        self.spin_scale.setDecimals(0)
        self.spin_scale.setSuffix(" %")
        self.spin_scale.setSingleStep(5)
        self.spin_scale.valueChanged.connect(self._on_change)
        form.addRow("Масштаб:", self.spin_scale)

        # Позиция X
        self.spin_x = QDoubleSpinBox()
        self.spin_x.setRange(0, 100)
        self.spin_x.setDecimals(1)
        self.spin_x.setSuffix(" %")
        self.spin_x.valueChanged.connect(self._on_change)
        form.addRow("Позиция X:", self.spin_x)

        # Позиция Y
        self.spin_y = QDoubleSpinBox()
        self.spin_y.setRange(0, 100)
        self.spin_y.setDecimals(1)
        self.spin_y.setSuffix(" %")
        self.spin_y.valueChanged.connect(self._on_change)
        form.addRow("Позиция Y:", self.spin_y)

        # Fade In
        self.spin_fade_in = QDoubleSpinBox()
        self.spin_fade_in.setRange(0, 10)
        self.spin_fade_in.setDecimals(1)
        self.spin_fade_in.setSuffix(" сек")
        self.spin_fade_in.valueChanged.connect(self._on_change)
        form.addRow("Fade In:", self.spin_fade_in)

        # Fade Out
        self.spin_fade_out = QDoubleSpinBox()
        self.spin_fade_out.setRange(0, 10)
        self.spin_fade_out.setDecimals(1)
        self.spin_fade_out.setSuffix(" сек")
        self.spin_fade_out.valueChanged.connect(self._on_change)
        form.addRow("Fade Out:", self.spin_fade_out)

        # --- Удаление фона ---
        from PyQt6.QtWidgets import QCheckBox
        self.chk_remove_bg = QCheckBox("Удалить фон")
        self.chk_remove_bg.setToolTip(
            "Автоматически убирает однотонный фон GIF/PNG\n"
            "по цвету угловых пикселей (chroma key)"
        )
        self.chk_remove_bg.stateChanged.connect(self._on_bg_change)
        form.addRow(self.chk_remove_bg)

        # Допуск удаления фона
        self.slider_bg_tolerance = QSlider(Qt.Orientation.Horizontal)
        self.slider_bg_tolerance.setRange(5, 150)
        self.slider_bg_tolerance.setValue(40)
        self.slider_bg_tolerance.setToolTip(
            "Допуск цвета: чем больше — тем больше оттенков фона удаляется"
        )
        self.slider_bg_tolerance.valueChanged.connect(self._on_bg_change)
        self.lbl_bg_tol = QLabel("40")
        bg_row = QHBoxLayout()
        bg_row.addWidget(self.slider_bg_tolerance)
        bg_row.addWidget(self.lbl_bg_tol)
        form.addRow("Допуск фона:", bg_row)

        # Скрыть, пока ничего не выбрано
        self._set_enabled(False)

    def set_element(self, elem: Optional[OverlayElement]):
        """Установить отображаемый элемент (или None для очистки)."""
        self._element = elem
        self._update_ui()

    def _update_ui(self):
        """Обновить значения виджетов из элемента."""
        self._updating = True
        if self._element:
            self._set_enabled(True)
            self.lbl_name.setText(self._element.name or "—")
            self.spin_start.setValue(self._element.start_time)
            self.spin_duration.setValue(self._element.duration)
            self.chk_until_end.setChecked(self._element.until_end)
            self.spin_duration.setEnabled(not self._element.until_end)
            self.slider_opacity.setValue(int(self._element.opacity))
            self.lbl_opacity.setText(f"{int(self._element.opacity)}%")
            self.spin_scale.setValue(self._element.scale)
            self.spin_x.setValue(self._element.x_percent)
            self.spin_y.setValue(self._element.y_percent)
            self.spin_fade_in.setValue(self._element.fade_in)
            self.spin_fade_out.setValue(self._element.fade_out)
            self.chk_remove_bg.setChecked(self._element.remove_bg)
            self.slider_bg_tolerance.setValue(self._element.bg_tolerance)
            self.lbl_bg_tol.setText(str(self._element.bg_tolerance))
        else:
            self._set_enabled(False)
            self.lbl_name.setText("—")
        self._updating = False

    def _set_enabled(self, on: bool):
        for w in (self.spin_start, self.spin_duration, self.slider_opacity,
                  self.spin_scale, self.spin_x, self.spin_y,
                  self.spin_fade_in, self.spin_fade_out,
                  self.chk_remove_bg, self.slider_bg_tolerance,
                  self.chk_until_end):
            w.setEnabled(on)
        # Если «до конца видео» — спинбокс длительности заблокирован
        if on and self._element and self._element.until_end:
            self.spin_duration.setEnabled(False)

    def set_video_duration(self, duration: float):
        """Сохраняет длительность видео для пересчёта 'до конца'."""
        self._video_duration = duration

    def _on_change(self):
        """Вызывается при изменении любого свойства пользователем."""
        if self._updating or not self._element:
            return
        self._element.start_time = self.spin_start.value()
        if not self._element.until_end:
            self._element.duration = self.spin_duration.value()
        self._element.opacity = self.slider_opacity.value()
        self.lbl_opacity.setText(f"{self.slider_opacity.value()}%")
        self._element.scale = self.spin_scale.value()
        self._element.x_percent = self.spin_x.value()
        self._element.y_percent = self.spin_y.value()
        self._element.fade_in = self.spin_fade_in.value()
        self._element.fade_out = self.spin_fade_out.value()

        # Пересчитываем длительность если «до конца»
        if self._element.until_end:
            self._recalc_until_end()

        self.property_changed.emit()

    def _on_until_end_changed(self):
        """Вызывается при переключении галки 'До конца видео'."""
        if self._updating or not self._element:
            return
        self._element.until_end = self.chk_until_end.isChecked()
        self.spin_duration.setEnabled(not self._element.until_end)
        if self._element.until_end:
            self._recalc_until_end()
        self.property_changed.emit()

    def _recalc_until_end(self):
        """Пересчитывает длительность = (конец видео) - (начало элемента)."""
        video_dur = getattr(self, '_video_duration', 0.0)
        if video_dur > 0:
            new_dur = max(0.1, video_dur - self._element.start_time)
            self._element.duration = round(new_dur, 1)
            self._updating = True
            self.spin_duration.setValue(self._element.duration)
            self._updating = False

    def _on_bg_change(self):
        """Вызывается при изменении настроек удаления фона."""
        if self._updating or not self._element:
            return
        self._element.remove_bg = self.chk_remove_bg.isChecked()
        self._element.bg_tolerance = self.slider_bg_tolerance.value()
        self.lbl_bg_tol.setText(str(self.slider_bg_tolerance.value()))
        # Сбрасываем кеш пиксмапов для этого файла, чтобы пересчитать
        from app.video_preview import gif_cache
        gif_cache.invalidate(self._element.file_path)
        self.property_changed.emit()

    def update_position(self, x: float, y: float):
        """Обновить позицию без эмиссии сигнала (при drag)."""
        if not self._element:
            return
        self._updating = True
        self.spin_x.setValue(x)
        self.spin_y.setValue(y)
        self._updating = False

    def update_scale(self, scale: float):
        """Обновить масштаб без эмиссии сигнала (при resize)."""
        if not self._element:
            return
        self._updating = True
        self.spin_scale.setValue(scale)
        self._updating = False


# ---------------------------------------------------------------------------
# Общий сайдбар
# ---------------------------------------------------------------------------
class SidebarWidget(QFrame):
    """Объединяет библиотеку и свойства в левый сайдбар."""

    element_activated = pyqtSignal(str, str)
    property_changed = pyqtSignal()

    def __init__(self, assets_dir: str, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        # Библиотека — прокручиваемая
        self.library = ElementLibrary(assets_dir)
        self.library.element_activated.connect(self.element_activated)

        # Свойства
        self.properties = ElementProperties()
        self.properties.property_changed.connect(self.property_changed)

        # Прокрутка
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.addWidget(self.library)
        container_layout.addWidget(self.properties)
        container_layout.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll)
