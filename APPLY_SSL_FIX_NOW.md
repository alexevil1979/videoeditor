# Применение исправления SSL на сервере

## Проблема
Certbot получил сертификат, но не смог автоматически настроить Apache.

**Почему это происходит:**
Certbot может автоматически настроить Apache только если в конфигурации есть только HTTP VirtualHost (порт 80). Когда в конфигурации уже есть оба VirtualHost (HTTP и HTTPS), certbot не может их сопоставить и выдает ошибку "Could not reverse map the HTTPS VirtualHost to the original".

**Решение:** Настроить Apache вручную, используя готовую конфигурацию из репозитория.

## Решение

### 1. Включите необходимые модули Apache

```bash
sudo a2enmod ssl
sudo a2enmod rewrite
sudo a2enmod proxy
sudo a2enmod proxy_fcgi
```

### 2. Обновите конфигурацию Apache

```bash
cd /ssd/www/videoeditor
git pull origin main
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf
```

### 3. Проверьте конфигурацию

```bash
sudo apache2ctl configtest
```

Должно быть: `Syntax OK`

### 4. Перезапустите Apache

```bash
sudo systemctl restart apache2
```

### 5. Проверьте статус

```bash
sudo systemctl status apache2
```

### 6. Проверьте SSL сертификат

```bash
sudo certbot certificates
```

### 7. Установите правильные права доступа

```bash
# Установите владельца и права
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage
sudo chmod -R 755 /ssd/www/videoeditor/public

# Проверьте что index.php существует
ls -la /ssd/www/videoeditor/public/index.php
sudo chmod 644 /ssd/www/videoeditor/public/index.php

# Проверьте .htaccess
ls -la /ssd/www/videoeditor/public/.htaccess
sudo chmod 644 /ssd/www/videoeditor/public/.htaccess
```

### 8. Проверьте PHP-FPM

```bash
# Проверьте что PHP-FPM запущен
sudo systemctl status php8.1-fpm
# или
sudo systemctl status php-fpm

# Если не запущен, запустите:
sudo systemctl start php8.1-fpm
sudo systemctl enable php8.1-fpm
```

### 9. Обновите config.php для HTTPS

```bash
cd /ssd/www/videoeditor
nano config/config.php
```

Измените:
```php
'url' => 'https://videoeditor.1tlt.ru',
```

### 10. Проверьте логи (если все еще 403)

```bash
# Проверьте логи ошибок
sudo tail -50 /var/log/apache2/videoeditor_ssl_error.log
sudo tail -50 /var/log/apache2/error.log
```

### 11. Проверьте в браузере

Откройте: `https://videoeditor.1tlt.ru`

Должен быть зеленый замочек и HTTPS соединение.

### 12. Проверьте редирект HTTP -> HTTPS

Откройте: `http://videoeditor.1tlt.ru`

Должен автоматически перенаправить на HTTPS.
