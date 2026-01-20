# Быстрое решение проблемы Composer на сервере

## Проблема
Composer выдает ошибку:
```
Root composer.json requires PHP extension ext-gd * but it is missing from your system.
```

## Решение (выполните на сервере)

```bash
cd /ssd/www/videoeditor

# Вариант 1: Обновить composer.json вручную (если git pull не работает)
# Отредактируйте composer.json и убедитесь что в "require" нет ext-gd

# Вариант 2: Используйте флаги игнорирования
composer install --ignore-platform-req=ext-gd --ignore-platform-req=ext-mbstring --no-dev --optimize-autoloader
```

## После установки зависимостей

**Обязательно установите расширения:**
```bash
# Установите mbstring (обязательно)
sudo apt install -y php-pear php8.1-dev
pecl install mbstring
echo "extension=mbstring.so" >> /usr/local/php8.1/etc/php.ini

# Проверьте
/usr/local/php8.1/bin/php -m | grep mbstring

# Перезапустите PHP-FPM
sudo systemctl restart php8.1-fpm
```

**Опционально установите GD (для красивых кнопок):**
```bash
sudo apt install -y libpng-dev libjpeg-dev libfreetype6-dev
pecl install gd
echo "extension=gd.so" >> /usr/local/php8.1/etc/php.ini
/usr/local/php8.1/bin/php -m | grep gd
sudo systemctl restart php8.1-fpm
```

## Проверка

```bash
# Проверьте обязательные расширения
/usr/local/php8.1/bin/php -m | grep -E "mbstring|pdo_mysql"

# Должны быть:
# mbstring
# pdo_mysql
```
