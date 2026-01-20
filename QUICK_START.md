# Quick Start Guide

## Repository
- **GitHub**: https://github.com/alexevil1979/videoeditor
- **Server Path**: `/ssd/www/videoeditor`

## ⚠️ Important: PHP Extensions

Before installing dependencies, ensure **required** PHP extensions are installed:
```bash
# Required extensions
sudo apt install -y php8.1-mbstring php8.1-mysql
php -m | grep -E "mbstring|pdo_mysql"  # Verify

# Optional: GD for image overlay buttons
# sudo apt install -y php8.1-gd
# php -m | grep gd
```

**Note**: Without GD the app works, but Subscribe/Like buttons will be text overlays instead of images.

If Composer shows errors about missing extensions, see `INSTALL_PHP_EXTENSIONS.md`

## For Developers

### Local Development Setup

1. **Clone repository:**
   ```bash
   git clone https://github.com/alexevil1979/videoeditor.git
   cd videoeditor
   ```

2. **Install dependencies:**
   ```bash
   composer install
   ```

3. **Configure:**
   ```bash
   cp config/config.example.php config/config.php
   # Edit config/config.php (database, paths, etc.)
   ```

4. **Setup database:**
   ```bash
   # Create database in MySQL
   mysql -u root -p
   # CREATE DATABASE video_overlay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   # CREATE USER 'video_user'@'localhost' IDENTIFIED BY 'your_password';
   # GRANT ALL PRIVILEGES ON video_overlay.* TO 'video_user'@'localhost';
   # FLUSH PRIVILEGES;
   
   # Run migrations
   php scripts/migrate.php
   ```

5. **Run PHP built-in server:**
   ```bash
   php -S localhost:8000 -t public
   ```

6. **Run worker (separate terminal):**
   ```bash
   php scripts/worker.php
   ```

7. **Access:**
   - Application: http://localhost:8000
   - Admin: admin@example.com / admin123
   - ⚠️ **IMPORTANT**: Change admin password after first login!

## For Production Deployment

### Quick Setup on VPS (Ubuntu)

```bash
# 1. Install dependencies
sudo apt update
sudo apt install -y php8.1-fpm php8.1-mysql php8.1-mbstring apache2 libapache2-mod-php8.1 mysql-server ffmpeg git composer

# Optional: Install GD for image overlay buttons
# sudo apt install -y php8.1-gd

# Verify PHP extensions
php -m | grep -E "pdo_mysql|mbstring"

# If extensions are missing, install them:
# sudo apt install -y php8.1-mbstring
# sudo systemctl restart php8.1-fpm

# 2. Clone repository
cd /ssd/www
git clone https://github.com/alexevil1979/videoeditor.git videoeditor
cd videoeditor

# 3. Install PHP dependencies
composer install --no-dev --optimize-autoloader

# 4. Configure
cp config/config.example.php config/config.php
nano config/config.php  # Edit database settings and paths

# 5. Setup database
mysql -u root -p
# CREATE DATABASE video_overlay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# CREATE USER 'video_user'@'localhost' IDENTIFIED BY 'your_password';
# GRANT ALL PRIVILEGES ON video_overlay.* TO 'video_user'@'localhost';
# FLUSH PRIVILEGES;

# 6. Setup database
# Create database in MySQL (if not exists):
# mysql -u root -p
# CREATE DATABASE video_overlay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# CREATE USER 'video_user'@'localhost' IDENTIFIED BY 'your_password';
# GRANT ALL PRIVILEGES ON video_overlay.* TO 'video_user'@'localhost';
# FLUSH PRIVILEGES;

# Configure config.php
cp config/config.example.php config/config.php
nano config/config.php  # Set database credentials

# Run migrations
php scripts/migrate.php

# 7. Set permissions
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage

# 8. Configure Apache
sudo a2enmod rewrite php8.1 expires deflate
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf
sudo nano /etc/apache2/sites-available/videoeditor.conf  # Update ServerName to videoeditor.1tlt.ru
sudo a2ensite videoeditor.conf
sudo a2dissite 000-default.conf  # Optional: disable default site
sudo apache2ctl configtest
sudo systemctl restart apache2

# 9. Setup worker
sudo cp scripts/video-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable video-worker
sudo systemctl start video-worker
sudo systemctl status video-worker

# 10. Done! Open your domain in browser
```

