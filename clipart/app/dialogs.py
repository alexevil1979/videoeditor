"""
dialogs.py — Диалоговые окна приложения.

  • RenderProgressDialog — прогресс рендеринга
  • SettingsDialog       — настройки (GitHub-токен, путь к репо)
  • AboutDialog          — информация о программе
  • GitHubUploadDialog   — прогресс выгрузки на GitHub
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QProgressBar, QFileDialog, QTextEdit,
    QFormLayout, QGroupBox, QMessageBox
)

from app.github_upload import load_github_settings, save_github_settings


# ---------------------------------------------------------------------------
# Диалог прогресса рендеринга
# ---------------------------------------------------------------------------
class RenderProgressDialog(QDialog):
    """Показывает прогресс-бар во время рендеринга видео."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Рендеринг видео")
        self.setFixedSize(450, 180)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.label = QLabel("Подготовка к рендерингу...")
        self.label.setFont(QFont("Segoe UI", 12))
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Кнопка отмены
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_cancel = QPushButton("Отмена")
        btn_row.addWidget(self.btn_cancel)
        layout.addLayout(btn_row)

    def set_progress(self, value: int):
        self.progress_bar.setValue(value)
        if value < 50:
            self.label.setText("Создание оверлейных клипов...")
        elif value < 95:
            self.label.setText("Запись видеофайла...")
        else:
            self.label.setText("Завершение...")

    def set_finished(self, path: str):
        self.label.setText("✅ Рендеринг завершён!")
        self.status_label.setText(f"Сохранено: {path}")
        self.progress_bar.setValue(100)
        self.btn_cancel.setText("Закрыть")

    def set_error(self, msg: str):
        self.label.setText("❌ Ошибка рендеринга")
        self.status_label.setText(msg)
        self.btn_cancel.setText("Закрыть")


# ---------------------------------------------------------------------------
# Диалог настроек
# ---------------------------------------------------------------------------
class SettingsDialog(QDialog):
    """Настройки приложения: GitHub-токен, путь к репозиторию."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setFixedSize(520, 300)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Группа GitHub
        grp = QGroupBox("GitHub")
        grp_layout = QFormLayout(grp)
        grp_layout.setSpacing(10)

        self.edit_token = QLineEdit()
        self.edit_token.setEchoMode(QLineEdit.EchoMode.Password)
        self.edit_token.setPlaceholderText("ghp_xxxxxxxxxxxxxxxxxxxx")
        grp_layout.addRow("Токен GitHub:", self.edit_token)

        repo_row = QHBoxLayout()
        self.edit_repo = QLineEdit()
        self.edit_repo.setPlaceholderText("C:/Users/.../clipart")
        repo_row.addWidget(self.edit_repo)

        btn_browse = QPushButton("📁")
        btn_browse.setFixedSize(36, 36)
        btn_browse.clicked.connect(self._browse_repo)
        repo_row.addWidget(btn_browse)
        grp_layout.addRow("Путь к репозиторию:", repo_row)

        info = QLabel(
            "Репозиторий: https://github.com/alexevil1979/clipart\n"
            "Токен нужен для push. Создайте Personal Access Token\n"
            "с правами repo в настройках GitHub."
        )
        info.setStyleSheet("color: #6c7086; font-size: 11px;")
        info.setWordWrap(True)
        grp_layout.addRow(info)

        layout.addWidget(grp)
        layout.addStretch()

        # Кнопки
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_save = QPushButton("💾 Сохранить")
        btn_save.clicked.connect(self._save)
        btn_row.addWidget(btn_save)

        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        layout.addLayout(btn_row)

        # Загрузить текущие настройки
        self._load()

    def _load(self):
        settings = load_github_settings()
        self.edit_token.setText(settings.get("token", ""))
        self.edit_repo.setText(settings.get("repo_path", ""))

    def _save(self):
        save_github_settings(self.edit_token.text().strip(),
                             self.edit_repo.text().strip())
        self.accept()

    def _browse_repo(self):
        path = QFileDialog.getExistingDirectory(
            self, "Выберите папку репозитория"
        )
        if path:
            self.edit_repo.setText(path)


# ---------------------------------------------------------------------------
# О программе
# ---------------------------------------------------------------------------
class AboutDialog(QDialog):
    """Информация о приложении."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О программе")
        self.setFixedSize(420, 280)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("Video CTA Overlay Editor")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #89b4fa;")
        layout.addWidget(title)

        version = QLabel("Версия 1.0.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        desc = QLabel(
            "Приложение для наложения анимированных призывов\n"
            "к действию (CTA) на видео.\n\n"
            "Технологии: PyQt6, MoviePy, OpenCV, GitPython\n\n"
            "GitHub: https://github.com/alexevil1979/clipart"
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

        btn = QPushButton("Закрыть")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)


# ---------------------------------------------------------------------------
# Диалог прогресса загрузки на GitHub
# ---------------------------------------------------------------------------
class GitHubUploadDialog(QDialog):
    """Показывает лог загрузки на GitHub."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выгрузка на GitHub")
        self.setFixedSize(480, 300)

        layout = QVBoxLayout(self)

        self.label = QLabel("Загрузка на GitHub...")
        self.label.setFont(QFont("Segoe UI", 12))
        layout.addWidget(self.label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_close = QPushButton("Закрыть")
        self.btn_close.clicked.connect(self.accept)
        self.btn_close.setEnabled(False)
        btn_row.addWidget(self.btn_close)
        layout.addLayout(btn_row)

    def add_log(self, msg: str):
        self.log.append(msg)

    def set_finished(self, msg: str):
        self.label.setText("✅ Загрузка завершена!")
        self.log.append(f"\n{msg}")
        self.btn_close.setEnabled(True)

    def set_error(self, msg: str):
        self.label.setText("❌ Ошибка загрузки")
        self.log.append(f"\n❌ {msg}")
        self.btn_close.setEnabled(True)
