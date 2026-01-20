# Отладка 404 на /login

## Проблема
Главная страница редиректит на `/login`, но там 404.

## Диагностика

### 1. Проверьте что mod_rewrite включен и работает

```bash
# Проверьте что mod_rewrite включен
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
```

### 3. Проверьте что AllowOverride All настроен

```bash
# Проверьте конфигурацию Apache
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

### 4. Проверьте логи Apache

```bash
# Проверьте логи ошибок
sudo tail -50 /var/log/apache2/videoeditor_ssl_error.log

# Проверьте логи доступа
sudo tail -50 /var/log/apache2/videoeditor_ssl_access.log | grep login
```

### 5. Проверьте что index.php существует и работает

```bash
# Проверьте что index.php существует
ls -la /ssd/www/videoeditor/public/index.php

# Проверьте права
sudo chmod 644 /ssd/www/videoeditor/public/index.php

# Попробуйте открыть напрямую
curl -I https://videoeditor.1tlt.ru/index.php
```

### 6. Проверьте что контроллер существует

```bash
# Проверьте что AuthController существует
ls -la /ssd/www/videoeditor/app/Controllers/AuthController.php

# Проверьте права
sudo chmod 644 /ssd/www/videoeditor/app/Controllers/AuthController.php
```

### 7. Включите отладку в index.php (временно)

Добавьте в начало `public/index.php`:
```php
error_reporting(E_ALL);
ini_set('display_errors', 1);
```

### 8. Проверьте что vendor/autoload.php существует

```bash
# Проверьте что Composer зависимости установлены
ls -la /ssd/www/videoeditor/vendor/autoload.php

# Если нет, установите:
cd /ssd/www/videoeditor
composer install --no-dev --optimize-autoloader
```

## Быстрое исправление

```bash
# 1. Включите mod_rewrite
sudo a2enmod rewrite

# 2. Обновите файлы
cd /ssd/www/videoeditor
git pull origin main

# 3. Установите права
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
sudo tail -50 /var/log/apache2/videoeditor_ssl_error.log
```
