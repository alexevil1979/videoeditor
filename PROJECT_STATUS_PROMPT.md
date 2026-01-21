# Промпт для быстрого понимания текущего состояния проекта

Используй этот промпт для быстрого понимания проекта и продолжения работы.

---

## Контекст проекта

**Проект:** Video Editor SaaS - платформа для автоматического добавления CTA оверлеев на видео  
**Репозиторий:** https://github.com/alexevil1979/videoeditor  
**Сервер:** Ubuntu VPS  
**Путь на сервере:** `/ssd/www/videoeditor`  
**Домен:** `videoeditor.1tlt.ru`  
**Локальный путь:** `C:\Users\1\Documents\videoeditor`  
**Веб-сервер:** Apache 2.4 + PHP-FPM 8.1  
**SSL:** Настроен через Let's Encrypt

---

## Текущее состояние проекта

### ✅ Что работает:

1. **Инфраструктура:**
   - Apache настроен с SSL (HTTPS)
   - PHP-FPM настроен через mod_proxy_fcgi
   - SSL сертификат получен и настроен
   - База данных настроена

2. **Функциональность:**
   - Регистрация и авторизация пользователей
   - Загрузка видео
   - Создание пресетов с кнопками Subscribe, Like, Title
   - Интерфейс для наложения кнопок на видео
   - Система очереди для обработки видео
   - Воркер для обработки видео через FFmpeg

3. **Исправления:**
   - Убран FallbackResource из Apache конфигурации
   - Исправлены пути к layout.php в views/auth
   - Убран DirectoryMatch из .htaccess
   - Создан скрипт для создания администратора
   - Исправлена ошибка с двойным двоеточием в фильтре drawtext
   - Исправлена ошибка инициализации энкодера (добавлен pad и явный размер)
   - Исправлена ошибка "height not divisible by 2" (размеры теперь четные)

### ⚠️ Текущие проблемы:

1. **Обработка видео:**
   - Задачи рендеринга падают с ошибками FFmpeg
   - Последняя ошибка: "height not divisible by 2" - ИСПРАВЛЕНО в коде
   - Нужно обновить код на сервере и протестировать

2. **Логирование:**
   - Добавлено расширенное логирование ошибок
   - Логи сохраняются в `storage/logs/worker_errors.log` и `storage/logs/ffmpeg_commands.log`

---

## Структура проекта

```
videoeditor/
├── app/
│   ├── Controllers/     # Контроллеры (AuthController, VideoController, PresetController, DashboardController)
│   ├── Core/            # Ядро (Router, Database, Config, Session, Lang)
│   ├── Models/          # Модели БД (User, Video, Preset, RenderJob)
│   └── Services/        # Бизнес-логика (FFmpegService, VideoService, AuthService)
├── public/
│   ├── index.php        # Точка входа
│   └── .htaccess        # Маршрутизация
├── views/
│   ├── auth/            # Страницы авторизации
│   ├── dashboard/       # Dashboard пользователя (с интерфейсом создания пресетов)
│   └── layout.php       # Основной layout
├── config/
│   ├── config.php       # Конфигурация (создать из config.example.php)
│   └── apache.conf      # Конфигурация Apache
├── scripts/
│   ├── worker.php       # Воркер для обработки очереди
│   ├── create-admin.php # Скрипт создания администратора
│   └── start-worker.sh  # Скрипт запуска воркера с проверками
└── storage/
    ├── uploads/         # Загруженные видео
    ├── renders/         # Обработанные видео
    └── logs/            # Логи приложения
```

---

## Важные файлы

1. **AI_CONTEXT.md** - Подробный контекст проекта и текущее состояние
2. **USER_REQUESTS.md** - История всех запросов пользователя
3. **SERVER_DEPLOY_COMMANDS.txt** - Команды для применения на сервере (обновляется после каждой работы)
4. **HOW_TO_GET_VIDEO_WITH_OVERLAY.md** - Инструкция для пользователей
5. **DEBUG_RENDERING_ERRORS.md** - Инструкция по диагностике ошибок

---

## Workflow

### Для деплоя изменений:

1. **Всегда использовать PowerShell для отправки в Git:**
   ```powershell
   powershell -Command "git add .; git commit -m 'Описание'; git push origin main"
   ```

2. **После каждой работы создавать файл `SERVER_DEPLOY_COMMANDS.txt`** с командами для сервера

3. **Обновлять `USER_REQUESTS.md`** с новыми запросами

### Для работы на сервере:

1. Обновить код: `cd /ssd/www/videoeditor && git pull origin main`
2. Установить права: `sudo chown -R www-data:www-data /ssd/www/videoeditor && sudo chmod -R 775 /ssd/www/videoeditor/storage`
3. Перезапустить воркер: `php scripts/worker.php`

---

## Последние исправления

### 2024-12-19:

1. ✅ Добавлен интерфейс создания пресетов с кнопками Subscribe, Like, Title
2. ✅ Исправлена ошибка с двойным двоеточием в фильтре drawtext
3. ✅ Исправлена ошибка инициализации энкодера (добавлен pad и явный размер вывода)
4. ✅ Исправлена ошибка "height not divisible by 2" (размеры теперь всегда четные)
5. ✅ Улучшено логирование ошибок FFmpeg
6. ✅ Добавлен отладочный вывод в консоль воркера

---

## Следующие шаги

1. **Обновить код на сервере** и протестировать обработку видео
2. **Проверить работу воркера** после всех исправлений
3. **Протестировать создание пресетов и рендеринг видео** с наложенными кнопками

---

## Важные заметки

- **Всегда использовать PowerShell** для отправки изменений в Git
- **Всегда создавать `SERVER_DEPLOY_COMMANDS.txt`** после работы
- **Всегда обновлять `USER_REQUESTS.md`** с новыми запросами
- На сервере **не делать изменения напрямую** - все через Git
- Воркер должен быть запущен для обработки видео

---

## Команды для быстрого старта

```bash
# Локально (Windows):
cd C:\Users\1\Documents\videoeditor
powershell -Command "git pull origin main"

# На сервере:
cd /ssd/www/videoeditor
git pull origin main
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage
php scripts/worker.php
```

---

**Последнее обновление:** 2024-12-19  
**Статус:** Проект готов к тестированию обработки видео после применения последних исправлений на сервере
