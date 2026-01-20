# Настройка Apache для videoeditor.1tlt.ru

## Быстрая установка

### 1. Установите Apache и модули

```bash
sudo apt update
sudo apt install -y apache2
sudo a2enmod rewrite proxy proxy_fcgi expires deflate
```

**Примечание:** Используется PHP-FPM через mod_proxy_fcgi, а не mod_php.

### 2. Настройте виртуальный хост

```bash
cd /ssd/www/videoeditor

# Скопируйте конфигурацию
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf

# Отредактируйте (если нужно изменить домен)
sudo nano /etc/apache2/sites-available/videoeditor.conf
# Убедитесь что ServerName: videoeditor.1tlt.ru

# Включите сайт
sudo a2ensite videoeditor.conf

# Отключите сайт по умолчанию (опционально)
sudo a2dissite 000-default.conf

# Проверьте конфигурацию
sudo apache2ctl configtest

# Перезапустите Apache
sudo systemctl restart apache2
```

### 3. Проверьте работу

Откройте в браузере: `http://videoeditor.1tlt.ru`

### 4. Настройте DNS (если нужно)

Убедитесь что домен `videoeditor.1tlt.ru` указывает на IP вашего сервера:
```bash
# Проверьте DNS
nslookup videoeditor.1tlt.ru
# или
dig videoeditor.1tlt.ru
```

### 5. Настройте SSL (опционально, но рекомендуется)

```bash
sudo apt install certbot python3-certbot-apache
sudo certbot --apache -d videoeditor.1tlt.ru
```

## Проверка конфигурации

```bash
# Проверьте что модули включены
apache2ctl -M | grep -E "rewrite|php|expires|deflate"

# Проверьте конфигурацию
sudo apache2ctl configtest

# Проверьте статус
sudo systemctl status apache2

# Проверьте логи
sudo tail -f /var/log/apache2/videoeditor_error.log
```

## Устранение проблем

### Ошибка 403 Forbidden

```bash
# Установите правильные права доступа
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

# Проверьте конфигурацию Apache Directory
sudo grep -A 5 "Directory /ssd/www/videoeditor/public" /etc/apache2/sites-available/videoeditor.conf

# Перезапустите Apache
sudo systemctl restart apache2

# Проверьте логи
sudo tail -30 /var/log/apache2/videoeditor_ssl_error.log
```

### Ошибка 500 Internal Server Error

```bash
# Проверьте логи
sudo tail -f /var/log/apache2/error.log

# Проверьте права на .htaccess
sudo chmod 644 /ssd/www/videoeditor/public/.htaccess
```

### PHP не работает

```bash
# Проверьте что модули proxy и proxy_fcgi включены
apache2ctl -M | grep -E "proxy|fcgi"

# Если нет, включите:
sudo a2enmod proxy proxy_fcgi
sudo systemctl restart apache2

# Проверьте что PHP-FPM запущен
sudo systemctl status php8.1-fpm
# или
sudo systemctl status php-fpm

# Если не запущен, запустите:
sudo systemctl start php8.1-fpm
sudo systemctl enable php8.1-fpm
```

### Домен не открывается

```bash
# Проверьте что сайт включен
apache2ctl -S

# Проверьте что Apache слушает порт 80
sudo netstat -tlnp | grep :80

# Проверьте firewall
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```
