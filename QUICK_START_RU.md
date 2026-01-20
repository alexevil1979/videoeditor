# Краткое руководство

## Для разработчиков

### Настройка локальной разработки

1. **Установите зависимости:**
   ```bash
   composer install
   ```

2. **Настройте:**
   ```bash
   cp config/config.example.php config/config.php
   # Отредактируйте config/config.php
   ```

3. **Настройте базу данных:**
   ```bash
   php scripts/migrate.php
   ```

4. **Запустите встроенный сервер PHP:**
   ```bash
   php -S localhost:8000 -t public
   ```

5. **Запустите воркер (отдельный терминал):**
   ```bash
   php scripts/worker.php
   ```

6. **Доступ:**
   - Приложение: http://localhost:8000
   - Админ: admin@example.com / admin123

## Для развертывания в продакшене

### Настройка одной командой (после первоначальной подготовки сервера)

```bash
cd /ssd/www
git clone https://github.com/alexevil1979/videoeditor.git videoeditor
cd videoeditor
composer install --no-dev --optimize-autoloader
cp config/config.example.php config/config.php
# Отредактируйте config/config.php
php scripts/migrate.php
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 775 storage
sudo cp config/nginx.conf /etc/nginx/sites-available/videoeditor
sudo ln -s /etc/nginx/sites-available/videoeditor /etc/nginx/sites-enabled/
sudo cp scripts/video-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable video-worker
sudo systemctl start video-worker
sudo systemctl reload nginx
```

## Ключевые URL

- `/` - Главная (перенаправляет на логин/дашборд)
- `/login` - Вход пользователя
- `/register` - Регистрация пользователя
- `/dashboard` - Панель пользователя
- `/admin` - Панель администратора
- `/api/videos/upload` - Загрузка видео (POST)
- `/api/videos/render` - Создание задачи рендеринга (POST)
- `/api/videos/download/{id}` - Скачать обработанное видео

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

## Тестирование обработки видео

1. Загрузите тестовое видео (MP4, MOV, AVI и т.д.)
2. Создайте или выберите пресет
3. Нажмите "Обработать"
4. Дождитесь обработки (проверьте статус задачи)
5. Скачайте готовое видео

## Устранение неполадок

**Воркер не обрабатывает:**
- Проверьте статус: `sudo systemctl status video-worker`
- Проверьте логи: `sudo journalctl -u video-worker -n 50`
- Проверьте FFmpeg: `ffmpeg -version`

**Загрузка не работает:**
- Проверьте лимиты размера файла в Nginx и PHP
- Проверьте права доступа к директории storage
- Проверьте логи ошибок PHP

**Ошибки базы данных:**
- Проверьте учетные данные в `config/config.php`
- Проверьте подключение: `mysql -u video_user -p video_overlay`
