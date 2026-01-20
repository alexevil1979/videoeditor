# Исправление ошибки 403 Forbidden

## Проблема
Ошибка "Forbidden - You don't have permission to access this resource" на HTTPS.

## Причины
1. Неправильные права доступа к файлам
2. Неправильный владелец файлов
3. Неправильная конфигурация Apache Directory
4. SELinux/AppArmor блокирует доступ

## Решение

### 1. Проверьте права доступа

```bash
# Проверьте текущие права
ls -la /ssd/www/videoeditor/public
ls -la /ssd/www/videoeditor

# Установите правильные права
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage
sudo chmod -R 755 /ssd/www/videoeditor/public
```

### 2. Проверьте конфигурацию Apache

```bash
# Проверьте конфигурацию
sudo apache2ctl configtest

# Проверьте что Directory настроен правильно
sudo grep -A 10 "Directory /ssd/www/videoeditor/public" /etc/apache2/sites-available/videoeditor.conf
```

Должно быть:
```apache
<Directory /ssd/www/videoeditor/public>
    Options -Indexes +FollowSymLinks
    AllowOverride All
    Require all granted
</Directory>
```

### 3. Проверьте .htaccess

```bash
# Проверьте что .htaccess существует
ls -la /ssd/www/videoeditor/public/.htaccess

# Проверьте права на .htaccess
sudo chmod 644 /ssd/www/videoeditor/public/.htaccess
```

### 4. Проверьте index.php

```bash
# Проверьте что index.php существует
ls -la /ssd/www/videoeditor/public/index.php

# Проверьте права
sudo chmod 644 /ssd/www/videoeditor/public/index.php
```

### 5. Проверьте логи Apache

```bash
# Проверьте логи ошибок
sudo tail -50 /var/log/apache2/videoeditor_ssl_error.log
sudo tail -50 /var/log/apache2/error.log

# Проверьте логи доступа
sudo tail -50 /var/log/apache2/videoeditor_ssl_access.log
```

### 6. Проверьте SELinux/AppArmor (если включен)

```bash
# Проверьте статус AppArmor
sudo aa-status

# Если AppArmor включен, добавьте исключение для Apache
sudo nano /etc/apparmor.d/usr.sbin.apache2
```

### 7. Перезапустите Apache

```bash
sudo systemctl restart apache2
sudo systemctl status apache2
```

### 8. Проверьте PHP-FPM

```bash
# Проверьте что PHP-FPM запущен
sudo systemctl status php8.1-fpm

# Проверьте права на сокет PHP-FPM
ls -la /run/php/
```

## Быстрое исправление (все команды сразу)

```bash
# Установите права
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage
sudo chmod -R 755 /ssd/www/videoeditor/public

# Проверьте конфигурацию
sudo apache2ctl configtest

# Перезапустите сервисы
sudo systemctl restart apache2
sudo systemctl restart php8.1-fpm

# Проверьте логи
sudo tail -20 /var/log/apache2/videoeditor_ssl_error.log
```
