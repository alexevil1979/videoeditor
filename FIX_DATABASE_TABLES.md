# Исправление проблемы с таблицами БД

## Проблема
Миграция говорит "Database schema loaded successfully!", но таблица `render_jobs` не найдена.

## Возможные причины

1. **Миграция выполнилась в другую базу данных** - проверьте config.php
2. **Таблицы не создались из-за ошибок** - проверьте логи
3. **Проблема с FOREIGN KEY** - возможно таблицы users/videos/presets не существуют

## Решение

### 1. Проверьте какая база данных используется

```bash
cd /ssd/www/videoeditor
cat config/config.php | grep -A 5 database
```

Должно быть:
```php
'database' => [
    'host' => 'localhost',
    'dbname' => 'video_overlay',
    ...
]
```

### 2. Проверьте какие таблицы существуют

```bash
mysql -u video_user -p video_overlay -e "SHOW TABLES;"
```

Если таблиц нет или их мало, значит миграция не выполнилась полностью.

### 3. Импортируйте схему напрямую

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

### 5. Если таблицы все еще не созданы

Проверьте ошибки:

```bash
mysql -u video_user -p video_overlay < database/schema.sql 2>&1
```

Или выполните вручную:

```bash
mysql -u video_user -p video_overlay
```

```sql
SHOW TABLES;
-- Если таблиц нет, выполните:
SOURCE /ssd/www/videoeditor/database/schema.sql;
SHOW TABLES;
EXIT;
```

### 6. Проверьте что таблица render_jobs существует

```bash
mysql -u video_user -p video_overlay -e "DESCRIBE render_jobs;"
```

Если таблица существует, но воркер все еще не видит ее, проверьте:
- Правильные ли данные в config.php
- Перезапустите воркер: `sudo systemctl restart video-worker`

## Быстрое решение (если ничего не помогло)

```bash
cd /ssd/www/videoeditor

# 1. Удалите все таблицы (ОСТОРОЖНО - удалит данные!)
mysql -u video_user -p video_overlay -e "DROP DATABASE video_overlay; CREATE DATABASE video_overlay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 2. Импортируйте схему заново
mysql -u video_user -p video_overlay < database/schema.sql

# 3. Проверьте
mysql -u video_user -p video_overlay -e "SHOW TABLES;"

# 4. Перезапустите воркер
sudo systemctl restart video-worker
```
