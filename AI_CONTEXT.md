# Контекст проекта и текущее состояние

## Общая информация

**Проект:** Video Editor SaaS - платформа для автоматического добавления CTA оверлеев на видео  
**Репозиторий:** https://github.com/alexevil1979/videoeditor  
**Сервер:** Ubuntu VPS  
**Путь на сервере:** `/ssd/www/videoeditor`  
**Домен:** `videoeditor.1tlt.ru`  
**Веб-сервер:** Apache 2.4 + PHP-FPM 8.1  
**SSL:** Настроен через Let's Encrypt (certbot)  
**Локальный путь (Windows):** `C:\Users\1\Documents\videoeditor` (после переименования)

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

1. **500 ошибка после добавления FallbackResource:**
   - FallbackResource вызывает 500 Internal Server Error
   - Решение: убрать FallbackResource, использовать только mod_rewrite через .htaccess
   - Исправлено в коде, нужно применить на сервере

2. **Ошибка с layout.php:**
   - В `views/auth/login.php` и `views/auth/register.php` неправильный путь к layout.php
   - Было: `require __DIR__ . '/layout.php';`
   - Исправлено на: `require __DIR__ . '/../layout.php';`
   - Исправлено в коде, нужно применить на сервере

3. **Ошибка с DirectoryMatch в .htaccess:**
   - `<DirectoryMatch>` не разрешен в .htaccess (только в конфигурации Apache)
   - Убран из .htaccess
   - Исправлено в коде, нужно применить на сервере

4. **PowerShell проблемы:**
   - PowerShell не может обработать кириллицу в пути проекта
   - **РЕШЕНИЕ:** Переименовать каталог проекта с "обработка видео" на "videoeditor"
   - После переименования PowerShell будет работать нормально

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

1. **Переименовать каталог проекта (ВАЖНО!):**
   ```bash
   # На локальной машине (Windows):
   # Переименовать: "C:\Users\1\Documents\обработка видео" 
   # В: "C:\Users\1\Documents\videoeditor"
   ```
   
   После переименования:
   - PowerShell будет работать нормально
   - Git команды будут выполняться без ошибок
   - Все bat-файлы будут работать корректно

2. **Отправить все изменения в Git:**
   ```bash
   # После переименования каталога:
   cd "C:\Users\1\Documents\videoeditor"
   git add -A
   git commit -m "Fix: Remove FallbackResource, fix layout.php paths, remove DirectoryMatch from .htaccess, add create-admin script"
   git push origin main
   ```

3. **Обновить на сервере:**
   ```bash
   cd /ssd/www/videoeditor
   git reset --hard HEAD
   git pull origin main
   ```

4. **Убрать FallbackResource из конфигурации Apache на сервере:**
   ```bash
   sudo nano /etc/apache2/sites-available/videoeditor.conf
   # Удалить строку: FallbackResource /index.php
   sudo apache2ctl configtest
   sudo systemctl restart apache2
   ```

5. **Создать первого администратора:**
   ```bash
   cd /ssd/www/videoeditor
   php scripts/create-admin.php
   # Ввести email и password
   ```

6. **Проверить работу сайта:**
   - Открыть: `https://videoeditor.1tlt.ru/login`
   - Войти с созданными учетными данными

### После переименования каталога:

1. **Проверить что Git работает:**
   ```bash
   cd "C:\Users\1\Documents\videoeditor"
   git status
   git remote -v
   ```

2. **Проверить что все файлы на месте:**
   ```bash
   ls -la
   # Проверить наличие всех директорий: app, config, public, scripts и т.д.
   ```

3. **Обновить пути в документации (если нужно):**
   - Все пути в документации уже используют `/ssd/www/videoeditor`
   - Локальный путь теперь: `C:\Users\1\Documents\videoeditor`

### После исправления всех проблем:

1. Убрать отладочное логирование из production
2. Настроить правильную обработку ошибок
3. Протестировать все маршруты
4. Создать первого администратора
5. Настроить воркер для обработки очереди видео

## Важные заметки

### PowerShell и кириллица:
- ~~PowerShell не может обработать кириллицу в путях~~ **РЕШЕНО:** Каталог переименован в `videoeditor`
- После переименования PowerShell будет работать нормально
- Bat-файлы все еще полезны для быстрого деплоя
- Всегда создавать bat-файлы для деплоя после изменений

### Исправленные проблемы:
1. ✅ Убран FallbackResource из Apache конфигурации (вызывал 500 ошибку)
2. ✅ Исправлен путь к layout.php в views/auth/login.php и register.php
3. ✅ Убран DirectoryMatch из .htaccess (не разрешен в .htaccess)
4. ✅ Создан скрипт scripts/create-admin.php для создания администратора

### Git workflow:
- После любых изменений **ВСЕГДА использовать PowerShell** для деплоя
- Использовать скрипт `deploy-fixes-final.ps1` или создать новый PowerShell скрипт
- Выполнять: `powershell -ExecutionPolicy Bypass -File deploy-fixes-final.ps1`
- На сервере выполнять `git pull origin main`

### Apache конфигурация:
- Используется PHP-FPM через mod_proxy_fcgi
- php_value директивы не работают (настраивать в php.ini)
- AllowOverride All обязательно для .htaccess

## Последнее обновление

**Дата:** 2024-12-19  
**Статус:** ✅ Все исправления закоммичены и готовы к деплою  
**Следующий шаг:** 
1. ✅ Каталог проекта переименован в `videoeditor` (проблемы с кириллицей решены)
2. ✅ Все изменения отправлены в Git (коммит: 8f189a6)
3. ⏳ Обновить на сервере: `git pull origin main`
4. ⏳ Убедиться что FallbackResource отсутствует в Apache конфигурации
5. ⏳ Создать первого администратора через `php scripts/create-admin.php`
6. ⏳ Проверить работу сайта: `https://videoeditor.1tlt.ru/login`

## Исправления в коде (закоммичены, готовы к деплою):

1. ✅ **config/apache.conf** - убран FallbackResource (вызывал 500 ошибку)
2. ✅ **public/.htaccess** - убран DirectoryMatch (не разрешен в .htaccess), убран FallbackResource
3. ✅ **views/auth/login.php** - исправлен путь к layout.php (`/../layout.php`)
4. ✅ **views/auth/register.php** - исправлен путь к layout.php (`/../layout.php`)
5. ✅ **scripts/create-admin.php** - новый скрипт для создания администратора

## Инструкции для деплоя:

### На локальной машине:
**ВАЖНО: Всегда использовать PowerShell для деплоя!**

1. Запустить PowerShell скрипт:
   ```powershell
   powershell -ExecutionPolicy Bypass -File deploy-fixes-final.ps1
   ```
2. Или вручную через PowerShell:
   ```powershell
   git add -A
   git commit -m "Описание изменений"
   git push origin main
   ```

### На сервере:
```bash
cd /ssd/www/videoeditor
git pull origin main

# Проверить Apache конфигурацию
sudo nano /etc/apache2/sites-available/videoeditor.conf
# Убедиться что FallbackResource отсутствует

# Проверить и перезапустить Apache
sudo apache2ctl configtest
sudo systemctl restart apache2

# Создать первого администратора
php scripts/create-admin.php
```
