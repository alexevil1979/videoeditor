#!/usr/bin/env python3
"""
Video CTA Overlay Editor — главная точка входа.

Десктопное приложение для наложения анимированных призывов к действию
(CTA) на видео. Использует PyQt6 для интерфейса, MoviePy для рендеринга,
OpenCV для превью, GitPython для выгрузки на GitHub.

Запуск:
    python main.py
"""

import sys
import os

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.styles import APP_STYLESHEET
from app.main_window import MainWindow


def main():
    """Точка входа в приложение."""

    # Включаем высокий DPI
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("Video CTA Overlay Editor")
    app.setOrganizationName("VideoCTAEditor")
    app.setApplicationVersion("1.0.0")

    # Шрифт по умолчанию
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Применяем стиль
    app.setStyleSheet(APP_STYLESHEET)

    # Создаём и показываем главное окно
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
