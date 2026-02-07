"""
main_window.py — Главное окно приложения Video CTA Overlay Editor.

Компонует все виджеты, связывает сигналы, реализует основную логику.
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
    QStatusBar, QMenuBar, QToolBar, QApplication
)

from app.models import Project, OverlayElement, UndoRedoManager
from app.video_preview import VideoPreviewWidget, PlaybackControlBar
from app.sidebar import SidebarWidget
from app.elements_table import ElementsTableWidget
from app.render_engine import RenderWorker, load_gpu_setting
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

        # Начальное состояние
        self._undo.save_state(self._project)
        self._update_all()

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
        """Строит центральную часть интерфейса."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Верхняя часть: сайдбар + превью
        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Сайдбар
        self._sidebar = SidebarWidget(self._assets_dir)
        top_splitter.addWidget(self._sidebar)

        # Правая часть: превью + контроли
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self._preview = VideoPreviewWidget()
        right_layout.addWidget(self._preview, stretch=1)

        self._playback_bar = PlaybackControlBar()
        right_layout.addWidget(self._playback_bar)

        top_splitter.addWidget(right_panel)

        # Пропорции сплиттера
        top_splitter.setSizes([320, 960])
        top_splitter.setStretchFactor(0, 0)
        top_splitter.setStretchFactor(1, 1)

        # Нижняя часть: таблица элементов
        self._elements_table = ElementsTableWidget()

        # Вертикальный сплиттер: превью | таблица
        v_splitter = QSplitter(Qt.Orientation.Vertical)
        v_splitter.addWidget(top_splitter)
        v_splitter.addWidget(self._elements_table)
        v_splitter.setSizes([500, 180])
        v_splitter.setStretchFactor(0, 1)
        v_splitter.setStretchFactor(1, 0)

        main_layout.addWidget(v_splitter, stretch=1)

    def _build_bottom_bar(self):
        """Панель действий внизу окна."""
        bar = QFrame()
        bar.setObjectName("bottomBar")
        bar.setFixedHeight(52)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

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

        btn_preview = QPushButton("👁 Предпросмотр")
        btn_preview.clicked.connect(self._toggle_preview)
        layout.addWidget(btn_preview)

        btn_render = QPushButton("🎬 РЕНДЕРИТЬ ВИДЕО")
        btn_render.setObjectName("btnRender")
        btn_render.clicked.connect(self._render_video)
        layout.addWidget(btn_render)

        btn_github = QPushButton("🐙 Выгрузить на GitHub")
        btn_github.setObjectName("btnGitHub")
        btn_github.clicked.connect(self._upload_to_github)
        layout.addWidget(btn_github)

        # Добавляем панель в главный layout
        self.centralWidget().layout().addWidget(bar)

    def _build_statusbar(self):
        """Строка состояния."""
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        self._statusbar.showMessage("Готово. Откройте видеофайл для начала работы.")

    # ===================================================================
    # Подключение сигналов
    # ===================================================================
    def _connect_signals(self):
        # --- Сайдбар ---
        self._sidebar.element_activated.connect(self._on_element_activated)
        self._sidebar.property_changed.connect(self._on_property_changed)

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
            lambda: self._preview.seek(max(0, self._preview._current_frame - int(self._preview.fps * 5)))
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
            # Передаём длительность видео в сайдбар для «До конца видео»
            self._sidebar.properties.set_video_duration(self._preview.duration)
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
        self._sidebar.properties.update_position(x, y)
        self._update_table()
        self._preview.update()

    # --- Масштабирование элемента ---
    def _on_element_scaled(self, elem_id: str, scale: float):
        self._sidebar.properties.update_scale(scale)
        self._update_table()

    # --- Выбор элемента ---
    def _on_element_selected(self, elem_id: str):
        self._selected_element_id = elem_id
        elem = self._project.get_element(elem_id)
        self._sidebar.properties.set_element(elem)
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
                self._sidebar.properties.set_element(None)
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
            self._sidebar.properties.set_element(None)
            self._update_all()
            self._statusbar.showMessage("Отменено.")

    def _do_redo(self):
        restored = self._undo.redo()
        if restored:
            self._project = restored
            self._preview.set_project(self._project)
            self._selected_element_id = None
            self._sidebar.properties.set_element(None)
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
                self._sidebar.properties.set_video_duration(self._preview.duration)

            self._selected_element_id = None
            self._sidebar.properties.set_element(None)
            self._update_all()
            self._statusbar.showMessage(f"Проект загружен: {path}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка",
                                f"Не удалось открыть проект:\n{e}")

    # --- Рендеринг ---
    def _render_video(self):
        if not self._project.video_path:
            QMessageBox.information(self, "Внимание",
                                    "Сначала откройте видеофайл.")
            return

        if not self._project.elements:
            QMessageBox.information(self, "Внимание",
                                    "Добавьте хотя бы один CTA-элемент.")
            return

        # Имя выходного файла
        base_name = Path(self._project.video_path).stem
        date_str = datetime.now().strftime("%Y-%m-%d")
        out_name = f"{base_name}_with_cta_{date_str}.mp4"

        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить видео",
            str(Path(self._outputs_dir) / out_name),
            "Видео MP4 (*.mp4)"
        )
        if not path:
            return

        # Останавливаем воспроизведение
        self._preview.pause()

        # Диалог прогресса
        dlg = RenderProgressDialog(self)

        # Читаем настройку GPU из конфигурации
        use_gpu = load_gpu_setting()

        self._render_worker = RenderWorker(self._project, path, use_gpu=use_gpu)
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

    def _on_render_finished(self, path: str, dlg: RenderProgressDialog):
        dlg.set_finished(path)
        self._statusbar.showMessage(f"Рендеринг завершён: {path}")
        self._last_rendered_path = path

    def _on_render_error(self, msg: str, dlg: RenderProgressDialog):
        dlg.set_error(msg)

    # --- Выгрузка на GitHub ---
    def _upload_to_github(self):
        if not hasattr(self, '_last_rendered_path') or not self._last_rendered_path:
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
