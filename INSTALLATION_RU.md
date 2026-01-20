# Руководство по установке

## Быстрый старт

### 1. Предварительные требования

- VPS Ubuntu 20.04+
- Root или sudo доступ
- Доменное имя (опционально, можно использовать IP)

### 2. Установка системных зависимостей

```bash
sudo apt update
sudo apt install -y php8.1-fpm php8.1-mysql php8.1-mbstring apache2 libapache2-mod-php8.1 mysql-server ffmpeg git composer

# Опционально: Установите GD для кнопок наложений
# sudo apt install -y php8.1-gd

# Проверьте установленные расширения PHP
php -m | grep -E "pdo_mysql|mbstring"

# Если расширения отсутствуют:
# sudo apt install -y php8.1-mbstring
# sudo systemctl restart php8.1-fpm
```

### 3. Настройка базы данных

```bash
sudo mysql
```

```sql
CREATE DATABASE video_overlay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'video_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON video_overlay.* TO 'video_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. Клонирование и настройка приложения

```bash
cd /ssd/www
sudo git clone https://github.com/alexevil1979/videoeditor.git videoeditor
cd videoeditor
sudo composer install --no-dev --optimize-autoloader
```

### 5. Конфигурация приложения

```bash
sudo cp config/config.example.php config/config.php
sudo nano config/config.php
```

Обновите учетные данные базы данных и другие настройки.

### 6. Инициализация базы данных

```bash
sudo php scripts/migrate.php
```

### 7. Установка прав доступа

```bash
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage
```

### 8. Конфигурация Nginx

```bash
sudo a2enmod rewrite php8.1 expires deflate
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf
sudo nano /etc/apache2/sites-available/videoeditor.conf
# Обновите ServerName на videoeditor.1tlt.ru
sudo a2ensite videoeditor.conf
sudo a2dissite 000-default.conf
sudo apache2ctl configtest
sudo systemctl restart apache2
```

### 9. Настройка сервиса воркера

```bash
sudo cp scripts/video-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable video-worker
sudo systemctl start video-worker
sudo systemctl status video-worker
```

### 10. Проверка установки

1. Откройте ваш домен/IP в браузере
2. Зарегистрируйте новый аккаунт
3. Войдите с учетными данными администратора:
   - Email: `admin@example.com`
   - Пароль: `admin123`
4. **ВАЖНО**: Измените пароль администратора немедленно!

## После установки

### SSL сертификат (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-apache
sudo certbot --apache -d videoeditor.1tlt.ru
```

### Настройка файрвола

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Настройка резервного копирования

Создайте скрипт резервного копирования:

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u video_user -p video_overlay > /backup/db_$DATE.sql
tar -czf /backup/storage_$DATE.tar.gz /ssd/www/videoeditor/storage
```

Добавьте в crontab:
```bash
0 2 * * * /path/to/backup.sh
```

## Устранение неполадок

### Воркер не запускается

```bash
sudo systemctl status video-worker
sudo journalctl -u video-worker -n 50
```

### FFmpeg не найден

```bash
which ffmpeg
ffmpeg -version
# Если не найден, установите: sudo apt install ffmpeg
```

### Ошибки прав доступа

```bash
sudo chown -R www-data:www-data /ssd/www/videoeditor/storage
sudo chmod -R 775 /ssd/www/videoeditor/storage
```

### Подключение к базе данных

```bash
mysql -u video_user -p video_overlay
# Проверка подключения
```

### Ошибки Nginx

```bash
sudo apache2ctl configtest
sudo tail -f /var/log/apache2/videoeditor_error.log
sudo tail -f /var/log/apache2/error.log
```

## Чеклист для продакшена

- [ ] Изменен пароль администратора
- [ ] Настроен SSL сертификат
- [ ] Настроен файрвол
- [ ] Настроено резервное копирование
- [ ] Обновлен `config/config.php` с настройками продакшена
- [ ] Установлен `debug` в `false` в конфигурации
- [ ] Настроено доменное имя
- [ ] Протестирована загрузка и обработка видео
- [ ] Проверены логи воркера
- [ ] Настроен мониторинг/оповещения (опционально)
