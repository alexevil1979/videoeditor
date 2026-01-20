# Обновление composer.json на сервере

## Проблема
На сервере старая версия composer.json где GD в require, а не в suggest.

## Решение

### Вариант 1: Обновить через git pull (если изменения уже запушены)

```bash
cd /ssd/www/videoeditor
git config --global --add safe.directory /ssd/www/videoeditor
git pull origin main
composer install --no-dev --optimize-autoloader
```

### Вариант 2: Использовать флаг игнорирования (временно)

```bash
cd /ssd/www/videoeditor
composer install --ignore-platform-req=ext-gd --ignore-platform-req=ext-mbstring --no-dev --optimize-autoloader
```

После этого обязательно установите mbstring:
```bash
sudo apt install -y php-pear php8.1-dev
pecl install mbstring
echo "extension=mbstring.so" >> /usr/local/php8.1/etc/php.ini
sudo systemctl restart php8.1-fpm
```

### Вариант 3: Обновить composer.json вручную на сервере

```bash
cd /ssd/www/videoeditor
nano composer.json
```

Измените:
```json
{
    "require": {
        "php": ">=8.1"
    },
    "suggest": {
        "ext-pdo": "Required for database operations",
        "ext-json": "Required for JSON handling",
        "ext-mbstring": "Required for string operations",
        "ext-gd": "Optional - for generating image overlay buttons (Subscribe/Like). Without GD, buttons will use text overlays instead."
    }
}
```

Затем:
```bash
composer install --no-dev --optimize-autoloader
```

## Рекомендуемое решение

1. Сначала запушьте обновленный composer.json с локальной машины
2. Затем на сервере сделайте git pull
3. Установите зависимости
