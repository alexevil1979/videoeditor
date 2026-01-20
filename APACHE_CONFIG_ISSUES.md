# Проблемы в вашей конфигурации Apache и исправления

## Обнаруженные проблемы

### HTTP VirtualHost (порт 80):

1. ❌ **`<FilesMatch \.php$>` находится вне `<Directory>`**
   - Должно быть внутри `<Directory>` блока
   - Иначе PHP-FPM не будет работать правильно

2. ✅ **Редирект на HTTPS** - правильный, но можно упростить

### HTTPS VirtualHost (порт 443):

1. ❌ **`<FilesMatch \.php$>` находится вне `<Directory>`**
   - Должно быть внутри `<Directory>` блока

2. ❌ **`<Directory /ssd/www/videoeditor>` - неправильный путь**
   - Должно быть `/ssd/www/videoeditor/public`
   - Иначе Apache будет искать файлы в неправильной директории

3. ❌ **Отсутствуют важные директивы в `<Directory>`**
   - Нет `Options -Indexes +FollowSymLinks`
   - Нет `AllowOverride All` (хотя есть, но в неправильном месте)
   - Нет `Require all granted` (хотя есть, но в неправильном месте)

4. ❌ **Отсутствует защита от прямого доступа к файлам**
   - Нет `<FilesMatch>` для блокировки конфигурационных файлов

5. ❌ **Отсутствует `LimitRequestBody`**
   - Нет ограничения размера загружаемых файлов

6. ⚠️ **Порядок директив SSL**
   - `SSLEngine on` должен быть перед сертификатами
   - Но это не критично

## Исправленная конфигурация

См. файл `APACHE_CONFIG_FIXED.conf` - там правильная версия.

## Что нужно сделать

1. Скопируйте исправленную конфигурацию:
```bash
cd /ssd/www/videoeditor
sudo cp APACHE_CONFIG_FIXED.conf /etc/apache2/sites-available/videoeditor.conf
```

2. Или используйте конфигурацию из репозитория:
```bash
cd /ssd/www/videoeditor
git pull origin main
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf
```

3. Проверьте и перезапустите:
```bash
sudo apache2ctl configtest
sudo systemctl restart apache2
```
