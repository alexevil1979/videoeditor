# Исправление проблемы с таблицами БД

## Проблема
Миграция говорит "Database schema loaded successfully!", но таблиц нет.

## Решение

### 1. Проверьте какие таблицы есть

```bash
mysql -u video_user -p video_overlay -e "SHOW TABLES;"
```

Если таблиц нет, продолжайте.

### 2. Проверьте config.php

```bash
cd /ssd/www/videoeditor
cat config/config.php | grep -A 5 database
```

Должно быть:
```php
'database' => [
    'host' => 'localhost',
    'dbname' => 'video_overlay',
    'username' => 'video_user',
    'password' => 'your_password',
],
```

### 3. Импортируйте схему напрямую через MySQL

```bash
cd /ssd/www/videoeditor
mysql -u video_user -p video_overlay < database/schema.sql
```

### 4. Проверьте таблицы снова

```bash
mysql -u video_user -p video_overlay -e "SHOW TABLES;"
```

Должны быть:
- users
- user_profiles
- balances
- balance_transactions
- videos
- presets
- preset_items
- render_jobs
- system_settings
- logs

### 5. Если таблицы все еще не созданы - проверьте ошибки

```bash
mysql -u video_user -p video_overlay < database/schema.sql 2>&1
```

### 6. Если проблема с FOREIGN KEY

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

### 7. Проверьте что таблица render_jobs существует

```bash
mysql -u video_user -p video_overlay -e "DESCRIBE render_jobs;"
```

Если таблица существует, но воркер не видит ее:
- Проверьте config.php
- Перезапустите воркер: `sudo systemctl restart video-worker`
