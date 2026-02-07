"""
styles.py — Таблица стилей (QSS) для Video CTA Overlay Editor.

Тёмная тема с акцентными цветами, современный вид.
"""

APP_STYLESHEET = """
/* ===== Основное окно ===== */
QMainWindow {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

/* ===== Меню ===== */
QMenuBar {
    background-color: #181825;
    color: #cdd6f4;
    border-bottom: 1px solid #313244;
    padding: 2px;
}
QMenuBar::item:selected {
    background-color: #45475a;
    border-radius: 4px;
}
QMenu {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item:selected {
    background-color: #45475a;
    border-radius: 4px;
}

/* ===== Кнопки ===== */
QPushButton {
    background-color: #45475a;
    color: #cdd6f4;
    border: 1px solid #585b70;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 13px;
    min-height: 28px;
}
QPushButton:hover {
    background-color: #585b70;
    border-color: #89b4fa;
}
QPushButton:pressed {
    background-color: #313244;
}
QPushButton:disabled {
    background-color: #313244;
    color: #6c7086;
    border-color: #45475a;
}
QPushButton#btnRender {
    background-color: #a6e3a1;
    color: #1e1e2e;
    font-weight: bold;
    font-size: 14px;
    border-color: #a6e3a1;
}
QPushButton#btnRender:hover {
    background-color: #94e2d5;
}
QPushButton#btnGitHub {
    background-color: #cba6f7;
    color: #1e1e2e;
    font-weight: bold;
    border-color: #cba6f7;
}
QPushButton#btnGitHub:hover {
    background-color: #b4befe;
}

/* ===== Ввод текста / спинбоксы ===== */
QLineEdit, QDoubleSpinBox, QSpinBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 5px;
    padding: 4px 8px;
    font-size: 13px;
}
QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {
    border-color: #89b4fa;
}

/* ===== Слайдеры ===== */
QSlider::groove:horizontal {
    background: #45475a;
    height: 6px;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #89b4fa;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    background: #b4befe;
}
QSlider::sub-page:horizontal {
    background: #89b4fa;
    border-radius: 3px;
}

/* ===== Таблица ===== */
QTableWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    gridline-color: #313244;
    border: 1px solid #313244;
    border-radius: 6px;
    font-size: 12px;
    selection-background-color: #45475a;
}
QHeaderView::section {
    background-color: #181825;
    color: #a6adc8;
    border: 1px solid #313244;
    padding: 5px 8px;
    font-weight: bold;
    font-size: 12px;
}
QTableWidget::item:selected {
    background-color: #45475a;
}

/* ===== Скроллбары ===== */
QScrollBar:vertical {
    background: #181825;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #585b70;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ===== Список (QListWidget) ===== */
QListWidget {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    outline: none;
    font-size: 13px;
}
QListWidget::item {
    padding: 6px 10px;
    border-radius: 4px;
    margin: 2px 4px;
}
QListWidget::item:hover {
    background-color: #313244;
}
QListWidget::item:selected {
    background-color: #45475a;
    color: #89b4fa;
}

/* ===== Метки ===== */
QLabel {
    color: #cdd6f4;
    font-size: 13px;
}
QLabel#sectionTitle {
    font-size: 14px;
    font-weight: bold;
    color: #89b4fa;
    padding: 4px 0;
}
QLabel#videoTimeLabel {
    font-size: 14px;
    font-family: monospace;
    color: #a6e3a1;
}

/* ===== Групповые рамки ===== */
QGroupBox {
    border: 1px solid #313244;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 18px;
    font-weight: bold;
    color: #89b4fa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}

/* ===== Подсказки ===== */
QToolTip {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px 8px;
}

/* ===== Прогресс-бар ===== */
QProgressBar {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    text-align: center;
    color: #cdd6f4;
    font-weight: bold;
    min-height: 22px;
}
QProgressBar::chunk {
    background-color: #a6e3a1;
    border-radius: 5px;
}

/* ===== Чекбоксы ===== */
QCheckBox {
    color: #cdd6f4;
    spacing: 8px;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #585b70;
    border-radius: 4px;
    background-color: #313244;
}
QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

/* ===== Разделители / фреймы ===== */
QFrame#sidebar {
    background-color: #181825;
    border-right: 1px solid #313244;
}
QFrame#bottomBar {
    background-color: #181825;
    border-top: 1px solid #313244;
}
"""
