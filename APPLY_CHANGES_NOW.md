# Команды для применения изменений

## 1. Локально: Закоммитить и запушить в Git

```bash
# Добавить все изменения
git add -A

# Проверить что будет закоммичено
git status

# Создать коммит
git commit -m "Update: Apache configuration, domain videoeditor.1tlt.ru, remove zip/gd requirements"

# Запушить в репозиторий
git push origin main
```

## 2. На сервере: Обновить код и настроить

```bash
# Перейти в директорию проекта
cd /ssd/www/videoeditor

# Обновить код из репозитория
git pull origin main

# Установить/обновить зависимости (если нужно)
composer install --no-dev --optimize-autoloader
```

## 3. На сервере: Установить Apache (если еще не установлен)

```bash
# Установить Apache и модуль PHP
sudo apt update
sudo apt install -y apache2 libapache2-mod-php8.1

# Включить необходимые модули
sudo a2enmod rewrite
sudo a2enmod php8.1
sudo a2enmod expires
sudo a2enmod deflate
```

## 4. На сервере: Настроить виртуальный хост Apache

```bash
cd /ssd/www/videoeditor

# Скопировать конфигурацию
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf

# Отредактировать (проверить ServerName)
sudo nano /etc/apache2/sites-available/videoeditor.conf
# Убедитесь что ServerName: videoeditor.1tlt.ru

# Включить сайт
sudo a2ensite videoeditor.conf

# Отключить сайт по умолчанию (опционально)
sudo a2dissite 000-default.conf

# Проверить конфигурацию
sudo apache2ctl configtest

# Перезапустить Apache
sudo systemctl restart apache2
```

## 5. На сервере: Настроить базу данных (если еще не настроена)

```bash
# Создать базу данных
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
# Настроить config.php
cd /ssd/www/videoeditor
cp config/config.example.php config/config.php
nano config/config.php
# Укажите правильные данные БД и URL: http://videoeditor.1tlt.ru

# Запустить миграции
php scripts/migrate.php

# Проверить таблицы
mysql -u video_user -p video_overlay -e "SHOW TABLES;"
```

## 6. На сервере: Установить обязательные PHP расширения

```bash
# ОБЯЗАТЕЛЬНО: mbstring (для работы со строками)
sudo apt install -y php-pear php8.1-dev
pecl install mbstring
echo "extension=mbstring.so" >> /usr/local/php8.1/etc/php.ini

# Проверить
/usr/local/php8.1/bin/php -m | grep mbstring

# Перезапустить PHP-FPM
sudo systemctl restart php8.1-fpm

# ⚠️ ВАЖНО: НЕ устанавливайте zip и gd!
# - zip - не используется в коде, не требуется
# - gd - опционально, без него кнопки будут текстовыми (работает нормально)
```

## 7. На сервере: Настроить права доступа

```bash
cd /ssd/www/videoeditor

# Установить права
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage
```

## 8. На сервере: Настроить воркер

```bash
cd /ssd/www/videoeditor

# Скопировать service файл
sudo cp scripts/video-worker.service /etc/systemd/system/

# Перезагрузить systemd
sudo systemctl daemon-reload

# Включить автозапуск
sudo systemctl enable video-worker

# Запустить воркер
sudo systemctl start video-worker

# Проверить статус
sudo systemctl status video-worker
```

## 9. На сервере: Проверка

```bash
# Проверить Apache
sudo systemctl status apache2
sudo apache2ctl configtest

# Проверить воркер
sudo systemctl status video-worker

# Проверить логи
sudo tail -f /var/log/apache2/videoeditor_error.log
sudo journalctl -u video-worker -f
```

## 10. Открыть в браузере

```
http://videoeditor.1tlt.ru
```

## Полная последовательность (если все с нуля)

```bash
# 1. Git
cd "C:\Users\1\Documents\обработка видео"
git add -A
git commit -m "Update: Apache config, domain videoeditor.1tlt.ru, remove zip/gd requirements"
git push origin main

# 2. На сервере - обновить код
cd /ssd/www/videoeditor
git pull origin main

# 3. Установить Apache
sudo apt install -y apache2 libapache2-mod-php8.1
sudo a2enmod rewrite php8.1 expires deflate

# 4. Настроить Apache
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf
sudo nano /etc/apache2/sites-available/videoeditor.conf  # Проверить ServerName
sudo a2ensite videoeditor.conf
sudo a2dissite 000-default.conf
sudo apache2ctl configtest
sudo systemctl restart apache2

# 5. Установить зависимости
composer install --no-dev --optimize-autoloader

# 6. Настроить БД (если нужно)
cp config/config.example.php config/config.php
nano config/config.php  # Указать данные БД и URL
php scripts/migrate.php

# 7. Установить mbstring (если нужно)
sudo apt install -y php-pear php8.1-dev
pecl install mbstring
echo "extension=mbstring.so" >> /usr/local/php8.1/etc/php.ini
sudo systemctl restart php8.1-fpm

# 8. Права доступа
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage

# 9. Воркер
sudo cp scripts/video-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable video-worker
sudo systemctl start video-worker

# 10. Проверка
sudo systemctl status apache2
sudo systemctl status video-worker
```
