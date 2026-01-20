# Исправление конфликта при git pull на сервере

## Проблема:
```
error: Your local changes to the following files would be overwritten by merge:
        SERVER_DEPLOY_COMMANDS.txt
        app/Services/FFmpegService.php
        scripts/worker.php
        views/dashboard/index.php
```

## Решение:

### Вариант 1: Сохранить изменения в stash (если они нужны)

```bash
cd /ssd/www/videoeditor

# Сохранить локальные изменения
git stash

# Обновить код
git pull origin main

# Посмотреть что было сохранено (опционально)
git stash list

# Если нужно вернуть изменения (обычно не нужно)
# git stash pop
```

### Вариант 2: Отменить локальные изменения (рекомендуется)

```bash
cd /ssd/www/videoeditor

# Отменить все локальные изменения
git reset --hard HEAD

# Обновить код
git pull origin main
```

### Вариант 3: Закоммитить локальные изменения (если они важны)

```bash
cd /ssd/www/videoeditor

# Добавить изменения
git add SERVER_DEPLOY_COMMANDS.txt app/Services/FFmpegService.php scripts/worker.php views/dashboard/index.php

# Закоммитить
git commit -m "Local server changes"

# Обновить код (может быть конфликт)
git pull origin main
```

## Рекомендация:

**Используйте Вариант 2** - отменить локальные изменения, так как все изменения должны приходить из Git репозитория, а не делаться напрямую на сервере.

## Быстрая команда:

```bash
cd /ssd/www/videoeditor && git reset --hard HEAD && git pull origin main
```
