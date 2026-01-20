# Платформа для обработки видео

Автоматизированная платформа для добавления мотивационных призывов к действию (Подписка, Лайк, Заголовок видео) на короткие видео.

## Возможности

- **Управление пользователями**: Регистрация, аутентификация, профили
- **Обработка видео**: Рендеринг наложений на основе FFmpeg
- **Система пресетов**: Переиспользуемые конфигурации наложений
- **Система очередей**: Асинхронная обработка задач
- **Панель администратора**: Полный интерфейс управления
- **Кредитная система**: Оплата по использованию
- **История**: История загрузок и рендеринга

## Требования

- VPS Ubuntu 20.04+
- PHP 8.1+ с расширениями:
  - `php8.1-fpm` - PHP-FPM
  - `php8.1-mysql` - Поддержка MySQL (PDO)
  - `php8.1-mbstring` - Операции со строками
  - `php8.1-gd` - Опционально - Генерация изображений для кнопок наложений (Subscribe/Like). Без GD кнопки используют текстовые наложения.
- MySQL 8.0+
- Apache 2.4+ (или Nginx)
- FFmpeg (установлен и в PATH)
- Git
- Composer

## ⚠️ Важно: PHP расширения

Перед установкой зависимостей Composer убедитесь что установлены необходимые PHP расширения:
```bash
sudo apt install -y php8.1-mbstring php8.1-mysql
php -m | grep -E "mbstring|pdo_mysql"  # Проверка

# Опционально: Установите GD для кнопок наложений
# sudo apt install -y php8.1-gd
```

**Примечание**: Если Composer выдает ошибку о недостающих расширениях, см. `INSTALL_PHP_EXTENSIONS.md`

## Последние обновления

- **2024**: Исправлены зависимости Composer - убраны жесткие требования к расширениям PHP
- **2024**: Добавлено руководство по установке расширений PHP (`INSTALL_PHP_EXTENSIONS.md`)
- **2024**: Добавлены проверки расширений в FFmpegService с понятными сообщениями об ошибках
- Поддержка мультиязычности (Английский, Русский, Тайский, Китайский)
- Репозиторий: https://github.com/alexevil1979/videoeditor
- Путь на сервере: `/ssd/www/videoeditor`

## Установка

### 1. Настройка сервера

```bash
# Установка зависимостей
sudo apt update
sudo apt install -y php8.1-fpm php8.1-mysql php8.1-mbstring apache2 libapache2-mod-php8.1 mysql-server ffmpeg git composer

# Опционально: Установите GD для кнопок наложений
# sudo apt install -y php8.1-gd

# Проверьте установленные расширения PHP
php -m | grep -E "pdo_mysql|mbstring"

# Если расширения отсутствуют, установите их:
# sudo apt install -y php8.1-gd php8.1-mbstring
# sudo systemctl restart php8.1-fpm

# Создание директорий
sudo mkdir -p /ssd/www/videoeditor/{storage/{uploads,renders,logs,cache},public}
sudo chown -R www-data:www-data /ssd/www/videoeditor/storage
```

### 2. Настройка базы данных

```bash
mysql -u root -p
```

```sql
CREATE DATABASE video_overlay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'video_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON video_overlay.* TO 'video_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Настройка приложения

```bash
cd /ssd/www/videoeditor
git clone https://github.com/alexevil1979/videoeditor.git .
composer install --no-dev --optimize-autoloader
cp config/config.example.php config/config.php
# Отредактируйте config.php с учетными данными БД
php scripts/migrate.php
```

### 4. Конфигурация Apache

```bash
# Включите необходимые модули
sudo a2enmod rewrite
sudo a2enmod php8.1
sudo a2enmod expires
sudo a2enmod deflate

# Скопируйте конфигурацию
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf

# Включите сайт
sudo a2ensite videoeditor.conf

# Отключите сайт по умолчанию (опционально)
sudo a2dissite 000-default.conf

# Проверьте конфигурацию
sudo apache2ctl configtest

# Перезапустите Apache
sudo systemctl restart apache2
```

См. `config/apache.conf` для конфигурации виртуального хоста Apache.

### 5. Настройка воркера

```bash
sudo cp scripts/video-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable video-worker
sudo systemctl start video-worker
```

### 6. Права доступа

```bash
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage
```

## Конфигурация

Отредактируйте `config/config.php`:
- Учетные данные базы данных
- Пути хранения
- Настройки FFmpeg
- Ключи безопасности
- Цены на кредиты

## Использование

1. Откройте приложение по адресу `http://your-domain.com`
2. Зарегистрируйте новый аккаунт
3. Загрузите видео
4. Выберите/создайте пресет
5. Обработайте видео
6. Скачайте результат

## Доступ администратора

Учетные данные администратора по умолчанию (измените после первого входа):
- Email: admin@example.com
- Пароль: admin123

## Разработка

```bash
composer install
php scripts/migrate.php
php scripts/worker.php  # Запуск воркера вручную
```

## Документация

- **ARCHITECTURE_RU.md** - Архитектура системы и дизайн
- **INSTALLATION_RU.md** - Подробное руководство по установке
- **DEPLOYMENT_RU.md** - Руководство по развертыванию и CI/CD
- **QUICK_START_RU.md** - Краткий справочник
- **FEATURES_RU.md** - Полный список функций
- **SECURITY_RU.md** - Документация по безопасности
- **PROJECT_STRUCTURE_RU.md** - Организация проекта
- **IMPLEMENTATION_SUMMARY_RU.md** - Обзор реализации
- **INSTALL_PHP_EXTENSIONS.md** - Руководство по установке PHP расширений

## Лицензия

Проприетарная - Все права защищены
