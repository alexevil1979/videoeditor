# ✅ ФИНАЛЬНЫЕ команды для сервера (БЕЗ zip и gd)

## 🔵 ЛОКАЛЬНО (Windows) - Git

```bash
cd "C:\Users\1\Documents\обработка видео"
git add -A
git commit -m "Update: Apache config, domain videoeditor.1tlt.ru, no zip/gd required"
git push origin main
```

## 🟢 НА СЕРВЕРЕ - Все команды

### 1. Проверьте/клонируйте проект

```bash
# Если проект уже есть
cd /ssd/www/videoeditor
ls -la  # Проверьте что есть composer.json

# ИЛИ клонируйте заново
cd /ssd/www
git clone https://github.com/alexevil1979/videoeditor.git videoeditor
cd videoeditor
```

### 2. Обновите код и зависимости

```bash
cd /ssd/www/videoeditor

# Исправить ошибку Git ownership (если возникает)
git config --global --add safe.directory /ssd/www/videoeditor

# Обновить код
git pull origin main

# Установить зависимости
composer install --no-dev --optimize-autoloader
```

### 3. Установите Apache

```bash
sudo apt update
sudo apt install -y apache2 libapache2-mod-php8.1
sudo a2enmod rewrite php8.1 expires deflate
```

### 4. Настройте Apache

```bash
cd /ssd/www/videoeditor
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf
sudo nano /etc/apache2/sites-available/videoeditor.conf  # ServerName: videoeditor.1tlt.ru

# Включите необходимые модули
sudo a2enmod ssl
sudo a2enmod rewrite
sudo a2enmod proxy
sudo a2enmod proxy_fcgi

sudo a2ensite videoeditor.conf
sudo a2dissite 000-default.conf
sudo apache2ctl configtest
sudo systemctl restart apache2
```

### 5. Настройте базу данных

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

# Если таблиц нет, импортируйте схему напрямую:
mysql -u video_user -p video_overlay < database/schema.sql

# Проверьте снова
mysql -u video_user -p video_overlay -e "SHOW TABLES;"
```

### 6. Установите ТОЛЬКО mbstring (обязательно)

```bash
# ⚠️ ВАЖНО: Устанавливаем ТОЛЬКО mbstring!
# zip и gd НЕ требуются!

sudo apt install -y php-pear php8.1-dev
pecl install mbstring
echo "extension=mbstring.so" >> /usr/local/php8.1/etc/php.ini
/usr/local/php8.1/bin/php -m | grep mbstring
sudo systemctl restart php8.1-fpm
```

### 7. Права доступа

```bash
cd /ssd/www/videoeditor
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage
```

### 8. Воркер

```bash
cd /ssd/www/videoeditor
sudo cp scripts/video-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable video-worker
sudo systemctl start video-worker
sudo systemctl status video-worker
```

### 9. Проверка

```bash
sudo systemctl status apache2
sudo systemctl status video-worker
sudo tail -f /var/log/apache2/videoeditor_error.log
```

## ⚠️ ВАЖНО: Что НЕ нужно устанавливать

- ❌ **zip** - не используется в коде, не требуется
- ❌ **gd** - опционально, без него кнопки будут текстовыми (приложение работает)

## ✅ Что нужно установить

- ✅ **mbstring** - обязательно для работы со строками
- ✅ **pdo_mysql** - обычно уже установлен с PHP

### 10. Настройте SSL (опционально, но рекомендуется)

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

## 📋 Быстрая команда (если проект уже настроен)

```bash
cd /ssd/www/videoeditor && \
git config --global --add safe.directory /ssd/www/videoeditor && \
git pull origin main && \
composer install --no-dev --optimize-autoloader && \
sudo systemctl restart apache2 && \
sudo systemctl restart video-worker
```
