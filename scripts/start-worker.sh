#!/bin/bash

# Скрипт для запуска воркера с проверками

cd /ssd/www/videoeditor || exit 1

echo "=========================================="
echo "Video Editor Worker Startup Script"
echo "=========================================="
echo ""

# Проверка директории
if [ ! -d "/ssd/www/videoeditor" ]; then
    echo "ERROR: Directory /ssd/www/videoeditor does not exist!"
    exit 1
fi

# Проверка PHP
if ! command -v php &> /dev/null; then
    echo "ERROR: PHP is not installed or not in PATH!"
    exit 1
fi

# Проверка FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "WARNING: FFmpeg is not installed or not in PATH!"
    echo "Video processing will fail!"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ FFmpeg found: $(ffmpeg -version | head -n 1)"
fi

# Проверка директории логов
if [ ! -d "storage/logs" ]; then
    echo "Creating storage/logs directory..."
    mkdir -p storage/logs
    chmod 775 storage/logs
fi

# Проверка прав доступа
if [ ! -w "storage/logs" ]; then
    echo "WARNING: storage/logs is not writable!"
    echo "Attempting to fix permissions..."
    chmod 775 storage/logs
fi

# Проверка памяти
echo ""
echo "System memory:"
free -h | grep -E "Mem|Swap"
echo ""

# Проверка дискового пространства
echo "Disk space:"
df -h /ssd 2>/dev/null || df -h / | head -n 2
echo ""

# Запуск воркера
echo "=========================================="
echo "Starting worker..."
echo "=========================================="
echo "Press Ctrl+C to stop"
echo ""

php scripts/worker.php
