<?php

namespace App\Models;

use App\Core\Database;

class Video
{
    public static function findById(int $id): ?array
    {
        return Database::fetchOne(
            "SELECT * FROM videos WHERE id = ? AND deleted_at IS NULL",
            [$id]
        );
    }

    public static function findByUser(int $userId, int $limit = 50, int $offset = 0): array
    {
        return Database::fetchAll(
            "SELECT * FROM videos 
             WHERE user_id = ? AND deleted_at IS NULL
             ORDER BY created_at DESC
             LIMIT ? OFFSET ?",
            [$userId, $limit, $offset]
        );
    }

    public static function create(array $data): int
    {
        Database::query(
            "INSERT INTO videos (user_id, original_filename, storage_path, file_size, status) 
             VALUES (?, ?, ?, ?, ?)",
            [
                $data['user_id'],
                $data['original_filename'],
                $data['storage_path'],
                $data['file_size'],
                $data['status'] ?? 'uploaded',
            ]
        );

        return (int) Database::lastInsertId();
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
        $sql = "UPDATE videos SET " . implode(', ', $fields) . " WHERE id = ?";

        return Database::execute($sql, $params) > 0;
    }

    public static function getAll(int $limit = 100, int $offset = 0): array
    {
        return Database::fetchAll(
            "SELECT v.*, u.email as user_email 
             FROM videos v
             LEFT JOIN users u ON v.user_id = u.id
             WHERE v.deleted_at IS NULL
             ORDER BY v.created_at DESC
             LIMIT ? OFFSET ?",
            [$limit, $offset]
        );
    }
}
