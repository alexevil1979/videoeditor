# Руководство по развертыванию

## Первоначальная настройка сервера

### 1. Установка зависимостей

```bash
sudo apt update
sudo apt install -y php8.1-fpm php8.1-mysql php8.1-mbstring apache2 libapache2-mod-php8.1 mysql-server ffmpeg git composer

# Опционально: Установите GD для кнопок наложений
# sudo apt install -y php8.1-gd
```

### 2. Настройка MySQL

```bash
sudo mysql_secure_installation
```

Создайте базу данных и пользователя:
```sql
CREATE DATABASE video_overlay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'video_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON video_overlay.* TO 'video_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Клонирование репозитория

```bash
cd /ssd/www
sudo git clone https://github.com/alexevil1979/videoeditor.git videoeditor
sudo chown -R www-data:www-data videoeditor
cd videoeditor
```

### 4. Установка PHP зависимостей

```bash
composer install --no-dev --optimize-autoloader
```

### 5. Конфигурация приложения

```bash
cp config/config.example.php config/config.php
# Отредактируйте config/config.php с вашими учетными данными базы данных
```

### 6. Запуск миграций базы данных

```bash
php scripts/migrate.php
```

### 7. Установка прав доступа

```bash
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage
```

### 8. Конфигурация Apache

```bash
sudo a2enmod rewrite php8.1 expires deflate
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf
sudo nano /etc/apache2/sites-available/videoeditor.conf  # Обновите ServerName на videoeditor.1tlt.ru
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

## Настройка CI/CD

### GitHub Actions

1. Добавьте секреты в репозиторий GitHub:
   - `SSH_HOST`: IP вашего сервера или домен
   - `SSH_USER`: Имя пользователя SSH (обычно `root` или `ubuntu`)
   - `SSH_KEY`: Приватный SSH ключ для развертывания

2. Push в ветку `main` запускает автоматическое развертывание

### Ручное развертывание

```bash
cd /ssd/www/videoeditor
bash scripts/deploy.sh
```

## После развертывания

1. **Измените пароль администратора**: Войдите с учетными данными по умолчанию и измените немедленно
2. **Настройте домен**: Обновите конфигурацию Apache с доменным именем (videoeditor.1tlt.ru)
3. **SSL сертификат**: Установите сертификат Let's Encrypt
4. **Файрвол**: Настройте UFW для разрешения только необходимых портов
5. **Резервное копирование**: Настройте автоматическое резервное копирование базы данных и хранилища

## Мониторинг

- Проверка статуса воркера: `sudo systemctl status video-worker`
- Просмотр логов воркера: `sudo journalctl -u video-worker -f`
- Проверка логов Apache: `sudo tail -f /var/log/apache2/videoeditor_error.log`
- Мониторинг очереди: Проверьте панель администратора

## Устранение неполадок

### Воркер не обрабатывает задачи
- Проверьте статус воркера: `sudo systemctl status video-worker`
- Проверьте логи: `sudo journalctl -u video-worker -n 50`
- Проверьте FFmpeg: `which ffmpeg`
- Проверьте права доступа к директориям хранилища

### Сбои загрузки
- Проверьте `LimitRequestBody` в config/apache.conf
- Проверьте `upload_max_filesize` и `post_max_size` в PHP
- Проверьте права доступа к директории хранилища

### Ошибки подключения к базе данных
- Проверьте учетные данные в `config/config.php`
- Проверьте сервис MySQL: `sudo systemctl status mysql`
- Проверьте подключение: `mysql -u video_user -p video_overlay`
