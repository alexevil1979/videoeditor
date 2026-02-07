"""
models.py — Модели данных приложения Video CTA Overlay Editor.

Содержит:
  - OverlayElement: данные одного наложенного элемента (позиция, время, масштаб и т.д.)
  - Project: набор элементов + путь к видео, сериализация в JSON
  - UndoRedoManager: простая система отмены/повтора (до 30 шагов)
"""

from __future__ import annotations

import copy
import json
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Модель одного наложенного элемента
# ---------------------------------------------------------------------------
@dataclass
class OverlayElement:
    """Один CTA-элемент, наложенный на видео."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Отображаемое имя и путь к файлу ассета (gif/png/mp4)
    name: str = ""
    file_path: str = ""

    # Временные параметры (в секундах)
    start_time: float = 0.0
    duration: float = 3.0
    until_end: bool = False       # если True — длительность = до конца видео

    # Позиция (в процентах от размера видео, 0‑100)
    x_percent: float = 50.0
    y_percent: float = 50.0

    # Масштаб (%) и прозрачность (0‑100%)
    scale: float = 100.0
    opacity: float = 100.0

    # Эффекты плавного появления / исчезновения (секунды)
    fade_in: float = 0.0
    fade_out: float = 0.0

    # Удаление фона (chroma key по цвету углов)
    remove_bg: bool = False       # включить удаление фона
    bg_tolerance: int = 40        # допуск цвета (0‑255), чем больше — тем больше убирается

    # --- Вспомогательные свойства ---
    @property
    def end_time(self) -> float:
        """Время исчезновения элемента."""
        return self.start_time + self.duration

    def is_visible_at(self, t: float) -> bool:
        """Возвращает True, если элемент виден в момент времени *t* (секунды)."""
        return self.start_time <= t < self.end_time

    def opacity_at(self, t: float) -> float:
        """Возвращает реальную прозрачность с учётом fade in/out (0‑1)."""
        if not self.is_visible_at(t):
            return 0.0

        base = self.opacity / 100.0
        elapsed = t - self.start_time
        remaining = self.end_time - t

        # Fade in
        if self.fade_in > 0 and elapsed < self.fade_in:
            base *= elapsed / self.fade_in

        # Fade out
        if self.fade_out > 0 and remaining < self.fade_out:
            base *= remaining / self.fade_out

        return max(0.0, min(1.0, base))

    def to_dict(self) -> dict:
        """Сериализация в словарь (для JSON)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "OverlayElement":
        """Десериализация из словаря."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------------
# Проект: видео + все наложенные элементы
# ---------------------------------------------------------------------------
@dataclass
class Project:
    """Набор данных проекта."""

    video_path: str = ""
    elements: List[OverlayElement] = field(default_factory=list)
    name: str = "Новый проект"

    # --- Управление элементами ---
    def add_element(self, elem: OverlayElement) -> None:
        self.elements.append(elem)

    def remove_element(self, elem_id: str) -> Optional[OverlayElement]:
        for i, e in enumerate(self.elements):
            if e.id == elem_id:
                return self.elements.pop(i)
        return None

    def get_element(self, elem_id: str) -> Optional[OverlayElement]:
        for e in self.elements:
            if e.id == elem_id:
                return e
        return None

    def move_element_up(self, elem_id: str) -> bool:
        """Сдвигает элемент на одну позицию вверх в списке."""
        for i, e in enumerate(self.elements):
            if e.id == elem_id and i > 0:
                self.elements[i], self.elements[i - 1] = self.elements[i - 1], self.elements[i]
                return True
        return False

    def move_element_down(self, elem_id: str) -> bool:
        """Сдвигает элемент на одну позицию вниз в списке."""
        for i, e in enumerate(self.elements):
            if e.id == elem_id and i < len(self.elements) - 1:
                self.elements[i], self.elements[i + 1] = self.elements[i + 1], self.elements[i]
                return True
        return False

    def visible_elements_at(self, t: float) -> List[OverlayElement]:
        """Возвращает элементы, видимые в момент времени *t*."""
        return [e for e in self.elements if e.is_visible_at(t)]

    # --- Сериализация ---
    def to_dict(self) -> dict:
        return {
            "video_path": self.video_path,
            "name": self.name,
            "elements": [e.to_dict() for e in self.elements],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        elems = [OverlayElement.from_dict(d) for d in data.get("elements", [])]
        return cls(
            video_path=data.get("video_path", ""),
            name=data.get("name", "Новый проект"),
            elements=elems,
        )

    def save(self, path: str) -> None:
        """Сохраняет проект в JSON-файл."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str) -> "Project":
        """Загружает проект из JSON-файла."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


# ---------------------------------------------------------------------------
# Система Undo / Redo
# ---------------------------------------------------------------------------
class UndoRedoManager:
    """
    Простой менеджер отмены/повтора на основе снимков состояния.
    Хранит до *max_steps* снимков проекта.
    """

    def __init__(self, max_steps: int = 30):
        self._history: List[dict] = []
        self._index: int = -1
        self._max_steps = max_steps

    def save_state(self, project: Project) -> None:
        """Сохранить текущее состояние проекта в историю."""
        snapshot = copy.deepcopy(project.to_dict())

        # Обрезаем «будущие» состояния, если были отмены
        self._history = self._history[: self._index + 1]
        self._history.append(snapshot)

        # Ограничиваем длину истории
        if len(self._history) > self._max_steps:
            self._history = self._history[-self._max_steps:]

        self._index = len(self._history) - 1

    def undo(self) -> Optional[Project]:
        """Вернуть предыдущее состояние проекта (или None)."""
        if self._index > 0:
            self._index -= 1
            return Project.from_dict(copy.deepcopy(self._history[self._index]))
        return None

    def redo(self) -> Optional[Project]:
        """Повторить отменённое действие (или None)."""
        if self._index < len(self._history) - 1:
            self._index += 1
            return Project.from_dict(copy.deepcopy(self._history[self._index]))
        return None

    @property
    def can_undo(self) -> bool:
        return self._index > 0

    @property
    def can_redo(self) -> bool:
        return self._index < len(self._history) - 1

    def clear(self) -> None:
        self._history.clear()
        self._index = -1
