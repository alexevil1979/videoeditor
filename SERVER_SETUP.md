# Быстрая настройка на сервере

## Если PHP установлен из исходников (/usr/local/php8.1)

### 1. Установите обязательные расширения PHP

```bash
# Установите зависимости для компиляции
sudo apt update
sudo apt install -y php-pear php8.1-dev

# Установите mbstring через PECL (если нужно)
pecl install mbstring

# Добавьте в php.ini
echo "extension=mbstring.so" >> /usr/local/php8.1/etc/php.ini

# Проверьте
/usr/local/php8.1/bin/php -m | grep -E "mbstring|pdo_mysql"
```

### 2. Опционально: Установите GD для кнопок наложений

```bash
# Установите зависимости для компиляции GD
sudo apt install -y libpng-dev libjpeg-dev libfreetype6-dev

# Установите GD через PECL
pecl install gd

# Добавьте в php.ini
echo "extension=gd.so" >> /usr/local/php8.1/etc/php.ini

# Проверьте
/usr/local/php8.1/bin/php -m | grep gd
```

**Примечание**: Без GD кнопки Subscribe/Like будут текстовыми наложениями вместо изображений. Это работает, но выглядит проще.

### 3. Временное решение (если расширения установить сложно)

```bash
# Обновите composer.json на сервере (убрать требования к расширениям)
cd /ssd/www/videoeditor
git pull origin main

# Или используйте флаг:
composer install --ignore-platform-req=ext-mbstring --no-dev --optimize-autoloader
```

**⚠️ ВАЖНО**: Расширение mbstring обязательно нужно для работы приложения! Это только для установки зависимостей Composer.

### 4. После установки зависимостей

```bash
# Обязательные расширения:
# - mbstring - для работы со строками
# - pdo_mysql - для работы с БД

# Опциональные расширения:
# - gd - для генерации изображений кнопок (без GD кнопки будут текстовыми)
```

## Проверка расширений

```bash
# Проверьте какие расширения загружены
/usr/local/php8.1/bin/php -m

# Проверьте обязательные расширения
/usr/local/php8.1/bin/php -m | grep mbstring
/usr/local/php8.1/bin/php -m | grep pdo_mysql

# Проверьте опциональное расширение
/usr/local/php8.1/bin/php -m | grep gd
```

## Если расширения не загружаются

```bash
# Проверьте php.ini
/usr/local/php8.1/bin/php --ini

# Отредактируйте php.ini
nano /usr/local/php8.1/etc/php.ini

# Добавьте расширения:
# extension=mbstring.so
# extension=pdo_mysql.so
# extension=gd.so (опционально)

# Или добавьте пути к .so файлам:
# extension=/usr/local/php8.1/lib/php/extensions/no-debug-non-zts-20210902/mbstring.so
# extension=/usr/local/php8.1/lib/php/extensions/no-debug-non-zts-20210902/pdo_mysql.so
# extension=/usr/local/php8.1/lib/php/extensions/no-debug-non-zts-20210902/gd.so
```

## Минимальная установка (без GD)

```bash
# 1. Установите только обязательные расширения
sudo apt install -y php-pear php8.1-dev
pecl install mbstring
echo "extension=mbstring.so" >> /usr/local/php8.1/etc/php.1/etc/php.ini

# 2. Установите зависимости Composer
cd /ssd/www/videoeditor
composer install --no-dev --optimize-autoloader

# 3. Приложение будет работать, но кнопки Subscribe/Like будут текстовыми
```

## Полная установка (с GD для красивых кнопок)

```bash
# 1. Установите все расширения
sudo apt install -y libpng-dev libjpeg-dev libfreetype6-dev php-pear php8.1-dev
pecl install mbstring gd
echo "extension=mbstring.so" >> /usr/local/php8.1/etc/php.ini
echo "extension=gd.so" >> /usr/local/php8.1/etc/php.ini

# 2. Установите зависимости Composer
cd /ssd/www/videoeditor
composer install --no-dev --optimize-autoloader

# 3. Кнопки будут цветными изображениями
```
