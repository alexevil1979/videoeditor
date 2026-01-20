# Как посмотреть полную ошибку FFmpeg

## Проблема:
Вывод показывает только версию FFmpeg, но не саму ошибку.

## Решение:

### 1. Проверить полный лог FFmpeg:

```bash
tail -100 /ssd/www/videoeditor/storage/logs/ffmpeg_commands.log
```

### 2. Проверить лог ошибок воркера:

```bash
tail -100 /ssd/www/videoeditor/storage/logs/worker_errors.log
```

### 3. Попробовать запустить команду FFmpeg вручную:

Скопируйте команду из лога и запустите в терминале:

```bash
ffmpeg -i '/ssd/www/videoeditor/storage/uploads/video_6970009748e5a6.03866459.mp4' -filter_complex '[0:v]scale=1080:-1[v];[v]drawtext=text='\''SUBSCRIBE'\'':fontsize=24:fontcolor=#FFFFFF:x=540:y=960:[v]' -map "[v]" -map 0:a? -c:v libx264 -c:a aac -crf 23 -preset medium -threads 4 -movflags +faststart -y /tmp/test_output.mp4
```

Это покажет реальную ошибку FFmpeg.

### 4. Возможные проблемы:

1. **Проблема с экранированием кавычек** - текст 'SUBSCRIBE' может быть неправильно экранирован
2. **Проблема с фильтром drawtext** - возможно нужен шрифт
3. **Проблема с путями** - относительные пути могут не работать

### 5. Проверить что файл существует:

```bash
ls -la /ssd/www/videoeditor/storage/uploads/video_6970009748e5a6.03866459.mp4
```
