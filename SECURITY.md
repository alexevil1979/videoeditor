# Security Notes

## Authentication & Authorization

1. **Password Hashing**: Uses PHP's `password_hash()` with bcrypt (default algorithm)
2. **Session Security**: 
   - Session IDs regenerated on login
   - Sessions stored in database for tracking
   - Session lifetime: 2 hours (configurable)
3. **Role-Based Access**: Admin and user roles enforced via middleware
4. **CSRF Protection**: Should be implemented for all POST requests (recommended: add CSRF tokens)

## File Upload Security

1. **File Type Validation**: Only allowed video formats accepted
2. **File Size Limits**: Enforced at application and server level (Nginx)
3. **Path Traversal Protection**: File paths sanitized, no user input in paths
4. **Storage Isolation**: Uploads stored outside web root
5. **File Content Validation**: Consider adding MIME type checking

## Database Security

1. **Prepared Statements**: All queries use PDO prepared statements
2. **SQL Injection**: Protected via parameterized queries
3. **Database User**: Limited privileges (only to application database)
4. **Connection Security**: Consider using SSL for MySQL connections in production

## Input Validation

1. **Email Validation**: Basic email format checking
2. **Password Requirements**: Minimum 8 characters (configurable)
3. **File Upload Validation**: Type, size, and error checking
4. **XSS Protection**: Output escaped in views using `htmlspecialchars()`

## Server Security

1. **Nginx Configuration**: 
   - Blocks access to sensitive directories
   - Limits upload size
   - Security headers included
2. **PHP Configuration**: 
   - `display_errors` should be off in production
   - `expose_php` should be off
   - File upload limits configured
3. **File Permissions**: 
   - Storage directories: 775 (www-data:www-data)
   - Application files: 755
   - Config files: 600 (should not be in web root)

## Recommendations for Production

1. **HTTPS**: Enforce HTTPS for all connections
2. **Rate Limiting**: Implement rate limiting for API endpoints
3. **Logging**: Monitor failed login attempts, suspicious activity
4. **Backup**: Regular database and file backups
5. **Updates**: Keep PHP, MySQL, Nginx, and FFmpeg updated
6. **Firewall**: Configure UFW or iptables
7. **SSH**: Disable root login, use key-based authentication
8. **Environment Variables**: Move sensitive config to environment variables
9. **CSRF Tokens**: Implement CSRF protection for forms
10. **Content Security Policy**: Add CSP headers
11. **Two-Factor Authentication**: Consider adding 2FA for admin accounts
12. **Audit Logging**: Log all admin actions

## Worker Security

1. **Process Isolation**: Worker runs as www-data user
2. **Resource Limits**: Memory and file descriptor limits set
3. **Error Handling**: Failures logged, jobs retried with limits
4. **Timeout Protection**: Jobs timeout after configured duration

## Known Limitations

- No CSRF token implementation (should be added)
- No rate limiting (should be added)
- Basic file validation (consider adding virus scanning)
- No IP whitelisting for admin (consider adding)
- Session fixation protection could be enhanced
