# Настройка PHP-FPM для Apache

## Проверка PHP-FPM

### 1. Проверьте что PHP-FPM установлен и запущен

```bash
# Проверьте статус
sudo systemctl status php8.1-fpm
# или
sudo systemctl status php-fpm

# Если не запущен, запустите:
sudo systemctl start php8.1-fpm
sudo systemctl enable php8.1-fpm
```

### 2. Проверьте конфигурацию PHP-FPM

```bash
# Найдите конфигурационный файл
php-fpm8.1 -i | grep "Loaded Configuration File"
# или
php-fpm -i | grep "Loaded Configuration File"

# Проверьте что PHP-FPM слушает на порту 9000
sudo netstat -tlnp | grep :9000
# или
sudo ss -tlnp | grep :9000
```

### 3. Настройка пула PHP-FPM (если нужно)

```bash
# Отредактируйте конфигурацию пула
sudo nano /etc/php/8.1/fpm/pool.d/www.conf
# или
sudo nano /etc/php8.1/fpm/pool.d/www.conf
```

Убедитесь что:
```ini
listen = 127.0.0.1:9000
# или
listen = /run/php/php8.1-fpm.sock
```

### 4. Перезапустите PHP-FPM

```bash
sudo systemctl restart php8.1-fpm
# или
sudo systemctl restart php-fpm
```

### 5. Проверьте логи PHP-FPM

```bash
# Логи ошибок
sudo tail -f /var/log/php8.1-fpm.log
# или
sudo tail -f /var/log/php-fpm.log

# Логи Apache
sudo tail -f /var/log/apache2/videoeditor_error.log
```

## Устранение проблем

### PHP-FPM не запускается

```bash
# Проверьте конфигурацию
sudo php-fpm8.1 -t
# или
sudo php-fpm -t

# Проверьте права на сокет
ls -la /run/php/
```

### Apache не может подключиться к PHP-FPM

```bash
# Проверьте что PHP-FPM слушает на правильном адресе
sudo netstat -tlnp | grep php-fpm

# Проверьте что модули Apache включены
apache2ctl -M | grep -E "proxy|fcgi"

# Если нет, включите:
sudo a2enmod proxy proxy_fcgi
sudo systemctl restart apache2
```

### Ошибка 502 Bad Gateway

```bash
# Проверьте что PHP-FPM запущен
sudo systemctl status php8.1-fpm

# Проверьте логи
sudo tail -f /var/log/apache2/videoeditor_error.log
sudo tail -f /var/log/php8.1-fpm.log
```
