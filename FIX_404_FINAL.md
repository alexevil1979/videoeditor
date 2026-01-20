# Финальное исправление 404 ошибки

## Проблема
404 ошибка на всех маршрутах (например `/login`).

## Возможные причины

1. **.htaccess не применяется** - AllowOverride не настроен
2. **mod_rewrite не работает** - модуль не включен или не работает
3. **Запрос не доходит до index.php** - проблема с маршрутизацией
4. **Неправильный DocumentRoot** - Apache ищет файлы не там

## Пошаговая диагностика и исправление

### Шаг 1: Проверьте что mod_rewrite включен

```bash
# На сервере:
apache2ctl -M | grep rewrite

# Если нет, включите:
sudo a2enmod rewrite
sudo systemctl restart apache2
```

### Шаг 2: Проверьте конфигурацию Apache

```bash
# Проверьте что AllowOverride All настроен
sudo grep -A 5 "Directory /ssd/www/videoeditor/public" /etc/apache2/sites-available/videoeditor.conf

# Должно быть:
# <Directory /ssd/www/videoeditor/public>
#     Options -Indexes +FollowSymLinks
#     AllowOverride All
#     Require all granted
# </Directory>
```

### Шаг 3: Проверьте .htaccess

```bash
# Проверьте что файл существует
ls -la /ssd/www/videoeditor/public/.htaccess

# Проверьте содержимое
cat /ssd/www/videoeditor/public/.htaccess

# Проверьте права
sudo chmod 644 /ssd/www/videoeditor/public/.htaccess
sudo chown www-data:www-data /ssd/www/videoeditor/public/.htaccess
```

### Шаг 4: Создайте тестовый файл

```bash
# Создайте простой тест
sudo tee /ssd/www/videoeditor/public/test.php << 'EOF'
<?php
echo "TEST OK\n";
echo "REQUEST_URI: " . ($_SERVER['REQUEST_URI'] ?? 'NOT SET') . "\n";
echo "SCRIPT_NAME: " . ($_SERVER['SCRIPT_NAME'] ?? 'NOT SET') . "\n";
echo "DOCUMENT_ROOT: " . ($_SERVER['DOCUMENT_ROOT'] ?? 'NOT SET') . "\n";
phpinfo();
EOF

sudo chmod 644 /ssd/www/videoeditor/public/test.php
sudo chown www-data:www-data /ssd/www/videoeditor/public/test.php
```

Откройте: `https://videoeditor.1tlt.ru/test.php`

### Шаг 5: Проверьте что index.php работает напрямую

Откройте: `https://videoeditor.1tlt.ru/index.php`

Если работает - проблема в .htaccess  
Если не работает - проблема с PHP-FPM или конфигурацией

### Шаг 6: Проверьте логи

```bash
# Логи Apache
sudo tail -50 /var/log/apache2/videoeditor_ssl_error.log
sudo tail -50 /var/log/apache2/error.log

# Логи PHP (если файл создан)
tail -50 /ssd/www/videoeditor/storage/logs/php_errors.log 2>/dev/null || echo "Лог файл не создан"
```

### Шаг 7: Включите отладку rewrite в Apache

Временно добавьте в `/etc/apache2/sites-available/videoeditor.conf`:

```apache
<Directory /ssd/www/videoeditor/public>
    Options -Indexes +FollowSymLinks
    AllowOverride All
    Require all granted
    LogLevel rewrite:trace3
</Directory>
```

```bash
sudo systemctl restart apache2
# Проверьте логи
sudo tail -100 /var/log/apache2/videoeditor_ssl_error.log | grep rewrite
```

## Быстрое исправление (все команды сразу)

```bash
# 1. Включите mod_rewrite
sudo a2enmod rewrite

# 2. Обновите конфигурацию Apache
cd /ssd/www/videoeditor
git pull origin main
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf

# 3. Установите права
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod 644 /ssd/www/videoeditor/public/.htaccess
sudo chmod 644 /ssd/www/videoeditor/public/index.php

# 4. Проверьте конфигурацию
sudo apache2ctl configtest

# 5. Перезапустите Apache
sudo systemctl restart apache2

# 6. Проверьте что mod_rewrite включен
apache2ctl -M | grep rewrite

# 7. Проверьте логи
sudo tail -50 /var/log/apache2/videoeditor_ssl_error.log
```

## Альтернативное решение: FallbackResource

Если mod_rewrite не работает, можно использовать FallbackResource:

```apache
# В .htaccess или в Apache конфигурации:
FallbackResource /index.php
```

Это автоматически перенаправит все несуществующие файлы на index.php.
