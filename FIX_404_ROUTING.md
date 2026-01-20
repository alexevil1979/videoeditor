# Исправление ошибки 404 на маршрутах

## Проблема
Ошибка 404 на маршрутах типа `/login`, `/register` и т.д.

## Причины
1. mod_rewrite не включен
2. .htaccess не работает (AllowOverride не настроен)
3. index.php не существует или неправильный путь
4. Проблемы с правами доступа к .htaccess

## Решение

### 1. Проверьте что mod_rewrite включен

```bash
# Проверьте включен ли mod_rewrite
apache2ctl -M | grep rewrite

# Если нет, включите:
sudo a2enmod rewrite
sudo systemctl restart apache2
```

### 2. Проверьте .htaccess

```bash
# Проверьте что .htaccess существует
ls -la /ssd/www/videoeditor/public/.htaccess

# Проверьте содержимое
cat /ssd/www/videoeditor/public/.htaccess

# Проверьте права
sudo chmod 644 /ssd/www/videoeditor/public/.htaccess
sudo chown www-data:www-data /ssd/www/videoeditor/public/.htaccess
```

### 3. Проверьте index.php

```bash
# Проверьте что index.php существует
ls -la /ssd/www/videoeditor/public/index.php

# Проверьте права
sudo chmod 644 /ssd/www/videoeditor/public/index.php
sudo chown www-data:www-data /ssd/www/videoeditor/public/index.php
```

### 4. Проверьте конфигурацию Apache

```bash
# Проверьте что AllowOverride All настроен
sudo grep -A 5 "Directory /ssd/www/videoeditor/public" /etc/apache2/sites-available/videoeditor.conf
```

Должно быть:
```apache
<Directory /ssd/www/videoeditor/public>
    Options -Indexes +FollowSymLinks
    AllowOverride All
    Require all granted
</Directory>
```

### 5. Проверьте логи Apache

```bash
# Проверьте логи ошибок
sudo tail -50 /var/log/apache2/videoeditor_ssl_error.log
sudo tail -50 /var/log/apache2/error.log
```

### 6. Перезапустите Apache

```bash
sudo systemctl restart apache2
sudo systemctl status apache2
```

### 7. Проверьте что файлы из репозитория на месте

```bash
cd /ssd/www/videoeditor
git pull origin main
ls -la public/
ls -la public/index.php
ls -la public/.htaccess
```

## Быстрое исправление (все команды сразу)

```bash
# 1. Включите mod_rewrite
sudo a2enmod rewrite

# 2. Обновите файлы из репозитория
cd /ssd/www/videoeditor
git pull origin main

# 3. Установите правильные права
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod 644 /ssd/www/videoeditor/public/.htaccess
sudo chmod 644 /ssd/www/videoeditor/public/index.php

# 4. Обновите конфигурацию Apache
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf

# 5. Проверьте конфигурацию
sudo apache2ctl configtest

# 6. Перезапустите Apache
sudo systemctl restart apache2

# 7. Проверьте логи
sudo tail -30 /var/log/apache2/videoeditor_ssl_error.log

# 8. Проверьте в браузере
# https://videoeditor.1tlt.ru/login
```
