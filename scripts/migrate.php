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
            $result = Database::getInstance()->exec($statement);
            if ($result !== false) {
                echo "✓ Executed: " . substr(trim($statement), 0, 60) . "...\n";
            }
        } catch (\PDOException $e) {
            // Ignore "table already exists" errors
            if (strpos($e->getMessage(), 'already exists') !== false) {
                echo "⊘ Skipped (already exists): " . substr(trim($statement), 0, 60) . "...\n";
                continue;
            }
            // Show errors
            echo "✗ Error: " . $e->getMessage() . "\n";
            echo "  Statement: " . substr(trim($statement), 0, 100) . "...\n";
        }
    }

    Database::getInstance()->commit();
    
    // Verify tables were created
    $tables = Database::query("SHOW TABLES")->fetchAll(\PDO::FETCH_COLUMN);
    echo "\nDatabase schema loaded!\n";
    echo "Tables created: " . count($tables) . "\n";
    if (count($tables) > 0) {
        echo "Table list: " . implode(', ', $tables) . "\n";
    } else {
        echo "⚠️  WARNING: No tables found! Check database connection and permissions.\n";
    }
} catch (\Exception $e) {
    Database::getInstance()->rollBack();
    die("Error: " . $e->getMessage() . "\n");
}
