"""
render_engine.py — Рендеринг итогового видео с наложением CTA-элементов.

Использует MoviePy v2 для композиции видео + оверлеи.
Поддерживает GIF-анимации, PNG, fade in/out.
"""

from __future__ import annotations

import os
import traceback
from pathlib import Path
from typing import List, Optional

import numpy as np
from PIL import Image as PILImage

from PyQt6.QtCore import QThread, pyqtSignal

# MoviePy v2 импорты
try:
    from moviepy import (
        VideoFileClip, ImageClip, CompositeVideoClip, VideoClip, vfx
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

from app.models import OverlayElement, Project


def _load_gif_frames(path: str):
    """Загружает кадры GIF и возвращает список numpy-массивов + длительности."""
    frames = []
    durations = []
    try:
        img = PILImage.open(path)
        n = getattr(img, 'n_frames', 1)
        for i in range(n):
            img.seek(i)
            frame = img.convert("RGBA")
            frames.append(np.array(frame))
            dur = img.info.get('duration', 100)
            durations.append(dur / 1000.0)  # мс → сек
    except Exception:
        pass
    return frames, durations


class RenderWorker(QThread):
    """
    Поток рендеринга видео.
    Сигналы:
      progress(int)  — 0..100
      finished_ok(str) — путь к готовому файлу
      error(str)     — текст ошибки
    """

    progress = pyqtSignal(int)
    finished_ok = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, project: Project, output_path: str, parent=None):
        super().__init__(parent)
        self._project = project
        self._output_path = output_path

    def run(self):
        if not MOVIEPY_AVAILABLE:
            self.error.emit("MoviePy не установлен. Установите: pip install moviepy")
            return

        try:
            self._render()
        except Exception as e:
            self.error.emit(f"Ошибка рендеринга:\n{traceback.format_exc()}")

    def _render(self):
        video_path = self._project.video_path
        if not video_path or not os.path.exists(video_path):
            self.error.emit(f"Видео не найдено: {video_path}")
            return

        self.progress.emit(5)

        # Открываем исходное видео
        clip = VideoFileClip(video_path)
        video_w, video_h = clip.size
        fps = clip.fps
        duration = clip.duration

        self.progress.emit(10)

        # Создаём оверлейные клипы
        overlay_clips = []
        total_elems = len(self._project.elements)

        for idx, elem in enumerate(self._project.elements):
            try:
                overlay = self._make_overlay_clip(
                    elem, video_w, video_h, fps
                )
                if overlay is not None:
                    overlay_clips.append(overlay)
            except Exception as e:
                print(f"Предупреждение: не удалось создать оверлей для {elem.name}: {e}")

            progress_pct = 10 + int(40 * (idx + 1) / max(total_elems, 1))
            self.progress.emit(progress_pct)

        self.progress.emit(50)

        # Композиция
        final = CompositeVideoClip([clip] + overlay_clips, size=(video_w, video_h))

        # Обеспечим директорию
        Path(self._output_path).parent.mkdir(parents=True, exist_ok=True)

        # Рендер
        self.progress.emit(55)

        final.write_videofile(
            self._output_path,
            codec="libx264",
            audio_codec="aac",
            fps=fps,
            logger=None,  # Убираем вывод MoviePy
            preset="medium",
        )

        self.progress.emit(100)
        self.finished_ok.emit(self._output_path)

        # Очищаем ресурсы
        final.close()
        clip.close()

    def _make_overlay_clip(self, elem: OverlayElement, vw: int, vh: int, fps: float):
        """Создаёт MoviePy-клип для одного оверлейного элемента."""
        if not elem.file_path or not os.path.exists(elem.file_path):
            return None

        ext = Path(elem.file_path).suffix.lower()

        # Позиция в пикселях
        x_px = int(vw * elem.x_percent / 100.0)
        y_px = int(vh * elem.y_percent / 100.0)

        # Масштаб: базовый размер = 15% от min(vw, vh)
        base_size = min(vw, vh) * 0.15
        target_h = int(base_size * elem.scale / 100.0)

        if ext in ('.gif', '.apng'):
            overlay = self._make_gif_clip(elem, target_h)
        else:
            overlay = self._make_image_clip(elem, target_h)

        if overlay is None:
            return None

        # Позиция (центрирование) — MoviePy v2 API: with_position
        ow, oh = overlay.size
        pos_x = max(0, x_px - ow // 2)
        pos_y = max(0, y_px - oh // 2)

        overlay = overlay.with_position((pos_x, pos_y))
        overlay = overlay.with_start(elem.start_time)
        overlay = overlay.with_duration(elem.duration)

        # Прозрачность — MoviePy v2: with_opacity
        if elem.opacity < 100:
            overlay = overlay.with_opacity(elem.opacity / 100.0)

        # Fade in / out — MoviePy v2: with_effects
        effects = []
        if elem.fade_in > 0:
            effects.append(vfx.CrossFadeIn(elem.fade_in))
        if elem.fade_out > 0:
            effects.append(vfx.CrossFadeOut(elem.fade_out))
        if effects:
            overlay = overlay.with_effects(effects)

        return overlay

    def _make_gif_clip(self, elem: OverlayElement, target_h: int):
        """Создаёт анимированный клип из GIF."""
        frames, durations = _load_gif_frames(elem.file_path)
        if not frames:
            return self._make_image_clip(elem, target_h)

        # Масштабируем кадры
        scaled_frames_rgb = []
        scaled_frames_alpha = []
        has_alpha = frames[0].shape[-1] == 4

        for frame_arr in frames:
            pil_frame = PILImage.fromarray(frame_arr)
            orig_w, orig_h = pil_frame.size
            if orig_h > 0:
                ratio = target_h / orig_h
                new_w = max(1, int(orig_w * ratio))
                new_h = max(1, target_h)
                pil_frame = pil_frame.resize((new_w, new_h), PILImage.LANCZOS)

            arr = np.array(pil_frame)
            if has_alpha:
                scaled_frames_rgb.append(arr[:, :, :3])
                scaled_frames_alpha.append(arr[:, :, 3] / 255.0)
            else:
                scaled_frames_rgb.append(arr[:, :, :3])

        if not scaled_frames_rgb:
            return None

        # Длительность GIF-цикла
        total_gif_dur = sum(durations) if durations else 1.0

        def _get_frame_index(t):
            """Определяет индекс кадра GIF для момента времени t."""
            gif_t = t % total_gif_dur if total_gif_dur > 0 else 0
            accum = 0
            for i, dur in enumerate(durations):
                accum += dur
                if gif_t < accum:
                    return i
            return len(durations) - 1

        def make_frame_rgb(t):
            idx = _get_frame_index(t)
            return scaled_frames_rgb[idx]

        clip = VideoClip(make_frame_rgb, duration=elem.duration)
        clip = clip.with_fps(25)

        # Маска (альфа-канал)
        if has_alpha and scaled_frames_alpha:
            def make_mask(t):
                idx = _get_frame_index(t)
                return scaled_frames_alpha[idx]

            mask_clip = VideoClip(make_mask, duration=elem.duration, is_mask=True)
            mask_clip = mask_clip.with_fps(25)
            clip = clip.with_mask(mask_clip)

        return clip

    def _make_image_clip(self, elem: OverlayElement, target_h: int):
        """Создаёт статичный клип из изображения."""
        try:
            pil_img = PILImage.open(elem.file_path).convert("RGBA")
        except Exception:
            return None

        orig_w, orig_h = pil_img.size
        if orig_h > 0:
            ratio = target_h / orig_h
            new_w = max(1, int(orig_w * ratio))
            new_h = max(1, target_h)
            pil_img = pil_img.resize((new_w, new_h), PILImage.LANCZOS)

        arr = np.array(pil_img)
        rgb = arr[:, :, :3]
        alpha = arr[:, :, 3] / 255.0

        clip = ImageClip(rgb).with_duration(elem.duration)

        mask = ImageClip(alpha, is_mask=True).with_duration(elem.duration)
        clip = clip.with_mask(mask)

        return clip
