# Структура проекта

```
videoeditor/
├── app/
│   ├── Controllers/          # Обработчики запросов
│   │   ├── AdminController.php
│   │   ├── AuthController.php
│   │   ├── DashboardController.php
│   │   ├── PresetController.php
│   │   └── VideoController.php
│   ├── Core/                 # Основные классы фреймворка
│   │   ├── Config.php        # Менеджер конфигурации
│   │   ├── Database.php      # Абстракция базы данных
│   │   ├── Response.php       # Обработчик HTTP ответов
│   │   ├── Router.php        # Маршрутизация URL
│   │   └── Session.php       # Управление сессиями
│   ├── Middleware/           # Middleware запросов
│   │   ├── AdminMiddleware.php
│   │   └── AuthMiddleware.php
│   ├── Models/               # Модели базы данных
│   │   ├── Preset.php
│   │   ├── RenderJob.php
│   │   ├── User.php
│   │   └── Video.php
│   └── Services/             # Бизнес-логика
│       ├── AuthService.php
│       ├── FFmpegService.php # Обработка видео
│       └── VideoService.php
├── config/
│   ├── config.example.php    # Пример конфигурации
│   └── nginx.conf            # Виртуальный хост Nginx
├── database/
│   └── schema.sql            # Схема базы данных
├── public/                   # Корень веб-сервера (корень документа Nginx)
│   ├── index.php            # Точка входа приложения
│   └── assets/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
├── scripts/
│   ├── deploy.sh            # Скрипт развертывания
│   ├── migrate.php          # Миграция базы данных
│   ├── video-worker.service # Файл сервиса systemd
│   └── worker.php           # Воркер очереди
├── storage/                  # Хранилище файлов
│   ├── uploads/            # Оригинальные видео
│   ├── renders/            # Обработанные видео
│   ├── logs/               # Логи приложения
│   └── cache/              # Временные файлы
├── views/                   # HTML шаблоны
│   ├── admin/
│   │   ├── dashboard.php
│   │   ├── jobs.php
│   │   └── users.php
│   ├── auth/
│   │   ├── login.php
│   │   └── register.php
│   ├── dashboard/
│   │   └── index.php
│   └── layout.php
├── .github/
│   └── workflows/
│       └── deploy.yml       # GitHub Actions CI/CD
├── .gitignore
├── ARCHITECTURE_RU.md       # Архитектура системы
├── composer.json            # PHP зависимости
├── DEPLOYMENT_RU.md         # Руководство по развертыванию
├── PROJECT_STRUCTURE_RU.md  # Этот файл
├── README_RU.md             # Основная документация
└── SECURITY_RU.md           # Заметки по безопасности
```

## Ключевые файлы

### Точка входа
- `public/index.php` - Главная точка входа приложения, маршрутизирует запросы

### Конфигурация
- `config/config.example.php` - Скопируйте в `config/config.php` и настройте
- `config/nginx.conf` - Конфигурация виртуального хоста Nginx

### База данных
- `database/schema.sql` - Полная схема базы данных
- `scripts/migrate.php` - Запустите для инициализации базы данных

### Воркеры
- `scripts/worker.php` - Воркер очереди (запускается через systemd)
- `scripts/video-worker.service` - Файл сервиса systemd

### Развертывание
- `scripts/deploy.sh` - Скрипт ручного развертывания
- `.github/workflows/deploy.yml` - Автоматизированный CI/CD

## Права доступа к файлам

На Linux сервере:
```bash
# Файлы приложения
chmod 755 -R /ssd/www/videoeditor
chown www-data:www-data -R /ssd/www/videoeditor

# Директории хранилища (доступны для записи)
chmod 775 -R /ssd/www/videoeditor/storage
```

## Переменные окружения

Вся конфигурация находится в `config/config.php`. Для продакшена рекомендуется переместить чувствительные данные в переменные окружения.

## Зависимости

- PHP 8.1+ с расширениями: pdo_mysql, mbstring (gd опционально для кнопок)
- MySQL 8.0+
- Nginx
- FFmpeg
- Composer (для автозагрузки)
