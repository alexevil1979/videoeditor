<?php

/**
 * Database Migration Script
 * Run this to set up the database schema
 */

require_once __DIR__ . '/../vendor/autoload.php';

use App\Core\Config;
use App\Core\Database;

Config::load(__DIR__ . '/../config/config.php');

$schemaFile = __DIR__ . '/../database/schema.sql';

if (!file_exists($schemaFile)) {
    die("Schema file not found: {$schemaFile}\n");
}

echo "Loading schema...\n";

$sql = file_get_contents($schemaFile);

// Split by semicolons (basic approach)
$statements = array_filter(
    array_map('trim', explode(';', $sql)),
    function($stmt) {
        return !empty($stmt) && !preg_match('/^--/', $stmt);
    }
);

try {
    Database::getInstance()->beginTransaction();

    foreach ($statements as $statement) {
        if (empty(trim($statement))) {
            continue;
        }
        
        try {
            Database::getInstance()->exec($statement);
        } catch (\PDOException $e) {
            // Ignore "table already exists" errors
            if (strpos($e->getMessage(), 'already exists') === false) {
                throw $e;
            }
        }
    }

    Database::getInstance()->commit();
    echo "Database schema loaded successfully!\n";
} catch (\Exception $e) {
    Database::getInstance()->rollBack();
    die("Error: " . $e->getMessage() . "\n");
}