## Key URLs

- `/` - Home (redirects to login/dashboard)
- `/login` - User login
- `/register` - User registration
- `/dashboard` - User dashboard
- `/admin` - Admin dashboard
- `/lang/{code}` - Switch language (en, ru, th, zh)
- `/api/videos/upload` - Upload video (POST)
- `/api/videos/render` - Create render job (POST)
- `/api/videos/download/{id}` - Download rendered video
- `/api/presets` - Manage presets

## Default Credentials

**Admin:**
- Email: `admin@example.com`
- Password: `admin123`

**⚠️ CHANGE IMMEDIATELY AFTER FIRST LOGIN!**

## Common Tasks

### Add Credits to User
1. Login as admin
2. Go to Admin → Users
3. Click "Edit Balance"
4. Enter amount (positive to add, negative to subtract)

### Create Preset
Use API or add directly to database:
```sql
INSERT INTO presets (user_id, name, is_global) VALUES (NULL, 'My Preset', 1);
INSERT INTO preset_items (preset_id, type, position_x, position_y, text) 
VALUES (LAST_INSERT_ID(), 'title', 'center', 'top', 'My Video Title');
```

### Switch Interface Language
- Use dropdown in top right navigation
- Or visit URL: `/lang/ru` (en, ru, th, zh)
- Language is saved in session and user profile

### Check Queue Status
```bash
mysql -u video_user -p video_overlay -e "SELECT status, COUNT(*) FROM render_jobs GROUP BY status;"
```

### View Worker Logs
```bash
sudo journalctl -u video-worker -f
```

### Restart Worker
```bash
sudo systemctl restart video-worker
```

### Update Project (after repository changes)
```bash
cd /ssd/www/videoeditor
git pull origin main
composer install --no-dev --optimize-autoloader
php scripts/migrate.php
sudo systemctl reload php8.1-fpm
sudo systemctl restart apache2
sudo systemctl restart video-worker
```

## Testing Video Processing

1. Register or login to system
2. Upload a test video (MP4, MOV, AVI, MKV, WEBM)
3. Create or select an overlay preset
4. Click "Render" (processing)
5. Wait for processing (check job status in dashboard)
6. Download completed video after finish

### Supported Formats
- Video: MP4, MOV, AVI, MKV, WEBM
- Max size: 100MB (configurable)
- Max duration: 5 minutes (configurable)

### Overlay Types
- **Subscribe** - Subscribe button
- **Like** - Like button
- **Title** - Video title text

## Troubleshooting

### Worker Not Processing
```bash
# Check status
sudo systemctl status video-worker

# Check logs
sudo journalctl -u video-worker -n 50

# Verify FFmpeg
ffmpeg -version

# Restart worker
sudo systemctl restart video-worker
```

### Upload Fails
```bash
# Check limits in Apache
sudo nano /etc/apache2/sites-available/videoeditor.conf
# LimitRequestBody 104857600

# Check limits in PHP
php -i | grep upload_max_filesize
php -i | grep post_max_size

# Check permissions
sudo chown -R www-data:www-data /ssd/www/videoeditor/storage
sudo chmod -R 775 /ssd/www/videoeditor/storage
```

### Database Errors
```bash
# Check credentials
nano /ssd/www/videoeditor/config/config.php

# Test connection
mysql -u video_user -p video_overlay

# Check MySQL status
sudo systemctl status mysql
```

### Translation Issues
- Ensure files exist in `lang/` (en.php, ru.php, th.php, zh.php)
- Check file permissions: `ls -la lang/`
- Clear browser cache

### FFmpeg Issues
```bash
# Install FFmpeg if missing
sudo apt install ffmpeg

# Check version
ffmpeg -version

# Check path in config
grep ffmpeg /ssd/www/videoeditor/config/config.php
```
