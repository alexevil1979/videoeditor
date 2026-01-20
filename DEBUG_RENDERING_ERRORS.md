# Диагностика ошибок рендеринга видео

## Как найти причину ошибки

### 1. Проверить логи воркера

```bash
# Просмотр логов ошибок воркера
tail -f /ssd/www/videoeditor/storage/logs/worker_errors.log

# Просмотр логов команд FFmpeg
tail -f /ssd/www/videoeditor/storage/logs/ffmpeg_commands.log
```

### 2. Проверить ошибку в базе данных

```bash
mysql -u video_user -p video_overlay -e "SELECT id, error_message FROM render_jobs WHERE status='failed' ORDER BY id DESC LIMIT 5;"
```

### 3. Проверить конкретную задачу

```bash
# Замените 3 на ID вашей задачи
mysql -u video_user -p video_overlay -e "SELECT * FROM render_jobs WHERE id=3;"
```

### 4. Проверить файл видео

```bash
# Проверить что файл существует
ls -la /ssd/www/videoeditor/storage/uploads/

# Проверить права доступа
ls -la /ssd/www/videoeditor/storage/
```

### 5. Проверить FFmpeg

```bash
# Проверить версию
ffmpeg -version

# Проверить что FFmpeg доступен
which ffmpeg
```

## Типичные ошибки и решения

### Ошибка: "Input video file not found"

**Причина:** Файл видео не существует по указанному пути

**Решение:**
```bash
# Проверить путь к файлу
mysql -u video_user -p video_overlay -e "SELECT id, storage_path FROM videos WHERE id=1;"

# Проверить что файл существует
ls -la /ssd/www/videoeditor/storage/uploads/
```

### Ошибка: "Output directory is not writable"

**Причина:** Нет прав на запись в директорию renders

**Решение:**
```bash
sudo chown -R www-data:www-data /ssd/www/videoeditor/storage
sudo chmod -R 775 /ssd/www/videoeditor/storage
```

### Ошибка: "FFmpeg processing failed"

**Причина:** Проблема с командой FFmpeg или форматом видео

**Решение:**
1. Проверить логи FFmpeg:
   ```bash
   tail -50 /ssd/www/videoeditor/storage/logs/ffmpeg_commands.log
   ```

2. Попробовать запустить команду FFmpeg вручную (из логов)

3. Проверить формат видео:
   ```bash
   ffprobe /ssd/www/videoeditor/storage/uploads/your_video.mp4
   ```

### Ошибка: "Invalid video or preset"

**Причина:** Видео или пресет не найдены в базе данных

**Решение:**
```bash
# Проверить видео
mysql -u video_user -p video_overlay -e "SELECT * FROM videos WHERE id=1;"

# Проверить пресет
mysql -u video_user -p video_overlay -e "SELECT * FROM presets WHERE id=1;"

# Проверить элементы пресета
mysql -u video_user -p video_overlay -e "SELECT * FROM preset_items WHERE preset_id=1;"
```

## Запуск воркера в режиме отладки

```bash
cd /ssd/www/videoeditor
php scripts/worker.php
```

Воркер выведет все ошибки в консоль в реальном времени.

## Проверка работы воркера

```bash
# Проверить статус сервиса
sudo systemctl status video-worker

# Просмотр логов systemd
sudo journalctl -u video-worker -f

# Перезапустить воркер
sudo systemctl restart video-worker
```
