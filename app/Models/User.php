<?php

namespace App\Models;

use App\Core\Database;

class User
{
    public static function findById(int $id): ?array
    {
        return Database::fetchOne(
            "SELECT * FROM users WHERE id = ? AND deleted_at IS NULL",
            [$id]
        );
    }

    public static function findByEmail(string $email): ?array
    {
        return Database::fetchOne(
            "SELECT * FROM users WHERE email = ? AND deleted_at IS NULL",
            [$email]
        );
    }

    public static function create(array $data): int
    {
        Database::query(
            "INSERT INTO users (email, password_hash, role, status, email_verified) 
             VALUES (?, ?, ?, ?, ?)",
            [
                $data['email'],
                $data['password_hash'],
                $data['role'] ?? 'user',
                $data['status'] ?? 'active',
                $data['email_verified'] ?? 0,
            ]
        );

        $userId = (int) Database::lastInsertId();

        // Create profile
        Database::query(
            "INSERT INTO user_profiles (user_id) VALUES (?)",
            [$userId]
        );

        // Create balance
        Database::query(
            "INSERT INTO balances (user_id, credits) VALUES (?, ?)",
            [$userId, $data['initial_credits'] ?? 0]
        );

        return $userId;
    }

    public static function update(int $id, array $data): bool
    {
        $fields = [];
        $params = [];

        foreach ($data as $key => $value) {
            $fields[] = "{$key} = ?";
            $params[] = $value;
        }

        if (empty($fields)) {
            return false;
        }

        $params[] = $id;
        $sql = "UPDATE users SET " . implode(', ', $fields) . " WHERE id = ?";

        return Database::execute($sql, $params) > 0;
    }

    public static function getAll(int $limit = 100, int $offset = 0): array
    {
        return Database::fetchAll(
            "SELECT u.*, up.first_name, up.last_name, b.credits 
             FROM users u
             LEFT JOIN user_profiles up ON u.id = up.user_id
             LEFT JOIN balances b ON u.id = b.user_id
             WHERE u.deleted_at IS NULL
             ORDER BY u.created_at DESC
             LIMIT ? OFFSET ?",
            [$limit, $offset]
        );
    }

    public static function count(): int
    {
        $result = Database::fetchOne(
            "SELECT COUNT(*) as count FROM users WHERE deleted_at IS NULL"
        );
        return (int) ($result['count'] ?? 0);
    }
}
