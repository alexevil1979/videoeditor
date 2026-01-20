# Установка PHP расширений

## Проблема

Composer выдает ошибку о недостающих PHP расширениях:
```
Root composer.json requires PHP extension ext-mbstring * but it is missing from your system.
```

## Обязательные расширения

Для работы приложения **обязательно** нужны:
- `mbstring` - для работы со строками
- `pdo_mysql` - для работы с базой данных

## Опциональные расширения

- `gd` - для генерации изображений кнопок Subscribe/Like. Без GD кнопки будут текстовыми наложениями.

## Решение

### Ubuntu/Debian (стандартная установка PHP)

```bash
# Установите все необходимые расширения
sudo apt update
sudo apt install -y php8.1-mbstring php8.1-mysql

# Опционально: Установите GD для кнопок наложений
# sudo apt install -y php8.1-gd

# Проверьте установленные расширения
php -m | grep -E "mbstring|pdo_mysql"

# Перезапустите PHP-FPM
sudo systemctl restart php8.1-fpm
```

### Кастомная установка PHP (из исходников, /usr/local/php8.1)

Если PHP установлен из исходников в `/usr/local/php8.1`:

#### Обязательные расширения:

```bash
# 1. Установите зависимости для компиляции
sudo apt update
sudo apt install -y php-pear php8.1-dev

# 2. Установите mbstring через PECL
pecl install mbstring

# 3. Добавьте в php.ini
echo "extension=mbstring.so" >> /usr/local/php8.1/etc/php.ini

# 4. Проверьте
/usr/local/php8.1/bin/php -m | grep mbstring

# 5. Перезапустите PHP-FPM
sudo systemctl restart php8.1-fpm
```

#### Опционально: GD для кнопок наложений

```bash
# 1. Установите зависимости для компиляции GD
sudo apt install -y libpng-dev libjpeg-dev libfreetype6-dev

# 2. Установите GD через PECL
pecl install gd

# 3. Добавьте в php.ini
echo "extension=gd.so" >> /usr/local/php8.1/etc/php.ini

# 4. Проверьте
/usr/local/php8.1/bin/php -m | grep gd

# 5. Перезапустите PHP-FPM
sudo systemctl restart php8.1-fpm
```

**Примечание**: Без GD приложение работает, но кнопки Subscribe/Like будут текстовыми наложениями.

**Альтернатива**: Если пересборка сложна, можно временно использовать флаг:
```bash
composer install --ignore-platform-req=ext-mbstring
```
⚠️ Внимание: mbstring обязательно нужен для работы приложения! GD опционален - без него кнопки будут текстовыми.

### Проверка расширений

```bash
# Список всех установленных расширений
php -m

# Проверка конкретных расширений
php -m | grep mbstring
php -m | grep pdo_mysql
# Опционально:
# php -m | grep gd
```

### Если расширения не найдены после установки

```bash
# Найдите файл php.ini
php --ini

# Отредактируйте php.ini и раскомментируйте расширения:
# extension=mbstring
# extension=pdo_mysql
# extension=gd (опционально)

# Или создайте отдельные файлы конфигурации:
sudo nano /etc/php/8.1/mods-available/gd.ini
# Добавьте: extension=gd.so

# Включите расширения
sudo phpenmod mbstring pdo_mysql
# Опционально:
# sudo phpenmod gd

# Перезапустите PHP-FPM
sudo systemctl restart php8.1-fpm
```


### Альтернативный способ (временный обход)

Если нужно срочно установить зависимости без расширений:

```bash
# Вариант 1: Обновите composer.json на сервере (git pull)
cd /ssd/www/videoeditor
git pull origin main

# Вариант 2: Используйте флаг игнорирования
composer install --ignore-platform-req=ext-mbstring --no-dev --optimize-autoloader
```

**⚠️ Внимание**: Это временное решение. Расширения все равно нужны для работы приложения:
- `mbstring` - для работы со строками (обязательно)
- `pdo_mysql` - для работы с базой данных (обязательно)
- `gd` - для генерации изображений кнопок (Subscribe, Like) - опционально, без GD кнопки будут текстовыми

## После установки расширений

```bash
# Установите зависимости Composer
composer install --no-dev --optimize-autoloader

# Проверьте что все работает
php -r "var_dump(extension_loaded('mbstring'));"
php -r "var_dump(extension_loaded('pdo_mysql'));"
# Опционально:
# php -r "var_dump(extension_loaded('gd'));"
```

Все должно вернуть `bool(true)`.
