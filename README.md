# Video Overlay SaaS Platform

Automated video processing platform for adding motivational CTAs (Subscribe, Like, Video Title) to short-form videos.

## Features

- **User Management**: Registration, authentication, profiles
- **Video Processing**: FFmpeg-based overlay rendering
- **Preset System**: Reusable overlay configurations
- **Queue System**: Asynchronous job processing
- **Admin Panel**: Full management interface
- **Credit System**: Usage-based billing
- **History Tracking**: Upload and render history

## Requirements

- Ubuntu 20.04+ VPS
- PHP 8.1+ with extensions:
  - `php8.1-fpm` - PHP-FPM
  - `php8.1-mysql` - MySQL support (PDO)
  - `php8.1-mbstring` - String operations
  - `php8.1-gd` - Optional - Image generation for overlay buttons (Subscribe/Like). Without GD, buttons use text overlays.
- MySQL 8.0+
- Apache 2.4+ (or Nginx)
- FFmpeg (installed and in PATH)
- Git
- Composer

## Installation

### 1. Server Setup

```bash
# Install dependencies
sudo apt update
sudo apt install -y php8.1-fpm php8.1-mysql php8.1-mbstring apache2 libapache2-mod-php8.1 mysql-server ffmpeg git composer

# Optional: Install GD for image overlay buttons
# sudo apt install -y php8.1-gd

# Verify PHP extensions
php -m | grep -E "pdo_mysql|mbstring"

# If extensions are missing, install them:
# sudo apt install -y php8.1-gd php8.1-mbstring

# Create directories
sudo mkdir -p /ssd/www/videoeditor/{storage/{uploads,renders,logs,cache},public}
sudo chown -R www-data:www-data /ssd/www/videoeditor/storage
```

### 2. Database Setup

```bash
mysql -u root -p
```

```sql
CREATE DATABASE video_overlay CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'video_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON video_overlay.* TO 'video_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Application Setup

```bash
cd /ssd/www/videoeditor
git clone https://github.com/alexevil1979/videoeditor.git .
composer install --no-dev --optimize-autoloader
cp config/config.example.php config/config.php
# Edit config.php with database credentials
php scripts/migrate.php
```

### 4. Apache Configuration

```bash
# Enable required modules
sudo a2enmod rewrite
sudo a2enmod php8.1
sudo a2enmod expires
sudo a2enmod deflate

# Copy configuration
sudo cp config/apache.conf /etc/apache2/sites-available/videoeditor.conf

# Enable site
sudo a2ensite videoeditor.conf

# Disable default site (optional)
sudo a2dissite 000-default.conf

# Test configuration
sudo apache2ctl configtest

# Restart Apache
sudo systemctl restart apache2
```

See `config/apache.conf` for Apache virtual host configuration.

### 5. Worker Setup

```bash
sudo cp scripts/video-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable video-worker
sudo systemctl start video-worker
```

### 6. Permissions

```bash
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 755 /ssd/www/videoeditor
sudo chmod -R 775 /ssd/www/videoeditor/storage
```

## Configuration

Edit `config/config.php`:
- Database credentials
- Storage paths
- FFmpeg settings
- Security keys
- Credit pricing

## Usage

1. Access the application at `http://your-domain.com`
2. Register a new account
3. Upload a video
4. Select/create a preset
5. Process video
6. Download result

## Admin Access

Default admin credentials (change after first login):
- Email: admin@example.com
- Password: admin123

## Development

```bash
composer install
php scripts/migrate.php
php scripts/worker.php  # Run worker manually
```

## Documentation

- **ARCHITECTURE.md** - System architecture and design
- **INSTALLATION.md** - Detailed installation guide  
- **DEPLOYMENT.md** - Deployment and CI/CD guide
- **QUICK_START.md** - Quick reference guide
- **FEATURES.md** - Complete feature list
- **SECURITY.md** - Security documentation
- **PROJECT_STRUCTURE.md** - Project organization
- **IMPLEMENTATION_SUMMARY.md** - Implementation overview

## Recent Updates

- **2024**: Fixed Composer dependencies - removed hard PHP extension requirements
- **2024**: Added PHP extension installation guide (`INSTALL_PHP_EXTENSIONS.md`)
- **2024**: Added extension checks in FFmpegService with helpful error messages
- Multi-language support (English, Russian, Thai, Chinese)
- Repository: https://github.com/alexevil1979/videoeditor
- Server path: `/ssd/www/videoeditor`

## ⚠️ Important: PHP Extensions Required

Before installing Composer dependencies, ensure required PHP extensions are installed:
```bash
sudo apt install -y php8.1-mbstring php8.1-mysql
php -m | grep -E "mbstring|pdo_mysql"  # Verify

# Optional: Install GD for image overlay buttons
# sudo apt install -y php8.1-gd
```

See `INSTALL_PHP_EXTENSIONS.md` for detailed instructions.

## License

Proprietary - All rights reserved
