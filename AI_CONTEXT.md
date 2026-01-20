# Контекст проекта и текущее состояние

## Общая информация

**Проект:** Video Editor SaaS - платформа для автоматического добавления CTA оверлеев на видео  
**Репозиторий:** https://github.com/alexevil1979/videoeditor  
**Сервер:** Ubuntu VPS  
**Путь на сервере:** `/ssd/www/videoeditor`  
**Домен:** `videoeditor.1tlt.ru`  
**Веб-сервер:** Apache 2.4 + PHP-FPM 8.1  
**SSL:** Настроен через Let's Encrypt (certbot)

## Текущее состояние

### ✅ Что уже сделано:

1. **Инфраструктура:**
   - Apache настроен с SSL (HTTPS)
   - PHP-FPM настроен через mod_proxy_fcgi
   - mod_rewrite включен
   - SSL сертификат получен и настроен

2. **Конфигурация:**
   - `config/apache.conf` - правильная конфигурация Apache с SSL
   - `public/.htaccess` - настроен для маршрутизации
   - Права доступа установлены (www-data:www-data)

3. **Отладка:**
   - Добавлено расширенное логирование в `public/index.php`
   - Добавлено логирование в `app/Core/Router.php`
   - Созданы файлы для диагностики

### ❌ Текущие проблемы:

1. **404 ошибка на маршрутах:**
   - Главная страница `/` редиректит на `/login` ✅
   - Но `/login` возвращает 404 ❌
   - Проблема с маршрутизацией через .htaccess

2. **Изменения не в Git:**
   - Локальные изменения с логированием не отправлены в репозиторий
   - На сервере `git pull` показывает "Already up to date"
   - Нужно запустить `git-push-now.bat` на локальной машине

3. **PowerShell проблемы:**
   - PowerShell не может обработать кириллицу в пути проекта
   - Используются bat-файлы для работы с Git

## Технические детали

### Структура проекта:
```
videoeditor/
├── app/
│   ├── Controllers/     # Контроллеры (AuthController, VideoController и т.д.)
│   ├── Core/            # Ядро (Router, Database, Config и т.д.)
│   ├── Models/          # Модели БД
│   └── Services/        # Бизнес-логика
├── public/
│   ├── index.php        # Точка входа (с логированием)
│   └── .htaccess        # Маршрутизация
├── config/
│   └── apache.conf      # Конфигурация Apache
└── scripts/
    └── worker.php       # Воркер для очереди
```

### Важные файлы:

1. **public/index.php:**
   - Добавлено логирование REQUEST_URI, SCRIPT_NAME, PHP_SELF
   - Логи пишутся в `storage/logs/php_errors.log`

2. **app/Core/Router.php:**
   - Добавлено логирование метода, URI и количества маршрутов
   - Улучшена обработка 404 с отладочной информацией

3. **config/apache.conf:**
   - Настроен SSL с Let's Encrypt
   - PHP-FPM через mod_proxy_fcgi
   - AllowOverride All для .htaccess

### Зависимости PHP:
- ✅ `ext-mbstring` - обязательно
- ✅ `ext-pdo_mysql` - обязательно
- ⚠️ `ext-gd` - опционально (для генерации изображений кнопок)
- ❌ `ext-zip` - удален, не используется

## Следующие шаги

### Немедленные действия:

1. **Отправить изменения в Git:**
   ```bash
   # На локальной машине (Windows):
   # Двойной клик по файлу: git-push-now.bat
   # ИЛИ в CMD:
   cd "C:\Users\1\Documents\обработка видео"
   git add -A
   git commit -m "Add: Enhanced debugging and logging for routing issues"
   git push origin main
   ```

2. **Обновить на сервере:**
   ```bash
   cd /ssd/www/videoeditor
   git pull origin main
   ```

3. **Проверить что изменения применены:**
   ```bash
   grep "REQUEST_URI" /ssd/www/videoeditor/public/index.php
   grep "Router dispatch" /ssd/www/videoeditor/app/Core/Router.php
   ```

4. **Диагностика проблемы с маршрутизацией:**
   ```bash
   # Открыть в браузере: https://videoeditor.1tlt.ru/login?debug=1
   # Проверить логи:
   tail -50 /ssd/www/videoeditor/storage/logs/php_errors.log
   tail -50 /var/log/apache2/videoeditor_ssl_error.log
   ```

### Диагностика проблемы 404:

1. **Проверить что .htaccess применяется:**
   - Убедиться что `AllowOverride All` в Apache конфигурации
   - Проверить права на `.htaccess` (644, www-data:www-data)

2. **Проверить что mod_rewrite работает:**
   ```bash
   apache2ctl -M | grep rewrite
   ```

3. **Проверить логи:**
   - Логи PHP покажут какой URI приходит в приложение
   - Логи Apache покажут ошибки сервера

4. **Тестовый файл:**
   ```bash
   # Создать test.php для проверки
   echo "<?php echo \$_SERVER['REQUEST_URI']; ?>" > /ssd/www/videoeditor/public/test.php
   # Открыть: https://videoeditor.1tlt.ru/test.php
   ```

### После исправления маршрутизации:

1. Убрать отладочное логирование из production
2. Настроить правильную обработку ошибок
3. Протестировать все маршруты
4. Настроить воркер для обработки очереди видео

## Важные заметки

### PowerShell и кириллица:
- PowerShell не может обработать кириллицу в путях
- Используются bat-файлы для работы с Git
- Всегда создавать bat-файлы для деплоя после изменений

### Git workflow:
- После любых изменений создавать bat-файл для деплоя
- Пользователь запускает bat-файл двойным кликом
- На сервере выполнять `git pull origin main`

### Apache конфигурация:
- Используется PHP-FPM через mod_proxy_fcgi
- php_value директивы не работают (настраивать в php.ini)
- AllowOverride All обязательно для .htaccess

## Последнее обновление

**Дата:** 2024-12-19  
**Статус:** Диагностика проблемы с маршрутизацией  
**Следующий шаг:** Отправить изменения в Git и проверить логи на сервере
