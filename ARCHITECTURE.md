# Video Editor SaaS - Architecture Overview

## System Architecture

### High-Level Overview
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Nginx     │────▶│   PHP-FPM    │────▶│   MySQL     │
│  (Port 80)  │     │  (Port 9000) │     │  (Port 3306)│
└─────────────┘     └──────────────┘     └─────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   FFmpeg     │
                    │  (Local CLI) │
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ Queue Worker │
                    │ (systemd)    │
                    └──────────────┘
```

### Technology Stack
- **Backend**: PHP 8.1+ (Object-oriented, PSR-4 autoloading)
- **Database**: MySQL 8.0+
- **Web Server**: Nginx + PHP-FPM
- **Video Processing**: FFmpeg (server-side)
- **Queue System**: MySQL-based job queue with CLI worker
- **Authentication**: Session-based with role system
- **Storage**: Local filesystem (extensible to S3)

### Directory Structure
```
/
├── app/
│   ├── Controllers/      # Request handlers
│   ├── Models/          # Database models
│   ├── Services/        # Business logic
│   ├── Middleware/      # Auth, validation
│   ├── Core/            # Base classes, config
│   └── Helpers/         # Utility functions
├── public/              # Web root (Nginx document root)
│   ├── index.php        # Entry point
│   ├── assets/          # CSS, JS, images
│   └── uploads/         # User uploads (symlink)
├── storage/
│   ├── uploads/         # Original videos
│   ├── renders/         # Processed videos
│   ├── logs/            # Application logs
│   └── cache/           # Temporary files
├── config/              # Configuration files
├── database/            # SQL migrations
├── scripts/             # Deployment, worker scripts
├── tests/               # Unit tests (optional)
└── vendor/              # Composer dependencies
```

### Request Flow
1. **User Request** → Nginx → `public/index.php`
2. **Router** → Parses URL, determines controller/action
3. **Middleware** → Authentication, validation
4. **Controller** → Handles request, calls services
5. **Service** → Business logic, database operations
6. **Model** → Database abstraction
7. **Response** → JSON or HTML template

### Video Processing Flow
1. **Upload** → File validated, stored in `storage/uploads/`
2. **Job Creation** → Record inserted into `render_jobs` table
3. **Queue** → Worker picks up job (status: `pending`)
4. **Processing** → FFmpeg renders video with overlays
5. **Completion** → Output saved to `storage/renders/`
6. **Notification** → User notified, job status updated

### Queue System
- **Storage**: MySQL table `render_jobs`
- **Worker**: CLI PHP script (`scripts/worker.php`)
- **Process**: systemd service runs worker continuously
- **Locking**: Database row-level locking prevents duplicate processing
- **Retries**: Automatic retry on failure (max 3 attempts)

### Security Layers
1. **Authentication**: Session-based with secure cookies
2. **Authorization**: Role-based access control (admin/user)
3. **File Validation**: Type, size, content checks
4. **SQL Injection**: Prepared statements only
5. **XSS Protection**: Output escaping
6. **CSRF Protection**: Token validation
7. **Path Traversal**: Sanitized file paths
8. **Rate Limiting**: Per-user upload limits

### Database Design
- **Normalized**: 3NF compliance
- **Indexes**: Optimized for common queries
- **Foreign Keys**: Referential integrity
- **Soft Deletes**: Preserve data history

### Deployment Strategy
- **Git-based**: Push to main triggers deployment
- **Zero Downtime**: Blue-green deployment pattern
- **Worker Persistence**: Workers continue during deploy
- **Rollback**: Git revert + redeploy

### Scalability Considerations
- **Horizontal Scaling**: Multiple workers possible
- **Storage**: Can migrate to S3/Object Storage
- **Queue**: Can migrate to Redis/RabbitMQ
- **Caching**: Ready for Redis integration
- **CDN**: Static assets can be served via CDN
