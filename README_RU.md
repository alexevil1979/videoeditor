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
- PHP 8.1+ с расширениями: pdo_mysql, gd, mbstring, zip
- MySQL 8.0+
- Nginx
- FFmpeg (установлен и в PATH)
- Git
- Composer

## Установка

### 1. Настройка сервера

```bash
# Установка зависимостей
sudo apt update
sudo apt install -y php8.1-fpm php8.1-mysql php8.1-gd php8.1-mbstring php8.1-zip nginx mysql-server ffmpeg git composer

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

### 4. Конфигурация Nginx

См. `config/nginx.conf` для конфигурации виртуального хоста Nginx.

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

## Лицензия

Проприетарная - Все права защищены
