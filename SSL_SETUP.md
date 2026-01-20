# Настройка SSL через Certbot для videoeditor.1tlt.ru

## Установка Certbot

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-apache
```

## Настройка SSL сертификата

### Автоматическая настройка (рекомендуется)

```bash
sudo certbot --apache -d videoeditor.1tlt.ru
```

Certbot автоматически:
- Получит SSL сертификат от Let's Encrypt
- Настроит Apache для HTTPS
- Настроит автоматическое обновление сертификата

### Ручная настройка (если автоматическая не работает)

```bash
# Получить сертификат
sudo certbot certonly --apache -d videoeditor.1tlt.ru

# Настроить Apache вручную
sudo nano /etc/apache2/sites-available/videoeditor.conf
```

Добавьте в конфигурацию:
```apache
<VirtualHost *:443>
    ServerName videoeditor.1tlt.ru
    ServerAlias www.videoeditor.1tlt.ru
    
    DocumentRoot /ssd/www/videoeditor/public
    
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/videoeditor.1tlt.ru/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/videoeditor.1tlt.ru/privkey.pem
    
    <Directory /ssd/www/videoeditor/public>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    
    ErrorLog ${APACHE_LOG_DIR}/videoeditor_ssl_error.log
    CustomLog ${APACHE_LOG_DIR}/videoeditor_ssl_access.log combined
    
    LimitRequestBody 104857600
    
    php_value upload_max_filesize 100M
    php_value post_max_size 100M
    php_value max_execution_time 300
    php_value memory_limit 512M
</VirtualHost>

# Редирект с HTTP на HTTPS
<VirtualHost *:80>
    ServerName videoeditor.1tlt.ru
    ServerAlias www.videoeditor.1tlt.ru
    Redirect permanent / https://videoeditor.1tlt.ru/
</VirtualHost>
```

```bash
# Включите SSL модуль
sudo a2enmod ssl

# Перезапустите Apache
sudo apache2ctl configtest
sudo systemctl restart apache2
```

## Проверка SSL

```bash
# Проверить сертификат
sudo certbot certificates

# Проверить автоматическое обновление
sudo systemctl status certbot.timer

# Тестовое обновление
sudo certbot renew --dry-run
```

## Обновление сертификата

Certbot автоматически обновляет сертификаты. Проверьте:

```bash
# Статус таймера обновления
sudo systemctl status certbot.timer

# Ручное обновление (если нужно)
sudo certbot renew
```

## Обновление config.php для HTTPS

```bash
cd /ssd/www/videoeditor
nano config/config.php
```

Измените:
```php
'url' => 'https://videoeditor.1tlt.ru',
```

## Проверка

Откройте в браузере: `https://videoeditor.1tlt.ru`

Должен быть зеленый замочек и HTTPS соединение.
