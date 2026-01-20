# Quick Start Guide

## For Developers

### Local Development Setup

1. **Install dependencies:**
   ```bash
   composer install
   ```

2. **Configure:**
   ```bash
   cp config/config.example.php config/config.php
   # Edit config/config.php
   ```

3. **Setup database:**
   ```bash
   php scripts/migrate.php
   ```

4. **Run PHP built-in server:**
   ```bash
   php -S localhost:8000 -t public
   ```

5. **Run worker (separate terminal):**
   ```bash
   php scripts/worker.php
   ```

6. **Access:**
   - Application: http://localhost:8000
   - Admin: admin@example.com / admin123

## For Production Deployment

### One-Command Setup (after initial server prep)

```bash
cd /ssd/www
git clone <repo-url> videoeditor
cd videoeditor
composer install --no-dev --optimize-autoloader
cp config/config.example.php config/config.php
# Edit config/config.php
php scripts/migrate.php
sudo chown -R www-data:www-data /ssd/www/videoeditor
sudo chmod -R 775 storage
sudo cp config/nginx.conf /etc/nginx/sites-available/videoeditor
sudo ln -s /etc/nginx/sites-available/videoeditor /etc/nginx/sites-enabled/
sudo cp scripts/video-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable video-worker
sudo systemctl start video-worker
sudo systemctl reload nginx
```

## Key URLs

- `/` - Home (redirects to login/dashboard)
- `/login` - User login
- `/register` - User registration
- `/dashboard` - User dashboard
- `/admin` - Admin dashboard
- `/api/videos/upload` - Upload video (POST)
- `/api/videos/render` - Create render job (POST)
- `/api/videos/download/{id}` - Download rendered video

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

## Testing Video Processing

1. Upload a test video (MP4, MOV, AVI, etc.)
2. Create or select a preset
3. Click "Render"
4. Wait for processing (check job status)
5. Download completed video

## Troubleshooting

**Worker not processing:**
- Check status: `sudo systemctl status video-worker`
- Check logs: `sudo journalctl -u video-worker -n 50`
- Verify FFmpeg: `ffmpeg -version`

**Upload fails:**
- Check file size limits in Nginx and PHP
- Verify storage directory permissions
- Check PHP error logs

**Database errors:**
- Verify credentials in `config/config.php`
- Test connection: `mysql -u video_user -p video_overlay`
