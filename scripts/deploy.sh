#!/bin/bash

# Deployment script for videoeditor SaaS
# Run this script on the server after git pull

set -e

APP_DIR="/ssd/www/videoeditor"
PHP_VERSION="8.1"

echo "Starting deployment..."

# Navigate to app directory
cd "$APP_DIR"

# Pull latest code
echo "Pulling latest code..."
git pull origin main

# Install/update dependencies
echo "Installing dependencies..."
composer install --no-dev --optimize-autoloader

# Run migrations (if any new)
echo "Running migrations..."
php scripts/migrate.php

# Set permissions
echo "Setting permissions..."
sudo chown -R www-data:www-data "$APP_DIR"
sudo chmod -R 755 "$APP_DIR"
sudo chmod -R 775 "$APP_DIR/storage"

# Clear cache (if any)
echo "Clearing cache..."
rm -rf "$APP_DIR/storage/cache/*"

# Reload services (no downtime)
echo "Reloading services..."
sudo systemctl reload php${PHP_VERSION}-fpm
sudo systemctl restart apache2

# Restart worker (graceful)
echo "Restarting worker..."
sudo systemctl restart video-worker

echo "Deployment completed successfully!"
