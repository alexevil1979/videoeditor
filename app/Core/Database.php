<?php

namespace App\Core;

use PDO;
use PDOException;

/**
 * Класс для работы с базой данных
 * Использует паттерн Singleton для единого подключения
 * Все запросы используют подготовленные запросы для защиты от SQL инъекций
 */
class Database
{
    private static ?PDO $instance = null;

    /**
     * Получает экземпляр подключения к базе данных (Singleton)
     * @return PDO
     * @throws \RuntimeException При ошибке подключения
     */
    public static function getInstance(): PDO
    {
        if (self::$instance === null) {
            $host = Config::get('database.host');
            $port = Config::get('database.port', 3306);
            $name = Config::get('database.name');
            $user = Config::get('database.user');
            $password = Config::get('database.password');
            $charset = Config::get('database.charset', 'utf8mb4');

            $dsn = "mysql:host={$host};port={$port};dbname={$name};charset={$charset}";

            $options = [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES => false,
                PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES {$charset}",
            ];

            try {
                self::$instance = new PDO($dsn, $user, $password, $options);
            } catch (PDOException $e) {
                throw new \RuntimeException("Ошибка подключения к базе данных: " . $e->getMessage());
            }
        }

        return self::$instance;
    }

    public static function query(string $sql, array $params = []): \PDOStatement
    {
        $db = self::getInstance();
        $stmt = $db->prepare($sql);
        $stmt->execute($params);
        return $stmt;
    }

    public static function fetchAll(string $sql, array $params = []): array
    {
        return self::query($sql, $params)->fetchAll();
    }

    public static function fetchOne(string $sql, array $params = []): ?array
    {
        $result = self::query($sql, $params)->fetch();
        return $result ?: null;
    }

    public static function execute(string $sql, array $params = []): int
    {
        return self::query($sql, $params)->rowCount();
    }

    public static function lastInsertId(): string
    {
        return self::getInstance()->lastInsertId();
    }

    public static function beginTransaction(): bool
    {
        return self::getInstance()->beginTransaction();
    }

    public static function commit(): bool
    {
        return self::getInstance()->commit();
    }

    public static function rollback(): bool
    {
        return self::getInstance()->rollBack();
    }
}
