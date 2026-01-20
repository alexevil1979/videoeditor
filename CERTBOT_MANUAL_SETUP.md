# Ручная настройка SSL через Certbot (когда автоматическая не работает)

## Проблема

Certbot выдает ошибку "Could not reverse map the HTTPS VirtualHost to the original" когда:
- В конфигурации Apache уже есть оба VirtualHost (HTTP и HTTPS)
- Структура конфигурации не соответствует ожиданиям certbot

## Решение: Ручная настройка

### Вариант 1: Использовать certonly (рекомендуется)

```bash
# 1. Получите сертификат без автоматической настройки Apache
sudo certbot certonly --apache -d videoeditor.1tlt.ru

# 2. Вручную настройте Apache (конфигурация уже готова в config/apache.conf)
cd /ssd/www/videoeditor
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf

# 3. Включите модули
sudo a2enmod ssl rewrite proxy proxy_fcgi

# 4. Проверьте и перезапустите
sudo apache2ctl configtest
sudo systemctl restart apache2
```

### Вариант 2: Временно упростить конфигурацию

```bash
# 1. Создайте временную простую конфигурацию только с HTTP
sudo cp /etc/apache2/sites-available/videoeditor.conf /etc/apache2/sites-available/videoeditor.conf.backup

# 2. Создайте простую конфигурацию только с HTTP
sudo nano /etc/apache2/sites-available/videoeditor.conf
```

Вставьте только HTTP VirtualHost:
```apache
<VirtualHost *:80>
    ServerName videoeditor.1tlt.ru
    ServerAlias www.videoeditor.1tlt.ru
    DocumentRoot /ssd/www/videoeditor/public
    
    <Directory /ssd/www/videoeditor/public>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
        
        <FilesMatch \.php$>
            SetHandler "proxy:fcgi://127.0.0.1:9000"
        </FilesMatch>
    </Directory>
    
    ErrorLog ${APACHE_LOG_DIR}/videoeditor_error.log
    CustomLog ${APACHE_LOG_DIR}/videoeditor_access.log combined
</VirtualHost>
```

```bash
# 3. Перезапустите Apache
sudo systemctl restart apache2

# 4. Запустите certbot (теперь он сможет автоматически настроить)
sudo certbot --apache -d videoeditor.1tlt.ru

# 5. Восстановите полную конфигурацию
cd /ssd/www/videoeditor
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf
sudo systemctl restart apache2
```

### Вариант 3: Использовать webroot (самый надежный)

```bash
# 1. Получите сертификат через webroot
sudo certbot certonly --webroot -w /ssd/www/videoeditor/public -d videoeditor.1tlt.ru

# 2. Настройте Apache вручную (конфигурация уже готова)
cd /ssd/www/videoeditor
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf

# 3. Включите модули
sudo a2enmod ssl rewrite proxy proxy_fcgi

# 4. Проверьте и перезапустите
sudo apache2ctl configtest
sudo systemctl restart apache2
```

## Проверка

```bash
# Проверьте сертификат
sudo certbot certificates

# Проверьте в браузере
# https://videoeditor.1tlt.ru - должен быть зеленый замочек
# http://videoeditor.1tlt.ru - должен редиректить на HTTPS
```

## Обновление сертификата

Certbot автоматически обновляет сертификаты. Проверьте:

```bash
# Статус автоматического обновления
sudo systemctl status certbot.timer

# Ручное обновление
sudo certbot renew
```
