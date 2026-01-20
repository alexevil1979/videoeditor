# Исправление ошибки Git "dubious ownership"

## Проблема
```
fatal: detected dubious ownership in repository at '/ssd/www/videoeditor'
```

## Решение

### Вариант 1: Добавить исключение (быстро)

```bash
git config --global --add safe.directory /ssd/www/videoeditor
git pull origin main
```

### Вариант 2: Изменить владельца (правильно)

```bash
# Изменить владельца на текущего пользователя (root)
sudo chown -R root:root /ssd/www/videoeditor

# Или на www-data (если нужно)
# sudo chown -R www-data:www-data /ssd/www/videoeditor

# Теперь можно делать git pull
git pull origin main
```

### Вариант 3: Для всех директорий (если нужно)

```bash
git config --global --add safe.directory '*'
```

## Рекомендуемое решение

```bash
# 1. Добавить исключение для этой директории
git config --global --add safe.directory /ssd/www/videoeditor

# 2. Теперь можно делать git pull
cd /ssd/www/videoeditor
git pull origin main

# 3. После этого установить правильные права для веб-сервера
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage
```
