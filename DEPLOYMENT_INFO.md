# Информация о развертывании

## Репозиторий
- **GitHub**: https://github.com/alexevil1979/videoeditor
- **Ветка**: main

## Пути на сервере
- **Корень проекта**: `/ssd/www/videoeditor`
- **Public**: `/ssd/www/videoeditor/public`
- **Storage**: `/ssd/www/videoeditor/storage`
- **Config**: `/ssd/www/videoeditor/config`

## Nginx
- **Конфиг**: `/etc/nginx/sites-available/videoeditor`
- **Логи**: 
  - Access: `/var/log/nginx/videoeditor-access.log`
  - Error: `/var/log/nginx/videoeditor-error.log`

## Systemd сервис
- **Файл**: `/etc/systemd/system/video-worker.service`
- **Команда**: `sudo systemctl {start|stop|restart|status} video-worker`

## Быстрая установка

```bash
# Клонирование
cd /ssd/www
git clone https://github.com/alexevil1979/videoeditor.git videoeditor
cd videoeditor

# Установка зависимостей
composer install --no-dev --optimize-autoloader

# Конфигурация
cp config/config.example.php config/config.php
# Отредактируйте config.php

# База данных
php scripts/migrate.php

# Права доступа
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage

# Nginx
sudo cp config/nginx.conf /etc/nginx/sites-available/videoeditor
sudo ln -s /etc/nginx/sites-available/videoeditor /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Воркер
sudo cp scripts/video-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable video-worker
sudo systemctl start video-worker
```

## Обновление

```bash
cd /ssd/www/videoeditor
git pull origin main
composer install --no-dev --optimize-autoloader
php scripts/migrate.php
sudo systemctl reload php8.1-fpm
sudo systemctl reload nginx
sudo systemctl restart video-worker
```
