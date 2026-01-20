# Исправление 500 ошибки после добавления FallbackResource

## Проблема
500 Internal Server Error после добавления `FallbackResource /index.php`.

## Возможные причины

1. **FallbackResource конфликтует с mod_rewrite** - если mod_rewrite включен, FallbackResource может вызывать проблемы
2. **Неправильный путь к index.php** - FallbackResource должен использовать относительный путь
3. **Проблема с PHP-FPM** - PHP-FPM не запущен или не может обработать запрос
4. **Ошибка в index.php** - синтаксическая ошибка или отсутствие зависимостей

## Решение

### Вариант 1: Убрать FallbackResource, использовать только mod_rewrite

```bash
# Отредактируйте конфигурацию
sudo nano /etc/apache2/sites-available/videoeditor.conf
```

Уберите строку `FallbackResource /index.php` из секции Directory.

Оставьте только:
```apache
<Directory /ssd/www/videoeditor/public>
    Options -Indexes +FollowSymLinks
    AllowOverride All
    Require all granted
    
    # PHP-FPM через mod_proxy_fcgi
    <FilesMatch \.php$>
        SetHandler "proxy:fcgi://127.0.0.1:9000"
    </FilesMatch>
</Directory>
```

Проверьте что .htaccess работает правильно.

### Вариант 2: Исправить FallbackResource

FallbackResource должен быть без начального слэша для относительного пути:

```apache
FallbackResource index.php
```

Или с полным путем от DocumentRoot:

```apache
FallbackResource /index.php
```

Но лучше использовать mod_rewrite через .htaccess.

### Вариант 3: Проверить логи и исправить ошибку

```bash
# Проверьте логи
sudo tail -50 /var/log/apache2/videoeditor_ssl_error.log

# Если ошибка в PHP, проверьте:
sudo tail -50 /var/log/php8.1-fpm.log
```

## Рекомендуемое решение

Убрать FallbackResource из Apache конфигурации и использовать только mod_rewrite через .htaccess:

1. Уберите `FallbackResource /index.php` из конфигурации Apache
2. Убедитесь что mod_rewrite включен: `sudo a2enmod rewrite`
3. Убедитесь что .htaccess настроен правильно
4. Перезапустите Apache: `sudo systemctl restart apache2`
