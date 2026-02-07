"""
main_window.py — Главное окно приложения Video CTA Overlay Editor.

Компонует все виджеты, связывает сигналы, реализует основную логику.
Макет: Библиотека (лево) | Видео (центр) | Свойства (право)

Новые функции:
  • Трёхколоночный layout: библиотека | видео | свойства
  • Сохранение/загрузка последнего пресета наложений (автозагрузка при старте)
  • Пакетная обработка всех видео в папке
  • Выбор префикса для выходных файлов
  • Сохранение в папку out/ рядом с исходным видео
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QFileDialog, QMessageBox, QFrame, QLabel,
    QStatusBar, QMenuBar, QToolBar, QApplication,
    QLineEdit, QCheckBox, QScrollArea
)

from app.models import (
    Project, OverlayElement, UndoRedoManager,
    save_last_preset, load_last_preset
)
from app.video_preview import VideoPreviewWidget, PlaybackControlBar
from app.sidebar import ElementLibrary, ElementProperties
from app.elements_table import ElementsTableWidget
from app.render_engine import (
    RenderWorker, BatchRenderWorker, load_gpu_setting,
    find_video_files, load_output_settings, save_output_settings
)
from app.github_upload import (
    GitHubUploadWorker, load_github_settings, GITHUB_REPO_URL
)
from app.dialogs import (
    RenderProgressDialog, SettingsDialog, AboutDialog, GitHubUploadDialog
)


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video CTA Overlay Editor")
        self.setMinimumSize(1000, 600)
        self.resize(1280, 720)

        # Данные
        self._project = Project()
        self._undo = UndoRedoManager(max_steps=30)
        self._selected_element_id: Optional[str] = None
        self._placing_asset_name: Optional[str] = None
        self._placing_asset_path: Optional[str] = None
        self._last_rendered_path: Optional[str] = None

        # Определяем пути
        self._app_dir = Path(__file__).resolve().parent.parent
        self._assets_dir = str(self._app_dir / "assets")
        self._outputs_dir = str(self._app_dir / "outputs")
        self._projects_dir = str(self._app_dir / "projects")

        # Создаём директории
        for d in (self._assets_dir, self._outputs_dir, self._projects_dir):
            Path(d).mkdir(parents=True, exist_ok=True)

        # Собираем UI
        self._build_menu()
        self._build_ui()
        self._build_bottom_bar()
        self._build_statusbar()
        self._connect_signals()

        # Загрузка настроек вывода (префикс, пакетная обработка)
        out_settings = load_output_settings()
        self._edit_prefix.setText(out_settings.get("prefix", "cta_"))
        self._chk_batch.setChecked(out_settings.get("batch", False))

        # Загрузка последнего пресета наложений
        self._load_last_preset()

        # Начальное состояние
        self._undo.save_state(self._project)
        self._update_all()

    def _load_last_preset(self):
        """Загружает последний использованный набор наложений при старте."""
        last_elements = load_last_preset()
        if last_elements:
            for elem in last_elements:
                self._project.add_element(elem)
            self._statusbar.showMessage(
                f"Загружен последний пресет: {len(last_elements)} элемент(ов). "
                "Откройте видеофайл для начала работы."
            )
        else:
            self._statusbar.showMessage(
                "Готово. Откройте видеофайл для начала работы."
            )

    # ===================================================================
    # Построение интерфейса
    # ===================================================================
    def _build_menu(self):
        """Создаёт меню приложения."""
        menubar = self.menuBar()

        # --- Файл ---
        file_menu = menubar.addMenu("Файл")

        act_open_video = QAction("Открыть видео…", self)
        act_open_video.setShortcut(QKeySequence("Ctrl+O"))
        act_open_video.triggered.connect(self._open_video)
        file_menu.addAction(act_open_video)

        file_menu.addSeparator()

        act_save_project = QAction("Сохранить проект…", self)
        act_save_project.setShortcut(QKeySequence("Ctrl+S"))
        act_save_project.triggered.connect(self._save_project)
        file_menu.addAction(act_save_project)

        act_open_project = QAction("Открыть проект…", self)
        act_open_project.setShortcut(QKeySequence("Ctrl+Shift+O"))
        act_open_project.triggered.connect(self._open_project)
        file_menu.addAction(act_open_project)

        file_menu.addSeparator()

        act_exit = QAction("Выход", self)
        act_exit.setShortcut(QKeySequence("Ctrl+Q"))
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        # --- Правка ---
        edit_menu = menubar.addMenu("Правка")

        self._act_undo = QAction("Отменить", self)
        self._act_undo.setShortcut(QKeySequence("Ctrl+Z"))
        self._act_undo.triggered.connect(self._do_undo)
        edit_menu.addAction(self._act_undo)

        self._act_redo = QAction("Повторить", self)
        self._act_redo.setShortcut(QKeySequence("Ctrl+Y"))
        self._act_redo.triggered.connect(self._do_redo)
        edit_menu.addAction(self._act_redo)

        # --- Вид ---
        view_menu = menubar.addMenu("Вид")

        self._act_overlay = QAction("Режим наложения", self)
        self._act_overlay.setCheckable(True)
        self._act_overlay.setChecked(True)
        self._act_overlay.triggered.connect(
            lambda checked: self._preview.set_overlay_mode(checked)
        )
        view_menu.addAction(self._act_overlay)

        # --- Настройки / О программе ---
        act_settings = QAction("⚙ Настройки", self)
        act_settings.triggered.connect(self._show_settings)
        menubar.addAction(act_settings)

        act_about = QAction("ℹ О программе", self)
        act_about.triggered.connect(self._show_about)
        menubar.addAction(act_about)

    def _build_ui(self):
        """Строит центральную часть: Библиотека (лево) | Видео (центр) | Свойства (право)."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === Трёхколоночный сплиттер ===
        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- ЛЕВАЯ КОЛОНКА: Библиотека элементов ---
        left_panel = QFrame()
        left_panel.setObjectName("sidebar")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(6, 6, 6, 6)
        left_layout.setSpacing(0)

        self._library = ElementLibrary(self._assets_dir)
        left_layout.addWidget(self._library)

        top_splitter.addWidget(left_panel)

        # --- ЦЕНТРАЛЬНАЯ КОЛОНКА: Видео превью ---
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        self._preview = VideoPreviewWidget()
        center_layout.addWidget(self._preview, stretch=1)

        self._playback_bar = PlaybackControlBar()
        center_layout.addWidget(self._playback_bar)

        top_splitter.addWidget(center_panel)

        # --- ПРАВАЯ КОЛОНКА: Свойства элемента ---
        right_panel = QFrame()
        right_panel.setObjectName("sidebar")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(6, 6, 6, 6)
        right_layout.setSpacing(0)

        # Прокрутка для свойств
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self._properties = ElementProperties()
        container_layout.addWidget(self._properties)
        container_layout.addStretch()

        scroll.setWidget(container)
        right_layout.addWidget(scroll)

        top_splitter.addWidget(right_panel)

        # Пропорции сплиттера: библиотека 240 | видео 700 | свойства 300
        top_splitter.setSizes([240, 700, 300])
        top_splitter.setStretchFactor(0, 0)   # библиотека фиксированная
        top_splitter.setStretchFactor(1, 1)   # видео растягивается
        top_splitter.setStretchFactor(2, 0)   # свойства фиксированные

        # --- Нижняя часть: таблица элементов ---
        self._elements_table = ElementsTableWidget()

        # Вертикальный сплиттер: (библ|видео|свойства) | таблица
        v_splitter = QSplitter(Qt.Orientation.Vertical)
        v_splitter.addWidget(top_splitter)
        v_splitter.addWidget(self._elements_table)
        v_splitter.setSizes([500, 180])
        v_splitter.setStretchFactor(0, 1)
        v_splitter.setStretchFactor(1, 0)

        main_layout.addWidget(v_splitter, stretch=1)

    def _build_bottom_bar(self):
        """Панель действий внизу окна (с настройками вывода)."""
        bar = QFrame()
        bar.setObjectName("bottomBar")
        bar.setFixedHeight(52)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        # --- Кнопки файлов ---
        btn_open = QPushButton("📂 Открыть видео")
        btn_open.clicked.connect(self._open_video)
        layout.addWidget(btn_open)

        btn_save = QPushButton("💾 Сохранить проект")
        btn_save.clicked.connect(self._save_project)
        layout.addWidget(btn_save)

        btn_load = QPushButton("📁 Открыть проект")
        btn_load.clicked.connect(self._open_project)
        layout.addWidget(btn_load)

        layout.addStretch()

        # --- Настройки вывода ---
        lbl_prefix = QLabel("Префикс:")
        lbl_prefix.setStyleSheet("color: #cdd6f4; font-size: 12px;")
        layout.addWidget(lbl_prefix)

        self._edit_prefix = QLineEdit("cta_")
        self._edit_prefix.setFixedWidth(80)
        self._edit_prefix.setToolTip(
            "Префикс для выходных файлов.\n"
            "Результат: {префикс}{имя_видео}.mp4\n"
            "Файлы сохраняются в папку out/ рядом с оригиналом."
        )
        layout.addWidget(self._edit_prefix)

        self._chk_batch = QCheckBox("Все файлы в папке")
        self._chk_batch.setToolTip(
            "Обработать все видеофайлы в папке выбранного видео.\n"
            "Каждый файл получит те же наложения.\n"
            "Результаты → {папка_видео}/out/"
        )
        layout.addWidget(self._chk_batch)

        layout.addStretch()

        # --- Кнопки действий ---
        btn_preview = QPushButton("👁 Предпросмотр")
        btn_preview.clicked.connect(self._toggle_preview)
        layout.addWidget(btn_preview)

        btn_render = QPushButton("🎬 РЕНДЕРИТЬ")
        btn_render.setObjectName("btnRender")
        btn_render.clicked.connect(self._render_video)
        layout.addWidget(btn_render)

        btn_github = QPushButton("🐙 GitHub")
        btn_github.setObjectName("btnGitHub")
        btn_github.clicked.connect(self._upload_to_github)
        layout.addWidget(btn_github)

        # Добавляем панель в главный layout
        self.centralWidget().layout().addWidget(bar)

    def _build_statusbar(self):
        """Строка состояния."""
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)

    # ===================================================================
    # Подключение сигналов
    # ===================================================================
    def _connect_signals(self):
        # --- Библиотека (левая панель) ---
        self._library.element_activated.connect(self._on_element_activated)

        # --- Свойства (правая панель) ---
        self._properties.property_changed.connect(self._on_property_changed)

        # --- Превью ---
        self._preview.element_placed.connect(self._on_element_placed)
        self._preview.element_moved.connect(self._on_element_moved)
        self._preview.element_scaled.connect(self._on_element_scaled)
        self._preview.element_selected.connect(self._on_element_selected)
        self._preview.element_delete_requested.connect(self._delete_element)
        self._preview.time_changed.connect(self._on_time_changed)

        # --- Playback ---
        self._playback_bar.btn_play.clicked.connect(self._preview.toggle_play)
        self._playback_bar.btn_back.clicked.connect(
            lambda: self._preview.seek(
                max(0, self._preview._current_frame - int(self._preview.fps * 5))
            )
        )
        self._playback_bar.btn_forward.clicked.connect(
            lambda: self._preview.seek(
                min(self._preview.total_frames - 1,
                    self._preview._current_frame + int(self._preview.fps * 5))
            )
        )
        self._playback_bar.seek_requested.connect(self._preview.seek)

        # Обновление кнопки play/pause при изменении состояния
        self._preview.time_changed.connect(self._on_time_tick)

        # --- Таблица ---
        self._elements_table.element_selected.connect(self._on_element_selected)
        self._elements_table.element_edit.connect(self._on_element_selected)
        self._elements_table.element_delete.connect(self._delete_element)
        self._elements_table.element_move_up.connect(self._move_element_up)
        self._elements_table.element_move_down.connect(self._move_element_down)

    # ===================================================================
    # Обработчики событий
    # ===================================================================

    # --- Открытие видео ---
    def _open_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите видеофайл",
            "",
            "Видеофайлы (*.mp4 *.avi *.mkv *.mov *.wmv *.webm);;Все файлы (*)"
        )
        if not path:
            return

        if self._preview.open_video(path):
            self._project.video_path = path
            self._playback_bar.set_duration(
                self._preview.total_frames, self._preview.fps
            )
            self._preview.set_project(self._project)
            # Передаём длительность видео в свойства для «До конца видео»
            self._properties.set_video_duration(self._preview.duration)
            self._undo.save_state(self._project)
            self._statusbar.showMessage(
                f"Видео загружено: {Path(path).name} "
                f"({self._preview.video_size[0]}×{self._preview.video_size[1]}, "
                f"{self._preview.fps:.1f} fps, "
                f"{self._preview.duration:.1f} сек)"
            )
        else:
            QMessageBox.warning(self, "Ошибка",
                                f"Не удалось открыть видеофайл:\n{path}")

    # --- Активация элемента из библиотеки ---
    def _on_element_activated(self, name: str, file_path: str):
        """Пользователь выбрал элемент в библиотеке — включаем режим размещения."""
        if not self._project.video_path:
            QMessageBox.information(self, "Внимание",
                                    "Сначала откройте видеофайл.")
            return

        self._placing_asset_name = name
        self._placing_asset_path = file_path
        self._preview.set_placing_mode(True)
        self._statusbar.showMessage(
            f"Кликните по видео, чтобы разместить «{name}»"
        )

    # --- Размещение элемента ---
    def _on_element_placed(self, x_pct: float, y_pct: float):
        """Клик по превью в режиме размещения."""
        if not self._placing_asset_name:
            return

        elem = OverlayElement(
            name=self._placing_asset_name,
            file_path=self._placing_asset_path if self._placing_asset_path != "__TEXT__" else "",
            start_time=self._preview.current_time,
            duration=3.0,
            x_percent=x_pct,
            y_percent=y_pct,
            scale=100.0,
            opacity=100.0,
        )

        self._project.add_element(elem)
        self._undo.save_state(self._project)
        self._selected_element_id = elem.id
        self._placing_asset_name = None
        self._placing_asset_path = None

        self._update_all()
        self._statusbar.showMessage(f"Элемент «{elem.name}» добавлен.")

    # --- Перемещение элемента ---
    def _on_element_moved(self, elem_id: str, x: float, y: float):
        self._properties.update_position(x, y)
        self._update_table()
        self._preview.update()

    # --- Масштабирование элемента ---
    def _on_element_scaled(self, elem_id: str, scale: float):
        self._properties.update_scale(scale)
        self._update_table()

    # --- Выбор элемента ---
    def _on_element_selected(self, elem_id: str):
        self._selected_element_id = elem_id
        elem = self._project.get_element(elem_id)
        self._properties.set_element(elem)
        self._preview.set_selected(elem_id)
        self._elements_table.highlight_row(elem_id)

    # --- Изменение свойств ---
    def _on_property_changed(self):
        self._undo.save_state(self._project)
        self._update_table()
        self._preview.update()

    # --- Удаление элемента ---
    def _delete_element(self, elem_id: str):
        elem = self._project.remove_element(elem_id)
        if elem:
            self._undo.save_state(self._project)
            if self._selected_element_id == elem_id:
                self._selected_element_id = None
                self._properties.set_element(None)
                self._preview.set_selected(None)
            self._update_all()
            self._statusbar.showMessage(f"Элемент «{elem.name}» удалён.")

    # --- Перемещение вверх/вниз ---
    def _move_element_up(self, elem_id: str):
        if self._project.move_element_up(elem_id):
            self._undo.save_state(self._project)
            self._update_table()

    def _move_element_down(self, elem_id: str):
        if self._project.move_element_down(elem_id):
            self._undo.save_state(self._project)
            self._update_table()

    # --- Undo / Redo ---
    def _do_undo(self):
        restored = self._undo.undo()
        if restored:
            # Сохраняем путь к видео, если он не изменился
            old_video = self._project.video_path
            self._project = restored
            if not self._project.video_path and old_video:
                self._project.video_path = old_video
            self._preview.set_project(self._project)
            self._selected_element_id = None
            self._properties.set_element(None)
            self._update_all()
            self._statusbar.showMessage("Отменено.")

    def _do_redo(self):
        restored = self._undo.redo()
        if restored:
            self._project = restored
            self._preview.set_project(self._project)
            self._selected_element_id = None
            self._properties.set_element(None)
            self._update_all()
            self._statusbar.showMessage("Повторено.")

    # --- Таймлайн ---
    def _on_time_changed(self, t: float):
        self._playback_bar.update_time(
            t, self._preview.duration, self._preview._current_frame
        )
        # Обновляем подсветку в таблице
        self._elements_table.update_elements(
            self._project.elements, t
        )
        if self._selected_element_id:
            self._elements_table.highlight_row(self._selected_element_id)

    def _on_time_tick(self, t: float):
        self._playback_bar.set_playing(self._preview.is_playing)

    # --- Предпросмотр ---
    def _toggle_preview(self):
        self._preview.toggle_play()

    # --- Сохранение / загрузка проекта ---
    def _save_project(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить проект",
            str(Path(self._projects_dir) / "project.json"),
            "Файлы проекта (*.json)"
        )
        if path:
            try:
                self._project.save(path)
                # Также сохраняем как последний пресет
                save_last_preset(self._project.elements)
                self._statusbar.showMessage(f"Проект сохранён: {path}")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка",
                                    f"Не удалось сохранить проект:\n{e}")

    def _open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть проект",
            self._projects_dir,
            "Файлы проекта (*.json)"
        )
        if not path:
            return
        try:
            self._project = Project.load(path)
            self._undo.clear()
            self._undo.save_state(self._project)
            self._preview.set_project(self._project)

            # Открываем видео из проекта
            if self._project.video_path and os.path.exists(self._project.video_path):
                self._preview.open_video(self._project.video_path)
                self._playback_bar.set_duration(
                    self._preview.total_frames, self._preview.fps
                )
                self._properties.set_video_duration(self._preview.duration)

            self._selected_element_id = None
            self._properties.set_element(None)
            self._update_all()
            self._statusbar.showMessage(f"Проект загружен: {path}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка",
                                f"Не удалось открыть проект:\n{e}")

    # ===================================================================
    # Рендеринг
    # ===================================================================
    def _render_video(self):
        """Запуск рендеринга (одиночного или пакетного)."""
        if not self._project.video_path:
            QMessageBox.information(self, "Внимание",
                                    "Сначала откройте видеофайл.")
            return

        if not self._project.elements:
            QMessageBox.information(self, "Внимание",
                                    "Добавьте хотя бы один CTA-элемент.")
            return

        # Сохраняем пресет наложений
        save_last_preset(self._project.elements)

        # Настройки вывода
        prefix = self._edit_prefix.text().strip() or "cta_"
        batch = self._chk_batch.isChecked()
        use_gpu = load_gpu_setting()

        # Папка вывода: {папка_видео}/out/
        video_dir = str(Path(self._project.video_path).parent)
        out_dir = str(Path(video_dir) / "out")

        # Останавливаем воспроизведение
        self._preview.pause()

        if batch:
            self._render_batch(video_dir, out_dir, prefix, use_gpu)
        else:
            self._render_single(out_dir, prefix, use_gpu)

    def _render_single(self, out_dir: str, prefix: str, use_gpu: bool):
        """Рендеринг одного файла → {out_dir}/{prefix}{name}.mp4"""
        out_name = f"{prefix}{Path(self._project.video_path).stem}.mp4"
        out_path = str(Path(out_dir) / out_name)

        dlg = RenderProgressDialog(self)
        dlg.add_log(f"Вывод: {out_path}")

        self._render_worker = RenderWorker(
            self._project, out_path, use_gpu=use_gpu
        )
        self._render_worker.progress.connect(dlg.set_progress)
        self._render_worker.log.connect(dlg.add_log)
        self._render_worker.finished_ok.connect(
            lambda p: self._on_render_finished(p, dlg)
        )
        self._render_worker.error.connect(
            lambda msg: self._on_render_error(msg, dlg)
        )
        dlg.btn_cancel.clicked.connect(lambda: dlg.close())

        self._render_worker.start()
        dlg.exec()

    def _render_batch(self, video_dir: str, out_dir: str,
                      prefix: str, use_gpu: bool):
        """Пакетный рендеринг всех видео в папке → {out_dir}/{prefix}{name}.mp4"""
        video_files = find_video_files(video_dir)
        if not video_files:
            QMessageBox.information(
                self, "Внимание",
                "Видеофайлы в папке не найдены."
            )
            return

        # Подтверждение
        answer = QMessageBox.question(
            self, "Пакетная обработка",
            f"Найдено {len(video_files)} видеофайл(ов) в папке:\n"
            f"{video_dir}\n\n"
            f"Результаты будут сохранены в:\n{out_dir}\n\n"
            f"Префикс: «{prefix}»\n\n"
            f"Начать обработку?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        elements_data = [e.to_dict() for e in self._project.elements]

        dlg = RenderProgressDialog(self)
        dlg.label.setText(f"Пакетная обработка: {len(video_files)} файл(ов)")

        self._render_worker = BatchRenderWorker(
            elements_data, video_files, out_dir, prefix, use_gpu
        )
        self._render_worker.progress.connect(dlg.set_progress)
        self._render_worker.log.connect(dlg.add_log)
        self._render_worker.finished_ok.connect(
            lambda msg: self._on_batch_finished(msg, dlg)
        )
        self._render_worker.error.connect(
            lambda msg: self._on_render_error(msg, dlg)
        )
        dlg.btn_cancel.clicked.connect(lambda: dlg.close())

        self._render_worker.start()
        dlg.exec()

    def _on_render_finished(self, path: str, dlg: RenderProgressDialog):
        dlg.set_finished(path)
        self._statusbar.showMessage(f"Рендеринг завершён: {path}")
        self._last_rendered_path = path

    def _on_batch_finished(self, msg: str, dlg: RenderProgressDialog):
        """Пакетная обработка завершена."""
        dlg.label.setText("✅ Пакетная обработка завершена!")
        dlg.status_label.setText(msg)
        dlg.progress_bar.setValue(100)
        dlg.btn_cancel.setText("Закрыть")
        self._statusbar.showMessage(msg)

    def _on_render_error(self, msg: str, dlg: RenderProgressDialog):
        dlg.set_error(msg)

    # --- Выгрузка на GitHub ---
    def _upload_to_github(self):
        if not self._last_rendered_path:
            QMessageBox.information(
                self, "Внимание",
                "Сначала выполните рендеринг видео."
            )
            return

        if not os.path.exists(self._last_rendered_path):
            QMessageBox.warning(
                self, "Ошибка",
                f"Файл не найден: {self._last_rendered_path}"
            )
            return

        settings = load_github_settings()
        token = settings.get("token", "")
        repo_path = settings.get("repo_path", "")

        if not repo_path:
            answer = QMessageBox.question(
                self, "Настройки GitHub",
                "Путь к репозиторию не указан.\n"
                "Открыть настройки?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if answer == QMessageBox.StandardButton.Yes:
                self._show_settings()
                settings = load_github_settings()
                token = settings.get("token", "")
                repo_path = settings.get("repo_path", "")
            if not repo_path:
                return

        # Диалог прогресса
        dlg = GitHubUploadDialog(self)

        worker = GitHubUploadWorker(
            self._last_rendered_path, repo_path, token
        )
        worker.progress.connect(dlg.add_log)
        worker.finished_ok.connect(dlg.set_finished)
        worker.error.connect(dlg.set_error)

        self._github_worker = worker  # предотвращаем GC
        worker.start()
        dlg.exec()

    # --- Настройки ---
    def _show_settings(self):
        SettingsDialog(self).exec()

    def _show_about(self):
        AboutDialog(self).exec()

    # ===================================================================
    # Обновление UI
    # ===================================================================
    def _update_all(self):
        """Полное обновление всех виджетов."""
        self._update_table()
        self._preview.update()
        self._act_undo.setEnabled(self._undo.can_undo)
        self._act_redo.setEnabled(self._undo.can_redo)

    def _update_table(self):
        """Обновить таблицу элементов."""
        self._elements_table.update_elements(
            self._project.elements, self._preview.current_time
        )
        if self._selected_element_id:
            self._elements_table.highlight_row(self._selected_element_id)

    # --- Закрытие ---
    def closeEvent(self, event):
        # Сохраняем настройки вывода
        save_output_settings(
            self._edit_prefix.text().strip() or "cta_",
            self._chk_batch.isChecked()
        )

        # Сохраняем пресет наложений (если есть элементы)
        if self._project.elements:
            save_last_preset(self._project.elements)

        if self._project.elements:
            answer = QMessageBox.question(
                self, "Выход",
                "Вы уверены, что хотите выйти?\n"
                "Несохранённые изменения будут потеряны.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        event.accept()
