# Исправление пути на сервере

## Проблема
Директория `/ssd/www/videoeditor/videoeditor` не существует.

## Решение

### 1. Проверьте где находится проект

```bash
# Проверьте структуру
ls -la /ssd/www/
ls -la /ssd/www/videoeditor/

# Если проект в /ssd/www/videoeditor (без двойного videoeditor)
cd /ssd/www/videoeditor
ls -la
```

### 2. Если проект уже клонирован в /ssd/www/videoeditor

```bash
cd /ssd/www/videoeditor
git pull origin main
composer install --no-dev --optimize-autoloader
```

### 3. Если проект нужно клонировать заново

```bash
# Удалите старую директорию (если есть)
rm -rf /ssd/www/videoeditor

# Клонируйте репозиторий
cd /ssd/www
git clone https://github.com/alexevil1979/videoeditor.git videoeditor
cd videoeditor

# Установите зависимости
composer install --no-dev --optimize-autoloader
```

### 4. Настройте Apache (путь должен быть /ssd/www/videoeditor)

```bash
cd /ssd/www/videoeditor

# Отредактируйте apache.conf если нужно
nano config/apache.conf
# Убедитесь что DocumentRoot: /ssd/www/videoeditor/public

# Скопируйте конфигурацию
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf
sudo a2ensite videoeditor.conf
sudo apache2ctl configtest
sudo systemctl restart apache2
```

### 5. Настройте config.php

```bash
cd /ssd/www/videoeditor
cp config/config.example.php config/config.php
nano config/config.php
# Укажите:
# - URL: http://videoeditor.1tlt.ru
# - Данные БД
```

### 6. Запустите миграции

```bash
cd /ssd/www/videoeditor
php scripts/migrate.php
```

### 7. Настройте права

```bash
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage
```
