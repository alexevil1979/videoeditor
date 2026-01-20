# Настройка базы данных

## Проблема
Ошибка: `Table 'video_overlay.render_jobs' doesn't exist`

Это значит, что миграции базы данных не были выполнены.

## Решение

### 1. Создайте базу данных (если еще не создана)

```bash
mysql -u root -p
```

```sql
CREATE DATABASE IF NOT EXISTS video_overlay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'video_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON video_overlay.* TO 'video_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 2. Настройте config.php

```bash
cd /ssd/www/videoeditor
cp config/config.example.php config/config.php
nano config/config.php
```

Укажите правильные данные:
```php
'database' => [
    'host' => 'localhost',
    'dbname' => 'video_overlay',
    'username' => 'video_user',
    'password' => 'your_password',
],
```

### 3. Запустите миграции

**Вариант 1: Через скрипт миграции**
```bash
cd /ssd/www/videoeditor
php scripts/migrate.php
```

**Вариант 2: Прямой импорт (если скрипт не работает)**
```bash
cd /ssd/www/videoeditor
mysql -u video_user -p video_overlay < database/schema.sql
```

Должно вывести что-то вроде:
```
Database schema loaded successfully!
```

### 4. Проверьте таблицы

```bash
mysql -u video_user -p video_overlay -e "SHOW TABLES;"
```

Должны быть таблицы:
- users
- user_profiles
- balances
- videos
- presets
- preset_items
- render_jobs
- system_settings
- logs

### 5. Перезапустите воркер

```bash
sudo systemctl restart video-worker
# или если запускаете вручную:
php scripts/worker.php
```

## Быстрая проверка

```bash
# Проверьте подключение к БД
cd /ssd/www/videoeditor
php -r "require 'app/Core/Config.php'; require 'app/Core/Database.php'; App\Core\Config::load('config/config.php'); echo 'DB OK: ' . (App\Core\Database::getInstance() ? 'Connected' : 'Failed');"
```

## Если миграции не работают

### Проверьте какие таблицы созданы

```bash
mysql -u video_user -p video_overlay -e "SHOW TABLES;"
```

Если таблиц нет или их мало, импортируйте схему напрямую:

```bash
cd /ssd/www/videoeditor
mysql -u video_user -p video_overlay < database/schema.sql
```

### Проверьте ошибки

```bash
mysql -u video_user -p video_overlay < database/schema.sql 2>&1 | grep -i error
```

### Если проблема с FOREIGN KEY

Если таблицы users/videos/presets не существуют, render_jobs не создастся из-за FOREIGN KEY.

Создайте таблицы в правильном порядке или временно отключите проверку:

```bash
mysql -u video_user -p video_overlay
```

```sql
SET FOREIGN_KEY_CHECKS = 0;
SOURCE /ssd/www/videoeditor/database/schema.sql;
SET FOREIGN_KEY_CHECKS = 1;
SHOW TABLES;
EXIT;
```
