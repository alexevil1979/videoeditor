# Project Structure

```
videoeditor/
├── app/
│   ├── Controllers/          # Request handlers
│   │   ├── AdminController.php
│   │   ├── AuthController.php
│   │   ├── DashboardController.php
│   │   ├── PresetController.php
│   │   └── VideoController.php
│   ├── Core/                 # Core framework classes
│   │   ├── Config.php        # Configuration manager
│   │   ├── Database.php      # Database abstraction
│   │   ├── Response.php       # HTTP response handler
│   │   ├── Router.php        # URL routing
│   │   └── Session.php       # Session management
│   ├── Middleware/           # Request middleware
│   │   ├── AdminMiddleware.php
│   │   └── AuthMiddleware.php
│   ├── Models/               # Database models
│   │   ├── Preset.php
│   │   ├── RenderJob.php
│   │   ├── User.php
│   │   └── Video.php
│   └── Services/             # Business logic
│       ├── AuthService.php
│       ├── FFmpegService.php # Video processing
│       └── VideoService.php
├── config/
│   ├── config.example.php    # Example configuration
│   └── nginx.conf            # Nginx virtual host
├── database/
│   └── schema.sql            # Database schema
├── public/                   # Web root (Nginx document root)
│   ├── index.php            # Application entry point
│   └── assets/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
├── scripts/
│   ├── deploy.sh            # Deployment script
│   ├── migrate.php          # Database migration
│   ├── video-worker.service # systemd service file
│   └── worker.php           # Queue worker
├── storage/                  # File storage
│   ├── uploads/            # Original videos
│   ├── renders/            # Processed videos
│   ├── logs/               # Application logs
│   └── cache/              # Temporary files
├── views/                   # HTML templates
│   ├── admin/
│   │   ├── dashboard.php
│   │   ├── jobs.php
│   │   └── users.php
│   ├── auth/
│   │   ├── login.php
│   │   └── register.php
│   ├── dashboard/
│   │   └── index.php
│   └── layout.php
├── .github/
│   └── workflows/
│       └── deploy.yml       # GitHub Actions CI/CD
├── .gitignore
├── ARCHITECTURE.md          # System architecture
├── composer.json            # PHP dependencies
├── DEPLOYMENT.md            # Deployment guide
├── PROJECT_STRUCTURE.md     # This file
├── README.md                # Main documentation
└── SECURITY.md              # Security notes
```

## Key Files

### Entry Point
- `public/index.php` - Main application entry, routes requests

### Configuration
- `config/config.example.php` - Copy to `config/config.php` and configure
- `config/nginx.conf` - Nginx virtual host configuration

### Database
- `database/schema.sql` - Complete database schema
- `scripts/migrate.php` - Run to initialize database

### Workers
- `scripts/worker.php` - Queue worker (runs via systemd)
- `scripts/video-worker.service` - systemd service file

### Deployment
- `scripts/deploy.sh` - Manual deployment script
- `.github/workflows/deploy.yml` - Automated CI/CD

## File Permissions

On Linux server:
```bash
# Application files
chmod 755 -R /ssd/www/videoeditor
chown www-data:www-data -R /ssd/www/videoeditor

# Storage directories (writable)
chmod 775 -R /ssd/www/videoeditor/storage
```

## Environment Variables

All configuration is in `config/config.php`. For production, consider moving sensitive data to environment variables.

## Dependencies

- PHP 8.1+ with extensions: pdo_mysql, gd, mbstring, zip
- MySQL 8.0+
- Nginx
- FFmpeg
- Composer (for autoloading)
