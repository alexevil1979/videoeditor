# Краткое руководство

## Репозиторий
- **GitHub**: https://github.com/alexevil1979/videoeditor
- **Путь на сервере**: `/ssd/www/videoeditor`

## ⚠️ Важно: PHP расширения

Перед установкой зависимостей Composer убедитесь что установлены **обязательные** PHP расширения:
```bash
# Обязательные расширения
sudo apt install -y php8.1-mbstring php8.1-mysql
php -m | grep -E "mbstring|pdo_mysql"  # Проверка

# Опционально: GD для красивых кнопок наложений
# sudo apt install -y php8.1-gd
# php -m | grep gd

sudo systemctl restart php8.1-fpm  # Перезапустите PHP-FPM
```

**Примечание**: Без GD приложение работает, но кнопки Subscribe/Like будут текстовыми вместо изображений.

Если Composer выдает ошибку о недостающих расширениях, см. `INSTALL_PHP_EXTENSIONS.md`

## Для разработчиков

### Настройка локальной разработки

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/alexevil1979/videoeditor.git
   cd videoeditor
   ```

2. **Установите зависимости:**
   ```bash
   composer install
   ```

3. **Настройте конфигурацию:**
   ```bash
   cp config/config.example.php config/config.php
   # Отредактируйте config/config.php (база данных, пути и т.д.)
   ```

4. **Настройте базу данных:**
   ```bash
   # Создайте базу данных в MySQL
   mysql -u root -p
   # CREATE DATABASE video_overlay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   # CREATE USER 'video_user'@'localhost' IDENTIFIED BY 'your_password';
   # GRANT ALL PRIVILEGES ON video_overlay.* TO 'video_user'@'localhost';
   # FLUSH PRIVILEGES;
   
   # Запустите миграции
   php scripts/migrate.php
   ```

5. **Запустите встроенный сервер PHP:**
   ```bash
   php -S localhost:8000 -t public
   ```

6. **Запустите воркер (отдельный терминал):**
   ```bash
   php scripts/worker.php
   ```

7. **Доступ:**
   - Приложение: http://localhost:8000
   - Админ: admin@example.com / admin123
   - ⚠️ **ВАЖНО**: Измените пароль администратора после первого входа!

## Для развертывания в продакшене

### Быстрая установка на VPS (Ubuntu)

```bash
# 1. Установите зависимости
sudo apt update
sudo apt install -y php8.1-fpm php8.1-mysql php8.1-mbstring apache2 libapache2-mod-php8.1 mysql-server ffmpeg git composer

# Опционально: Установите GD для кнопок наложений
# sudo apt install -y php8.1-gd

# Проверьте установленные расширения PHP
php -m | grep -E "pdo_mysql|mbstring"

# Если расширения отсутствуют, установите их:
# sudo apt install -y php8.1-mbstring
# sudo systemctl restart php8.1-fpm

# 2. Клонируйте репозиторий
cd /ssd/www
git clone https://github.com/alexevil1979/videoeditor.git videoeditor
cd videoeditor

# 3. Установите PHP зависимости
composer install --no-dev --optimize-autoloader

# 4. Настройте конфигурацию
cp config/config.example.php config/config.php
nano config/config.php  # Отредактируйте настройки БД и пути

# 5. Настройте базу данных
mysql -u root -p
# CREATE DATABASE video_overlay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# CREATE USER 'video_user'@'localhost' IDENTIFIED BY 'your_password';
# GRANT ALL PRIVILEGES ON video_overlay.* TO 'video_user'@'localhost';
# FLUSH PRIVILEGES;

# 6. Настройте базу данных
# Создайте БД в MySQL (если еще не создана):
# mysql -u root -p
# CREATE DATABASE video_overlay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# CREATE USER 'video_user'@'localhost' IDENTIFIED BY 'your_password';
# GRANT ALL PRIVILEGES ON video_overlay.* TO 'video_user'@'localhost';
# FLUSH PRIVILEGES;

# Настройте config.php
cp config/config.example.php config/config.php
nano config/config.php  # Укажите данные БД

# Запустите миграции
php scripts/migrate.php

# 7. Установите права доступа
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage

# 8. Настройте Apache
sudo a2enmod rewrite php8.1 expires deflate
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf
sudo nano /etc/apache2/sites-available/videoeditor.conf  # Обновите ServerName на videoeditor.1tlt.ru
sudo a2ensite videoeditor.conf
sudo a2dissite 000-default.conf  # Опционально: отключите сайт по умолчанию
sudo apache2ctl configtest
sudo systemctl restart apache2

# 9. Настройте воркер
sudo cp scripts/video-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable video-worker
sudo systemctl start video-worker
sudo systemctl status video-worker

