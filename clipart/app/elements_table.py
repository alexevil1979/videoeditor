"""
elements_table.py — Таблица всех наложенных элементов (нижняя панель).

Показывает: #, Элемент, Начало (с), Длительность, Позиция, Действия (✎ ✕ ↑ ↓).
Подсвечивает строки элементов, видимых в текущий момент времени.
"""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QAbstractItemView, QFrame, QLabel
)

from app.models import OverlayElement


class ElementsTableWidget(QFrame):
    """
    Таблица со списком всех наложенных элементов.
    """

    element_selected = pyqtSignal(str)          # id
    element_edit = pyqtSignal(str)               # id
    element_delete = pyqtSignal(str)             # id
    element_move_up = pyqtSignal(str)            # id
    element_move_down = pyqtSignal(str)          # id

    COLUMNS = ["#", "Элемент", "Начало (с)", "Длительность", "Позиция", "Действия"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("bottomBar")
        self.setMinimumHeight(120)
        self.setMaximumHeight(220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        # Заголовок
        title = QLabel("Наложенные элементы")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        # Таблица
        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self._on_cell_clicked)

        layout.addWidget(self.table)

        self._elements: List[OverlayElement] = []

    def update_elements(self, elements: List[OverlayElement], current_time: float = 0.0):
        """Полностью перестроить таблицу из списка элементов."""
        self._elements = elements
        self.table.setRowCount(len(elements))

        for row, elem in enumerate(elements):
            visible = elem.is_visible_at(current_time)
            bg = QColor("#2a2d3a") if visible else QColor("#1e1e2e")

            # #
            item_num = QTableWidgetItem(str(row + 1))
            item_num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_num.setBackground(QBrush(bg))
            self.table.setItem(row, 0, item_num)

            # Элемент
            item_name = QTableWidgetItem(elem.name)
            item_name.setBackground(QBrush(bg))
            self.table.setItem(row, 1, item_name)

            # Начало
            item_start = QTableWidgetItem(f"{elem.start_time:.1f}")
            item_start.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_start.setBackground(QBrush(bg))
            self.table.setItem(row, 2, item_start)

            # Длительность
            item_dur = QTableWidgetItem(f"{elem.duration:.1f}")
            item_dur.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_dur.setBackground(QBrush(bg))
            self.table.setItem(row, 3, item_dur)

            # Позиция
            item_pos = QTableWidgetItem(f"{elem.x_percent:.0f}%, {elem.y_percent:.0f}%")
            item_pos.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_pos.setBackground(QBrush(bg))
            self.table.setItem(row, 4, item_pos)

            # Действия — виджет с кнопками
            actions_widget = self._make_actions_widget(elem.id)
            self.table.setCellWidget(row, 5, actions_widget)

    def _make_actions_widget(self, elem_id: str) -> QWidget:
        """Создаёт виджет с кнопками действий для строки таблицы."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)

        btn_edit = QPushButton("✎")
        btn_edit.setFixedSize(28, 28)
        btn_edit.setToolTip("Выбрать / Редактировать")
        btn_edit.clicked.connect(lambda: self.element_edit.emit(elem_id))

        btn_del = QPushButton("✕")
        btn_del.setFixedSize(28, 28)
        btn_del.setToolTip("Удалить")
        btn_del.setStyleSheet("color: #f38ba8;")
        btn_del.clicked.connect(lambda: self.element_delete.emit(elem_id))

        btn_up = QPushButton("↑")
        btn_up.setFixedSize(28, 28)
        btn_up.setToolTip("Переместить выше")
        btn_up.clicked.connect(lambda: self.element_move_up.emit(elem_id))

        btn_down = QPushButton("↓")
        btn_down.setFixedSize(28, 28)
        btn_down.setToolTip("Переместить ниже")
        btn_down.clicked.connect(lambda: self.element_move_down.emit(elem_id))

        layout.addWidget(btn_edit)
        layout.addWidget(btn_del)
        layout.addWidget(btn_up)
        layout.addWidget(btn_down)
        layout.addStretch()

        return widget

    def _on_cell_clicked(self, row, col):
        if 0 <= row < len(self._elements):
            self.element_selected.emit(self._elements[row].id)

    def highlight_row(self, elem_id: Optional[str]):
        """Подсвечивает строку выбранного элемента."""
        for row in range(self.table.rowCount()):
            if row < len(self._elements) and self._elements[row].id == elem_id:
                self.table.selectRow(row)
                return
        self.table.clearSelection()
