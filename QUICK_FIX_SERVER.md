# Быстрое решение для сервера

## Проблема
Composer выдает ошибку о недостающем расширении на сервере с кастомным PHP.

## Решение 1: Обновить composer.json (рекомендуется)

```bash
cd /ssd/www/videoeditor
git pull origin main
composer install --no-dev --optimize-autoloader
```

## Решение 2: Временный обход (если git pull не работает)

```bash
cd /ssd/www/videoeditor

# Установите зависимости, игнорируя требования к расширениям
composer install --ignore-platform-req=ext-gd --ignore-platform-req=ext-mbstring --no-dev --optimize-autoloader
```

**Примечание**: Если вы только что клонировали репозиторий, возможно изменения еще не запушены. Используйте флаги игнорирования.

**⚠️ ВАЖНО**: После этого обязательно установите расширения PHP!
- `mbstring` - обязательно для работы приложения
- `pdo_mysql` - обязательно для работы с БД
- `gd` - опционально, для красивых кнопок (без GD кнопки будут текстовыми)

## Решение 3: Установить расширения для кастомного PHP

### Обязательные расширения:

```bash
# Установите зависимости для компиляции
sudo apt update
sudo apt install -y php-pear php8.1-dev

# Установите mbstring через PECL
pecl install mbstring

# Добавьте в php.ini
echo "extension=mbstring.so" >> /usr/local/php8.1/etc/php.ini

# Проверьте
/usr/local/php8.1/bin/php -m | grep mbstring

# Перезапустите PHP-FPM
sudo systemctl restart php8.1-fpm

# Теперь установите зависимости
composer install --no-dev --optimize-autoloader
```

### Опционально: GD для кнопок наложений

```bash
# Установите зависимости для компиляции GD
sudo apt install -y libpng-dev libjpeg-dev libfreetype6-dev

# Установите GD через PECL
pecl install gd

# Добавьте в php.ini
echo "extension=gd.so" >> /usr/local/php8.1/etc/php.ini

# Проверьте
/usr/local/php8.1/bin/php -m | grep gd

# Перезапустите PHP-FPM
sudo systemctl restart php8.1-fpm
```

**Примечание**: Без GD приложение работает, но кнопки Subscribe/Like будут текстовыми наложениями вместо цветных изображений.

## Проверка после установки

```bash
# Проверьте обязательные расширения
/usr/local/php8.1/bin/php -m | grep -E "mbstring|pdo_mysql"

# Должны быть видны:
# mbstring
# pdo_mysql

# Проверьте опциональное расширение
/usr/local/php8.1/bin/php -m | grep gd
# Если установлено, будет видно: gd
```

## Минимальные требования

Для работы приложения **обязательно** нужны:
- ✅ `mbstring` - для работы со строками
- ✅ `pdo_mysql` - для работы с базой данных

**Опционально**:
- ⚪ `gd` - для генерации изображений кнопок (без GD кнопки будут текстовыми)

## Быстрый старт (минимум)

```bash
# 1. Установите только mbstring (pdo_mysql обычно уже есть)
sudo apt install -y php-pear php8.1-dev
pecl install mbstring
echo "extension=mbstring.so" >> /usr/local/php8.1/etc/php.ini

# 2. Установите зависимости
cd /ssd/www/videoeditor
composer install --no-dev --optimize-autoloader

# 3. Готово! Приложение работает, кнопки будут текстовыми
```
