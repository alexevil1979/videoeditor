# Deployment Guide

## Initial Server Setup

### 1. Install Dependencies

```bash
sudo apt update
sudo apt install -y php8.1-fpm php8.1-mysql php8.1-mbstring apache2 libapache2-mod-php8.1 mysql-server ffmpeg git composer

# Optional: Install GD for image overlay buttons
# sudo apt install -y php8.1-gd
```

### 2. Configure MySQL

```bash
sudo mysql_secure_installation
```

Create database and user:
```sql
CREATE DATABASE video_overlay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'video_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON video_overlay.* TO 'video_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Clone Repository

```bash
cd /ssd/www
sudo git clone https://github.com/alexevil1979/videoeditor.git videoeditor
sudo chown -R www-data:www-data videoeditor
cd videoeditor
```

### 4. Install PHP Dependencies

```bash
composer install --no-dev --optimize-autoloader
```

### 5. Configure Application

```bash
cp config/config.example.php config/config.php
# Edit config/config.php with your database credentials
```

### 6. Run Database Migrations

```bash
php scripts/migrate.php
```

### 7. Set Permissions

```bash
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage
```

### 8. Configure Apache

```bash
sudo a2enmod rewrite php8.1 expires deflate
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf
sudo nano /etc/apache2/sites-available/videoeditor.conf  # Update ServerName to videoeditor.1tlt.ru
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

## CI/CD Setup

### GitHub Actions

1. Add secrets to GitHub repository:
   - `SSH_HOST`: Your server IP or domain
   - `SSH_USER`: SSH username (usually `root` or `ubuntu`)
   - `SSH_KEY`: Private SSH key for deployment

2. Push to `main` branch triggers automatic deployment

### Manual Deployment

```bash
cd /ssd/www/videoeditor
bash scripts/deploy.sh
```

## Post-Deployment

1. **Change Admin Password**: Login with default credentials and change immediately
2. **Configure Domain**: Update Apache config with domain name (videoeditor.1tlt.ru)
3. **SSL Certificate**: Install Let's Encrypt certificate
4. **Firewall**: Configure UFW to allow only necessary ports
5. **Backup**: Set up automated backups for database and storage

## Monitoring

- Check worker status: `sudo systemctl status video-worker`
- View worker logs: `sudo journalctl -u video-worker -f`
- Check Apache logs: `sudo tail -f /var/log/apache2/videoeditor_error.log`
- Monitor queue: Check admin dashboard

## Troubleshooting

### Worker Not Processing Jobs
- Check worker status: `sudo systemctl status video-worker`
- Check logs: `sudo journalctl -u video-worker -n 50`
- Verify FFmpeg: `which ffmpeg`
- Check permissions on storage directories: `ls -la /ssd/www/videoeditor/storage`

### Upload Failures
- Check Apache `LimitRequestBody` in config/apache.conf
- Check PHP `upload_max_filesize` and `post_max_size`
- Verify storage directory permissions

### Database Connection Errors
- Verify credentials in `config/config.php`
- Check MySQL service: `sudo systemctl status mysql`
- Test connection: `mysql -u video_user -p video_overlay`