# 10. Готово! Откройте ваш домен в браузере
```

## Ключевые URL

- `/` - Главная (перенаправляет на логин/дашборд)
- `/login` - Вход пользователя
- `/register` - Регистрация пользователя
- `/dashboard` - Панель пользователя
- `/admin` - Панель администратора
- `/lang/{code}` - Переключение языка (en, ru, th, zh)
- `/api/videos/upload` - Загрузка видео (POST)
- `/api/videos/render` - Создание задачи рендеринга (POST)
- `/api/videos/download/{id}` - Скачать обработанное видео
- `/api/presets` - Управление пресетами

## Учетные данные по умолчанию

**Администратор:**
- Email: `admin@example.com`
- Пароль: `admin123`

**⚠️ ИЗМЕНИТЕ НЕМЕДЛЕННО ПОСЛЕ ПЕРВОГО ВХОДА!**

## Частые задачи

### Добавить кредиты пользователю
1. Войдите как администратор
2. Перейдите в Админ → Пользователи
3. Нажмите "Изменить баланс"
4. Введите сумму (положительную для добавления, отрицательную для вычитания)

### Создать пресет
Используйте API или добавьте напрямую в базу данных:
```sql
INSERT INTO presets (user_id, name, is_global) VALUES (NULL, 'Мой пресет', 1);
INSERT INTO preset_items (preset_id, type, position_x, position_y, text) 
VALUES (LAST_INSERT_ID(), 'title', 'center', 'top', 'Мой заголовок видео');
```

### Переключить язык интерфейса
- Используйте выпадающий список в правом верхнем углу навигации
- Или перейдите по URL: `/lang/ru` (en, ru, th, zh)
- Язык сохранится в сессии и профиле пользователя

### Проверить статус очереди
```bash
mysql -u video_user -p video_overlay -e "SELECT status, COUNT(*) FROM render_jobs GROUP BY status;"
```

### Просмотр логов воркера
```bash
sudo journalctl -u video-worker -f
```

### Перезапуск воркера
```bash
sudo systemctl restart video-worker
```

### Обновление проекта (после изменений в репозитории)
```bash
cd /ssd/www/videoeditor
git pull origin main
composer install --no-dev --optimize-autoloader
php scripts/migrate.php
sudo systemctl reload php8.1-fpm
sudo systemctl restart apache2
sudo systemctl restart video-worker
```

## Тестирование обработки видео

1. Зарегистрируйтесь или войдите в систему
2. Загрузите тестовое видео (MP4, MOV, AVI, MKV, WEBM)
3. Создайте или выберите пресет наложений
4. Нажмите "Обработать" (рендеринг)
5. Дождитесь обработки (проверьте статус задачи в панели)
6. Скачайте готовое видео после завершения

### Поддерживаемые форматы
- Видео: MP4, MOV, AVI, MKV, WEBM
- Максимальный размер: 100MB (настраивается)
- Максимальная длительность: 5 минут (настраивается)

### Типы наложений
- **Subscribe** - Кнопка подписки
- **Like** - Кнопка лайка  
- **Title** - Текстовый заголовок видео

## Устранение неполадок

### Воркер не обрабатывает задачи
```bash
# Проверьте статус
sudo systemctl status video-worker

# Проверьте логи
sudo journalctl -u video-worker -n 50

# Проверьте FFmpeg
ffmpeg -version

# Перезапустите воркер
sudo systemctl restart video-worker
```

### Загрузка не работает
```bash
# Проверьте лимиты в Apache
sudo nano /etc/apache2/sites-available/videoeditor.conf
# LimitRequestBody 104857600

# Проверьте лимиты в PHP
php -i | grep upload_max_filesize
php -i | grep post_max_size

# Проверьте права доступа
sudo chown -R www-data:www-data /ssd/www/videoeditor/storage
sudo chmod -R 775 /ssd/www/videoeditor/storage
```

### Ошибки базы данных
```bash
# Проверьте учетные данные
nano /ssd/www/videoeditor/config/config.php

# Проверьте подключение
mysql -u video_user -p video_overlay

# Проверьте статус MySQL
sudo systemctl status mysql
```

### Проблемы с переводами
- Убедитесь что файлы в `lang/` существуют (en.php, ru.php, th.php, zh.php)
- Проверьте права доступа к файлам: `ls -la lang/`
- Очистите кэш браузера

### Проблемы с FFmpeg
```bash
# Установите FFmpeg если отсутствует
sudo apt install ffmpeg

# Проверьте версию
ffmpeg -version

# Проверьте путь в конфиге
grep ffmpeg /ssd/www/videoeditor/config/config.php
```
