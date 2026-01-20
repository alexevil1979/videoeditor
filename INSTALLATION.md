# Installation Guide

## Quick Start

### 1. Prerequisites

- Ubuntu 20.04+ VPS
- Root or sudo access
- Domain name (optional, can use IP)

### 2. Install System Dependencies

```bash
sudo apt update
sudo apt install -y php8.1-fpm php8.1-mysql php8.1-mbstring apache2 libapache2-mod-php8.1 mysql-server ffmpeg git composer

# Optional: Install GD for image overlay buttons
# sudo apt install -y php8.1-gd

# Verify PHP extensions
php -m | grep -E "pdo_mysql|mbstring"

# If extensions are missing:
# sudo apt install -y php8.1-mbstring
# sudo systemctl restart php8.1-fpm
```

### 3. Setup Database

```bash
sudo mysql
```

```sql
CREATE DATABASE video_overlay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'video_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON video_overlay.* TO 'video_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. Clone and Setup Application

```bash
cd /ssd/www
sudo git clone https://github.com/alexevil1979/videoeditor.git videoeditor
cd videoeditor
sudo composer install --no-dev --optimize-autoloader
```

### 5. Configure Application

```bash
sudo cp config/config.example.php config/config.php
sudo nano config/config.php
```

Update database credentials and other settings.

### 6. Initialize Database

```bash
sudo php scripts/migrate.php
```

### 7. Set Permissions

```bash
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage
```

### 8. Configure Nginx

```bash
sudo a2enmod rewrite php8.1 expires deflate
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf
sudo nano /etc/apache2/sites-available/videoeditor.conf
# Update ServerName to videoeditor.1tlt.ru
sudo a2ensite videoeditor.conf
sudo a2dissite 000-default.conf
sudo apache2ctl configtest
sudo systemctl restart apache2
```

### 9. Setup Worker Service

```bash
sudo cp scripts/video-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable video-worker
sudo systemctl start video-worker
sudo systemctl status video-worker
```

### 10. Verify Installation

1. Visit your domain/IP in browser
2. Register a new account
3. Login with admin credentials:
   - Email: `admin@example.com`
   - Password: `admin123`
4. **IMPORTANT**: Change admin password immediately!

## Post-Installation

### SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-apache
sudo certbot --apache -d videoeditor.1tlt.ru
```

### Firewall Setup

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Backup Setup

Create a backup script:

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u video_user -p video_overlay > /backup/db_$DATE.sql
tar -czf /backup/storage_$DATE.tar.gz /ssd/www/videoeditor/storage
```

Add to crontab:
```bash
0 2 * * * /path/to/backup.sh
```

## Troubleshooting

### Worker Not Running

```bash
sudo systemctl status video-worker
sudo journalctl -u video-worker -n 50
```

### FFmpeg Not Found

```bash
which ffmpeg
ffmpeg -version
# If not found, install: sudo apt install ffmpeg
```

### Permission Errors

```bash
sudo chown -R www-data:www-data /ssd/www/videoeditor/storage
sudo chmod -R 775 /ssd/www/videoeditor/storage
```

### Database Connection

```bash
mysql -u video_user -p video_overlay
# Test connection
```

### Apache Errors

```bash
sudo apache2ctl configtest
sudo tail -f /var/log/apache2/videoeditor_error.log
sudo tail -f /var/log/apache2/error.log
```

## Production Checklist

- [ ] Changed admin password
- [ ] Configured SSL certificate
- [ ] Set up firewall
- [ ] Configured backups
- [ ] Updated `config/config.php` with production settings
- [ ] Set `debug` to `false` in config
- [ ] Configured domain name
- [ ] Tested video upload and processing
- [ ] Monitored worker logs
- [ ] Set up monitoring/alerting (optional)
