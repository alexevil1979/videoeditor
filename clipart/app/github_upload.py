"""
github_upload.py — Автоматическая выгрузка готового видео на GitHub.

Использует GitPython для:
  • git add → commit → push
  • Если репо не клонировано — предлагает клонировать
  • Токен хранится в настройках (QSettings)
"""

from __future__ import annotations

import os
import shutil
import traceback
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal, QSettings

# GitPython
try:
    import git
    from git import Repo, InvalidGitRepositoryError, GitCommandNotFound
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False


GITHUB_REPO_URL = "https://github.com/alexevil1979/clipart"
DEFAULT_BRANCH = "main"


class GitHubUploadWorker(QThread):
    """
    Поток для выгрузки файла на GitHub.
    Сигналы:
      progress(str) — статусные сообщения
      finished_ok(str) — сообщение об успехе
      error(str) — сообщение об ошибке
    """

    progress = pyqtSignal(str)
    finished_ok = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, video_path: str, repo_path: str,
                 github_token: str = "", parent=None):
        super().__init__(parent)
        self._video_path = video_path
        self._repo_path = repo_path
        self._token = github_token

    def run(self):
        if not GIT_AVAILABLE:
            self.error.emit("GitPython не установлен. Установите: pip install gitpython")
            return

        try:
            self._upload()
        except Exception as e:
            self.error.emit(f"Ошибка загрузки на GitHub:\n{traceback.format_exc()}")

    def _upload(self):
        repo_path = Path(self._repo_path)

        # Проверяем, есть ли репозиторий
        if not repo_path.exists() or not (repo_path / ".git").exists():
            self.progress.emit("Клонирование репозитория...")
            clone_url = self._get_auth_url()
            try:
                Repo.clone_from(clone_url, str(repo_path))
            except Exception as e:
                self.error.emit(
                    f"Не удалось клонировать репозиторий:\n{e}\n\n"
                    f"Убедитесь, что указан правильный путь и токен GitHub."
                )
                return

        self.progress.emit("Открытие репозитория...")
        try:
            repo = Repo(str(repo_path))
        except Exception as e:
            self.error.emit(f"Не удалось открыть репозиторий:\n{e}")
            return

        # Создаём папку outputs/ если нет
        outputs_dir = repo_path / "outputs"
        outputs_dir.mkdir(exist_ok=True)

        # Копируем файл
        video_name = Path(self._video_path).name
        dest = outputs_dir / video_name
        self.progress.emit(f"Копирование {video_name}...")
        shutil.copy2(self._video_path, dest)

        # Git add
        self.progress.emit("git add...")
        relative_path = f"outputs/{video_name}"
        repo.index.add([relative_path])

        # Git commit
        commit_msg = f"Added CTA overlay video: {video_name}"
        self.progress.emit(f"git commit: {commit_msg}")
        repo.index.commit(commit_msg)

        # Git push
        self.progress.emit("git push...")
        try:
            origin = repo.remote("origin")

            # Обновляем URL с токеном если есть
            if self._token:
                auth_url = self._get_auth_url()
                origin.set_url(auth_url)

            origin.push(DEFAULT_BRANCH)
        except Exception as e:
            self.error.emit(
                f"Не удалось выполнить git push:\n{e}\n\n"
                f"Проверьте токен GitHub и разрешения."
            )
            return

        self.finished_ok.emit(f"Видео успешно загружено на GitHub:\n{relative_path}")

    def _get_auth_url(self) -> str:
        """Формирует URL с токеном аутентификации."""
        if self._token:
            # https://<token>@github.com/user/repo.git
            return GITHUB_REPO_URL.replace(
                "https://", f"https://{self._token}@"
            ) + ".git"
        return GITHUB_REPO_URL + ".git"


# ---------------------------------------------------------------------------
# Вспомогательные функции для настроек
# ---------------------------------------------------------------------------
def load_github_settings() -> dict:
    """Загружает настройки GitHub из QSettings."""
    settings = QSettings("VideoCTAEditor", "VideoCTAEditor")
    return {
        "token": settings.value("github/token", ""),
        "repo_path": settings.value("github/repo_path", ""),
    }


def save_github_settings(token: str, repo_path: str) -> None:
    """Сохраняет настройки GitHub в QSettings."""
    settings = QSettings("VideoCTAEditor", "VideoCTAEditor")
    settings.setValue("github/token", token)
    settings.setValue("github/repo_path", repo_path)
