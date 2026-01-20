# ✅ ПРАВИЛЬНЫЕ команды для сервера

## 🔵 ЛОКАЛЬНО (Windows) - Git команды

```bash
cd "C:\Users\1\Documents\обработка видео"
git add -A
git commit -m "Update: Apache configuration, domain videoeditor.1tlt.ru, remove zip/gd requirements"
git push origin main
```

## 🟢 НА СЕРВЕРЕ - Правильный путь: /ssd/www/videoeditor

### Шаг 1: Проверьте структуру директорий

```bash
# Проверьте что существует
ls -la /ssd/www/

# Если есть /ssd/www/videoeditor - используйте его
# Если нет - клонируйте репозиторий
```

### Шаг 2: Если проект уже есть в /ssd/www/videoeditor

```bash
cd /ssd/www/videoeditor
ls -la  # Проверьте что есть composer.json, app/, config/ и т.д.

# Исправить ошибку Git ownership (если возникает)
git config --global --add safe.directory /ssd/www/videoeditor

# Обновите код
git pull origin main

# Установите зависимости
composer install --no-dev --optimize-autoloader
```

### Шаг 3: Если проекта нет - клонируйте

```bash
cd /ssd/www
git clone https://github.com/alexevil1979/videoeditor.git videoeditor
cd videoeditor

# Установите зависимости
composer install --no-dev --optimize-autoloader
```

### Шаг 4: Установите Apache (если еще не установлен)

```bash
sudo apt update
sudo apt install -y apache2 libapache2-mod-php8.1
sudo a2enmod rewrite php8.1 expires deflate
```

### Шаг 5: Настройте виртуальный хост Apache

```bash
cd /ssd/www/videoeditor
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf
sudo nano /etc/apache2/sites-available/videoeditor.conf  # Проверить ServerName: videoeditor.1tlt.ru
sudo a2ensite videoeditor.conf
sudo a2dissite 000-default.conf
sudo apache2ctl configtest
sudo systemctl restart apache2
```

### Шаг 6: Настройте базу данных

```bash
# Создайте БД
mysql -u root -p
```

```sql
CREATE DATABASE IF NOT EXISTS video_overlay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'video_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON video_overlay.* TO 'video_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

```bash
# Настройте config.php
cd /ssd/www/videoeditor
cp config/config.example.php config/config.php
nano config/config.php
# Укажите:
# - 'url' => 'http://videoeditor.1tlt.ru'
# - Данные БД (host, name, user, password)

# Запустите миграции
php scripts/migrate.php

# Проверьте таблицы
mysql -u video_user -p video_overlay -e "SHOW TABLES;"
```

### Шаг 7: Установите PHP расширения (ОБЯЗАТЕЛЬНО только mbstring)

```bash
# ОБЯЗАТЕЛЬНО: mbstring (для работы со строками)
sudo apt install -y php-pear php8.1-dev
pecl install mbstring
echo "extension=mbstring.so" >> /usr/local/php8.1/etc/php.ini
/usr/local/php8.1/bin/php -m | grep mbstring
sudo systemctl restart php8.1-fpm

# ⚠️ НЕ УСТАНАВЛИВАЙТЕ zip и gd - они НЕ требуются!
# Приложение работает без них:
# - zip - не используется в коде
# - gd - опционально, без него кнопки будут текстовыми
```

### Шаг 8: Настройте права доступа

```bash
cd /ssd/www/videoeditor
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage
```

### Шаг 9: Настройте воркер

```bash
cd /ssd/www/videoeditor
sudo cp scripts/video-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable video-worker
sudo systemctl start video-worker
sudo systemctl status video-worker
```

### Шаг 10: Проверка

```bash
# Проверить Apache
sudo systemctl status apache2
sudo apache2ctl configtest

# Проверить воркер
sudo systemctl status video-worker

# Проверить логи
sudo tail -f /var/log/apache2/videoeditor_error.log
```

### Шаг 11: Настройте SSL (опционально, но рекомендуется)

```bash
# Установите Certbot
sudo apt install -y certbot python3-certbot-apache

# Настройте SSL автоматически
sudo certbot --apache -d videoeditor.1tlt.ru

# Обновите config.php для HTTPS
cd /ssd/www/videoeditor
nano config/config.php
# Измените 'url' => 'https://videoeditor.1tlt.ru'
```

## 📋 Быстрая команда (если проект уже есть)

```bash
cd /ssd/www/videoeditor && \
git config --global --add safe.directory /ssd/www/videoeditor && \
git pull origin main && \
composer install --no-dev --optimize-autoloader && \
sudo systemctl restart apache2 && \
sudo systemctl restart video-worker
```
