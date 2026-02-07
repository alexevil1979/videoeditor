"""
render_engine.py — Рендеринг итогового видео с наложением CTA-элементов.

Использует MoviePy v2 для композиции видео + оверлеи.
Поддерживает:
  • GPU-кодирование через NVIDIA NVENC (h264_nvenc) — снимает нагрузку с CPU
  • Автоматическое определение доступности GPU
  • Фоллбэк на libx264 (CPU) если GPU недоступен
  • GIF-анимации, PNG, fade in/out
  • Пакетную обработку нескольких видео (BatchRenderWorker)
  • Автосохранение в папку out/ рядом с исходным видео
"""

from __future__ import annotations

import copy
import os
import subprocess
import traceback
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image as PILImage

from PyQt6.QtCore import QThread, pyqtSignal, QSettings

# MoviePy v2 импорты
try:
    from moviepy import (
        VideoFileClip, ImageClip, CompositeVideoClip, VideoClip, vfx
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

from app.models import OverlayElement, Project


# ---------------------------------------------------------------------------
# Константы
# ---------------------------------------------------------------------------
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.webm', '.flv', '.m4v'}


# ---------------------------------------------------------------------------
# Удаление фона (chroma key) — для рендеринга
# ---------------------------------------------------------------------------
def _remove_bg_numpy(arr: np.ndarray, tolerance: int = 40) -> np.ndarray:
    """
    Удаляет фон из RGBA numpy-массива по цвету угловых пикселей.
    Аналогичный алгоритм используется в превью (video_preview.py).
    """
    if arr.ndim != 3 or arr.shape[2] < 3:
        return arr
    h, w = arr.shape[:2]
    result = arr.copy()
    if result.shape[2] == 3:
        alpha_ch = np.full((h, w, 1), 255, dtype=np.uint8)
        result = np.concatenate([result, alpha_ch], axis=2)

    corner_size = max(1, min(4, h // 10, w // 10))
    corners = []
    for cy, cx in [(0, 0), (0, w - corner_size), (h - corner_size, 0),
                   (h - corner_size, w - corner_size)]:
        patch = result[cy:cy + corner_size, cx:cx + corner_size, :3]
        corners.append(patch.reshape(-1, 3))
    bg_color = np.median(np.concatenate(corners, axis=0), axis=0).astype(np.float32)

    rgb = result[:, :, :3].astype(np.float32)
    diff = np.sqrt(np.sum((rgb - bg_color) ** 2, axis=2))

    edge_zone = tolerance * 0.3
    soft_mask = np.clip((diff - tolerance + edge_zone) / max(edge_zone, 1), 0, 1)
    result[:, :, 3] = (result[:, :, 3].astype(np.float32) * soft_mask).astype(np.uint8)
    return result


# ---------------------------------------------------------------------------
# Определение доступности GPU (NVIDIA NVENC)
# ---------------------------------------------------------------------------
_nvenc_available: Optional[bool] = None  # кеш результата


def check_nvenc_available() -> bool:
    """
    Проверяет, доступен ли кодировщик h264_nvenc в ffmpeg.
    Результат кешируется.
    """
    global _nvenc_available
    if _nvenc_available is not None:
        return _nvenc_available

    try:
        # Находим ffmpeg из imageio-ffmpeg (тот же, что использует MoviePy)
        try:
            import imageio_ffmpeg
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            ffmpeg_path = "ffmpeg"

        # Проверяем наличие h264_nvenc в списке кодировщиков
        result = subprocess.run(
            [ffmpeg_path, "-hide_banner", "-encoders"],
            capture_output=True, text=True, timeout=10,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        )
        _nvenc_available = "h264_nvenc" in result.stdout
    except Exception:
        _nvenc_available = False

    return _nvenc_available


def get_gpu_info() -> str:
    """Возвращает строку с информацией о доступности GPU-кодирования."""
    if check_nvenc_available():
        return "NVIDIA NVENC доступен (h264_nvenc)"
    return "NVENC недоступен — будет использован CPU (libx264)"


# ---------------------------------------------------------------------------
# Загрузка GIF-кадров
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Поиск видеофайлов в папке
# ---------------------------------------------------------------------------
def find_video_files(directory: str) -> List[str]:
    """Находит все видеофайлы в указанной директории (без рекурсии)."""
    result = []
    try:
        for f in Path(directory).iterdir():
            if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS:
                result.append(str(f))
    except Exception:
        pass
    return sorted(result)


# ---------------------------------------------------------------------------
# Параметры кодирования (GPU / CPU)
# ---------------------------------------------------------------------------
def _get_encoding_params(use_gpu: bool,
                         log_fn: Optional[Callable[[str], None]] = None) -> dict:
    """Определяет параметры кодирования: NVENC или libx264."""
    def log(msg: str):
        if log_fn:
            log_fn(msg)

    if use_gpu and check_nvenc_available():
        log("GPU-кодирование: NVIDIA NVENC (h264_nvenc)")
        return {
            "codec": "h264_nvenc",
            "ffmpeg_params": [
                "-preset", "p4",       # p1(fastest)..p7(quality), p4=balanced
                "-rc", "vbr",          # variable bitrate
                "-cq", "23",           # качество (ниже = лучше, 18-28 норма)
                "-b:v", "0",           # авто-битрейт
                "-gpu", "0",           # первый GPU
            ],
        }
    else:
        if use_gpu:
            log("NVENC недоступен — используется CPU (libx264)")
        else:
            log("CPU-кодирование: libx264")
        return {
            "codec": "libx264",
            "ffmpeg_params": [
                "-preset", "medium",
                "-crf", "23",
            ],
        }


# ---------------------------------------------------------------------------
# Создание оверлейных клипов (module-level функции)
# ---------------------------------------------------------------------------
def _make_overlay_clip(elem: OverlayElement, vw: int, vh: int, fps: float):
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
        overlay = _make_gif_clip(elem, target_h)
    else:
        overlay = _make_image_clip(elem, target_h)

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


def _make_gif_clip(elem: OverlayElement, target_h: int):
    """Создаёт анимированный клип из GIF."""
    frames, durations = _load_gif_frames(elem.file_path)
    if not frames:
        return _make_image_clip(elem, target_h)

    # Масштабируем кадры + удаление фона если включено
    scaled_frames_rgb = []
    scaled_frames_alpha = []

    for frame_arr in frames:
        # Удаление фона по цвету углов
        if elem.remove_bg:
            frame_arr = _remove_bg_numpy(frame_arr, elem.bg_tolerance)

        pil_frame = PILImage.fromarray(frame_arr)
        orig_w, orig_h = pil_frame.size
        if orig_h > 0:
            ratio = target_h / orig_h
            new_w = max(1, int(orig_w * ratio))
            new_h = max(1, target_h)
            pil_frame = pil_frame.resize((new_w, new_h), PILImage.LANCZOS)

        arr = np.array(pil_frame)
        if arr.shape[2] >= 4:
            scaled_frames_rgb.append(arr[:, :, :3])
            scaled_frames_alpha.append(arr[:, :, 3] / 255.0)
        else:
            scaled_frames_rgb.append(arr[:, :, :3])
            scaled_frames_alpha.append(np.ones((arr.shape[0], arr.shape[1])))

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

    # Маска (альфа-канал) — всегда создаём
    def make_mask(t):
        idx = _get_frame_index(t)
        return scaled_frames_alpha[idx]

    mask_clip = VideoClip(make_mask, duration=elem.duration, is_mask=True)
    mask_clip = mask_clip.with_fps(25)
    clip = clip.with_mask(mask_clip)

    return clip


def _make_image_clip(elem: OverlayElement, target_h: int):
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

    # Удаление фона если включено
    if elem.remove_bg:
        arr = _remove_bg_numpy(arr, elem.bg_tolerance)

    rgb = arr[:, :, :3]
    alpha = arr[:, :, 3] / 255.0 if arr.shape[2] >= 4 else np.ones(rgb.shape[:2])

    clip = ImageClip(rgb).with_duration(elem.duration)

    mask = ImageClip(alpha, is_mask=True).with_duration(elem.duration)
    clip = clip.with_mask(mask)

    return clip


# ---------------------------------------------------------------------------
# Ядро рендеринга — общая функция для единичного и пакетного режима
# ---------------------------------------------------------------------------
def render_project(project: Project, output_path: str, use_gpu: bool,
                   log_fn: Optional[Callable[[str], None]] = None,
                   progress_fn: Optional[Callable[[int], None]] = None) -> str:
    """
    Рендерит один проект (видео + наложения) в выходной файл.
    Возвращает путь к готовому файлу.
    Вызывается из RenderWorker и BatchRenderWorker.
    """
    def log(msg: str):
        if log_fn:
            log_fn(msg)

    def progress(val: int):
        if progress_fn:
            progress_fn(val)

    if not MOVIEPY_AVAILABLE:
        raise RuntimeError("MoviePy не установлен. pip install moviepy")

    video_path = project.video_path
    if not video_path or not os.path.exists(video_path):
        raise FileNotFoundError(f"Видео не найдено: {video_path}")

    progress(5)

    # Открываем исходное видео
    clip = VideoFileClip(video_path)
    video_w, video_h = clip.size
    fps = clip.fps
    duration = clip.duration

    log(f"Видео: {video_w}x{video_h}, {fps:.1f} fps, {duration:.1f} сек")

    # Пересчёт длительности «до конца видео» для каждого элемента
    for elem in project.elements:
        if elem.until_end:
            elem.duration = max(0.1, duration - elem.start_time)

    progress(10)

    # Создаём оверлейные клипы
    overlay_clips = []
    total_elems = len(project.elements)

    for idx, elem in enumerate(project.elements):
        try:
            overlay = _make_overlay_clip(elem, video_w, video_h, fps)
            if overlay is not None:
                overlay_clips.append(overlay)
                log(f"  Оверлей: {elem.name}")
        except Exception as e:
            log(f"  Предупреждение: {elem.name}: {e}")

        pct = 10 + int(40 * (idx + 1) / max(total_elems, 1))
        progress(pct)

    progress(50)

    # Композиция
    final = CompositeVideoClip([clip] + overlay_clips, size=(video_w, video_h))

    # Обеспечим директорию
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Определяем параметры кодирования
    enc = _get_encoding_params(use_gpu, log)
    progress(55)
    log(f"Кодек: {enc['codec']}")
    log("Запись видеофайла...")

    # Рендер
    final.write_videofile(
        output_path,
        codec=enc["codec"],
        audio_codec="aac",
        fps=fps,
        logger=None,
        ffmpeg_params=enc.get("ffmpeg_params", []),
    )

    progress(100)
    log(f"Готово: {output_path}")

    # Очищаем ресурсы
    final.close()
    clip.close()

    return output_path


# ---------------------------------------------------------------------------
# Поток рендеринга одного файла
# ---------------------------------------------------------------------------
class RenderWorker(QThread):
    """
    Поток рендеринга одного видео.
    Сигналы:
      progress(int)    — 0..100
      finished_ok(str) — путь к готовому файлу
      error(str)       — текст ошибки
      log(str)         — информационные сообщения
    """

    progress = pyqtSignal(int)
    finished_ok = pyqtSignal(str)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, project: Project, output_path: str,
                 use_gpu: bool = True, parent=None):
        super().__init__(parent)
        self._project = project
        self._output_path = output_path
        self._use_gpu = use_gpu

    def run(self):
        try:
            render_project(
                self._project, self._output_path, self._use_gpu,
                log_fn=self.log.emit,
                progress_fn=self.progress.emit,
            )
            self.finished_ok.emit(self._output_path)
        except Exception as e:
            self.error.emit(f"Ошибка рендеринга:\n{traceback.format_exc()}")


# ---------------------------------------------------------------------------
# Пакетный рендеринг — обработка всех видео в папке
# ---------------------------------------------------------------------------
class BatchRenderWorker(QThread):
    """
    Пакетный рендеринг: применяет одинаковые наложения ко всем видео в папке.
    Сигналы:
      progress(int)    — 0..100 (общий прогресс)
      log(str)         — сообщения о ходе работы
      finished_ok(str) — итоговое сообщение
      error(str)       — ошибка
    """

    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished_ok = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, elements_data: List[dict], video_files: List[str],
                 output_dir: str, prefix: str, use_gpu: bool, parent=None):
        super().__init__(parent)
        self._elements_data = elements_data  # сериализованные элементы
        self._video_files = video_files
        self._output_dir = output_dir
        self._prefix = prefix
        self._use_gpu = use_gpu

    def run(self):
        if not MOVIEPY_AVAILABLE:
            self.error.emit("MoviePy не установлен. pip install moviepy")
            return

        total = len(self._video_files)
        self.log.emit(f"Пакетная обработка: {total} файл(ов)\n")

        Path(self._output_dir).mkdir(parents=True, exist_ok=True)
        success = 0
        errors = 0

        for i, video_path in enumerate(self._video_files):
            fname = Path(video_path).name
            self.log.emit(f"\n{'='*50}")
            self.log.emit(f"[{i+1}/{total}] {fname}")
            self.log.emit(f"{'='*50}")

            try:
                # Создаём копию элементов с новыми ID для каждого файла
                elements = [OverlayElement.from_dict(d) for d in self._elements_data]
                project = Project(video_path=video_path, elements=elements)

                out_name = f"{self._prefix}{Path(video_path).stem}.mp4"
                out_path = str(Path(self._output_dir) / out_name)

                # Прогресс-колбэк: маппим прогресс файла на общий прогресс
                def file_progress(val, idx=i):
                    overall = int((idx * 100 + val) / total)
                    self.progress.emit(overall)

                render_project(
                    project, out_path, self._use_gpu,
                    log_fn=self.log.emit,
                    progress_fn=file_progress,
                )
                success += 1

            except Exception as e:
                self.log.emit(f"  ОШИБКА: {e}")
                errors += 1

            # Обновляем общий прогресс после каждого файла
            overall = int(100 * (i + 1) / total)
            self.progress.emit(overall)

        summary = f"\nОбработано: {success} из {total} файлов"
        if errors:
            summary += f" ({errors} с ошибками)"
        self.log.emit(summary)
        self.finished_ok.emit(summary)


# ---------------------------------------------------------------------------
# Утилиты: сохранение/загрузка настроек
# ---------------------------------------------------------------------------
def load_gpu_setting() -> bool:
    """Загружает настройку 'использовать GPU' из QSettings."""
    s = QSettings("VideoCTAEditor", "VideoCTAEditor")
    return s.value("render/use_gpu", True, type=bool)


def save_gpu_setting(use_gpu: bool) -> None:
    """Сохраняет настройку 'использовать GPU' в QSettings."""
    s = QSettings("VideoCTAEditor", "VideoCTAEditor")
    s.setValue("render/use_gpu", use_gpu)


def load_output_settings() -> dict:
    """Загружает настройки вывода (префикс, пакетная обработка) из QSettings."""
    s = QSettings("VideoCTAEditor", "VideoCTAEditor")
    return {
        "prefix": s.value("output/prefix", "cta_", type=str),
        "batch": s.value("output/batch", False, type=bool),
    }


def save_output_settings(prefix: str, batch: bool) -> None:
    """Сохраняет настройки вывода в QSettings."""
    s = QSettings("VideoCTAEditor", "VideoCTAEditor")
    s.setValue("output/prefix", prefix)
    s.setValue("output/batch", batch)
