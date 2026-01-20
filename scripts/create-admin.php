<?php

/**
 * Script to create the first admin user
 * Usage: php scripts/create-admin.php
 */

require_once __DIR__ . '/../vendor/autoload.php';

use App\Core\Config;
use App\Core\Database;

Config::load(__DIR__ . '/../config/config.php');

echo "=== Create Admin User ===\n\n";

// Get input
echo "Enter email: ";
$email = trim(fgets(STDIN));

if (empty($email)) {
    die("Error: Email is required\n");
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    die("Error: Invalid email format\n");
}

echo "Enter password: ";
$password = trim(fgets(STDIN));

if (empty($password)) {
    die("Error: Password is required\n");
}

if (strlen($password) < 8) {
    die("Error: Password must be at least 8 characters\n");
}

echo "Enter first name (optional): ";
$firstName = trim(fgets(STDIN));
$firstName = empty($firstName) ? null : $firstName;

echo "Enter last name (optional): ";
$lastName = trim(fgets(STDIN));
$lastName = empty($lastName) ? null : $lastName;

try {
    Database::getInstance()->beginTransaction();
    
    // Check if user already exists
    $existing = Database::fetchOne(
        "SELECT id FROM users WHERE email = ?",
        [$email]
    );
    
    if ($existing) {
        die("Error: User with email '{$email}' already exists\n");
    }
    
    // Create user
    $hashedPassword = password_hash($password, PASSWORD_DEFAULT);
    
    Database::query(
        "INSERT INTO users (email, password_hash, role, created_at) VALUES (?, ?, 'admin', NOW())",
        [$email, $hashedPassword]
    );
    
    $userId = Database::getInstance()->lastInsertId();
    
    // Create profile
    Database::query(
        "INSERT INTO user_profiles (user_id, first_name, last_name, language, created_at) VALUES (?, ?, ?, 'en', NOW())",
        [$userId, $firstName, $lastName]
    );
    
    // Create balance
    Database::query(
        "INSERT INTO balances (user_id, credits, created_at) VALUES (?, 0, NOW())",
        [$userId]
    );
    
    Database::getInstance()->commit();
    
    echo "\n✓ Admin user created successfully!\n";
    echo "Email: {$email}\n";
    echo "Role: admin\n";
    echo "User ID: {$userId}\n\n";
    echo "You can now login at: https://videoeditor.1tlt.ru/login\n";
    
} catch (\Exception $e) {
    Database::getInstance()->rollBack();
    die("Error: " . $e->getMessage() . "\n");
}
