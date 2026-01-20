# Создание первого администратора

## Способ 1: Через скрипт (рекомендуется)

```bash
cd /ssd/www/videoeditor
php scripts/create-admin.php
```

Скрипт попросит ввести:
- Email
- Password (минимум 8 символов)
- First name (опционально)
- Last name (опционально)

## Способ 2: Через регистрацию на сайте

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

## Способ 3: Прямой SQL запрос

```bash
mysql -u video_user -p video_overlay
```

```sql
-- Создать пользователя
INSERT INTO users (email, password_hash, role, created_at) 
VALUES ('admin@example.com', '$2y$10$YourHashedPasswordHere', 'admin', NOW());

-- Получить ID созданного пользователя
SELECT id FROM users WHERE email = 'admin@example.com';

-- Создать профиль (замените USER_ID на полученный ID)
INSERT INTO user_profiles (user_id, first_name, last_name, language, created_at) 
VALUES (USER_ID, 'Admin', 'User', 'en', NOW());

-- Создать баланс
INSERT INTO balances (user_id, balance, created_at) 
VALUES (USER_ID, 0, NOW());

EXIT;
```

**Для генерации хеша пароля:**

```bash
php -r "echo password_hash('your_password', PASSWORD_DEFAULT) . PHP_EOL;"
```

## Проверка

После создания пользователя проверьте:

```bash
mysql -u video_user -p video_overlay -e "SELECT id, email, role FROM users WHERE role = 'admin';"
```

## Вход

Откройте: `https://videoeditor.1tlt.ru/login`

Введите:
- Email: тот который вы указали
- Password: тот который вы указали
