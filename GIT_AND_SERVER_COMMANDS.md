# Команды Git и для сервера

## 🔵 ЛОКАЛЬНО (Windows) - Git команды

```bash
# Перейти в директорию проекта
cd "C:\Users\1\Documents\обработка видео"

# Добавить все изменения
git add -A

# Проверить статус
git status

# Создать коммит
git commit -m "Update: Apache configuration, domain videoeditor.1tlt.ru, remove zip/gd requirements"

# Запушить в репозиторий
git push origin main
```

## 🟢 НА СЕРВЕРЕ - Обновление и настройка

### Шаг 1: Обновить код из репозитория

```bash
cd /ssd/www/videoeditor

# Исправить ошибку Git ownership (если возникает)
git config --global --add safe.directory /ssd/www/videoeditor

# Обновить код
git pull origin main
```

### Шаг 2: Установить/обновить зависимости

```bash
composer install --no-dev --optimize-autoloader
```

### Шаг 3: Установить Apache (если еще не установлен)

```bash
sudo apt update
sudo apt install -y apache2 libapache2-mod-php8.1
sudo a2enmod rewrite php8.1 expires deflate
```

### Шаг 4: Настроить виртуальный хост Apache

```bash
cd /ssd/www/videoeditor
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf
sudo nano /etc/apache2/sites-available/videoeditor.conf  # Проверить ServerName: videoeditor.1tlt.ru
sudo a2ensite videoeditor.conf
sudo a2dissite 000-default.conf
sudo apache2ctl configtest
sudo systemctl restart apache2
```

### Шаг 5: Настроить базу данных (если нужно)

```bash
# Создать БД
mysql -u root -p
# CREATE DATABASE IF NOT EXISTS video_overlay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# CREATE USER IF NOT EXISTS 'video_user'@'localhost' IDENTIFIED BY 'your_password';
# GRANT ALL PRIVILEGES ON video_overlay.* TO 'video_user'@'localhost';
# FLUSH PRIVILEGES;
# EXIT;

# Настроить config.php
cd /ssd/www/videoeditor
cp config/config.example.php config/config.php
nano config/config.php  # Указать данные БД и URL: http://videoeditor.1tlt.ru

# Запустить миграции
php scripts/migrate.php
```

### Шаг 6: Установить PHP расширения (ОБЯЗАТЕЛЬНО только mbstring)

```bash
# ОБЯЗАТЕЛЬНО: mbstring (для работы со строками)
sudo apt install -y php-pear php8.1-dev
pecl install mbstring
echo "extension=mbstring.so" >> /usr/local/php8.1/etc/php.ini
/usr/local/php8.1/bin/php -m | grep mbstring
sudo systemctl restart php8.1-fpm

# ⚠️ НЕ УСТАНАВЛИВАЙТЕ zip и gd - они НЕ требуются!
# - zip - не используется в коде
# - gd - опционально, без него кнопки будут текстовыми
```

### Шаг 7: Настроить права доступа

```bash
cd /ssd/www/videoeditor
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage
```

### Шаг 8: Настроить воркер

```bash
cd /ssd/www/videoeditor
sudo cp scripts/video-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable video-worker
sudo systemctl start video-worker
sudo systemctl status video-worker
```

### Шаг 9: Проверка

```bash
# Проверить Apache
sudo systemctl status apache2
sudo apache2ctl configtest

# Проверить воркер
sudo systemctl status video-worker

# Проверить логи
sudo tail -f /var/log/apache2/videoeditor_error.log
```

### Шаг 10: Настройте SSL (опционально, но рекомендуется)

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

## 📋 Быстрая команда (все сразу)

```bash
# На сервере выполните:
cd /ssd/www/videoeditor && \
git config --global --add safe.directory /ssd/www/videoeditor && \
git pull origin main && \
composer install --no-dev --optimize-autoloader && \
sudo systemctl restart apache2 && \
sudo systemctl restart video-worker
```
