# Учетные данные для входа

## Способ 1: Создать администратора через скрипт (рекомендуется)

```bash
cd /ssd/www/videoeditor
php scripts/create-admin.php
```

Скрипт попросит ввести:
- **Email** (например: `admin@videoeditor.1tlt.ru`)
- **Password** (минимум 8 символов)
- First name (опционально)
- Last name (опционально)

После создания используйте эти данные для входа.

## Способ 2: Дефолтный администратор (если был создан при миграции)

Если в базе данных был создан дефолтный администратор:

- **Email:** `admin@example.com`
- **Password:** `admin123`

⚠️ **ВАЖНО**: Если используете дефолтный пароль, измените его сразу после первого входа!

## Способ 3: Зарегистрировать обычного пользователя и сделать его админом

1. Откройте: `https://videoeditor.1tlt.ru/register`
2. Зарегистрируйте пользователя
3. В базе данных измените роль на `admin`:

```bash
mysql -u video_user -p video_overlay
```

```sql
UPDATE users SET role = 'admin' WHERE email = 'your_email@example.com';
EXIT;
```

## Проверка существующих пользователей

```bash
mysql -u video_user -p video_overlay -e "SELECT id, email, role FROM users;"
```

## Вход в систему

1. Откройте: `https://videoeditor.1tlt.ru/login`
2. Введите:
   - **Email** - тот который вы указали при создании
   - **Password** - тот который вы указали при создании
3. Нажмите "Войти"

## Если забыли пароль

Сбросить пароль можно через SQL:

```bash
mysql -u video_user -p video_overlay
```

```sql
-- Сгенерировать новый хеш пароля (замените 'new_password' на ваш пароль)
-- Выполните в PHP:
-- php -r "echo password_hash('new_password', PASSWORD_DEFAULT) . PHP_EOL;"

-- Обновить пароль
UPDATE users SET password_hash = '$2y$10$YourNewHashedPasswordHere' WHERE email = 'your_email@example.com';
EXIT;
```

Или создайте нового администратора через скрипт.
