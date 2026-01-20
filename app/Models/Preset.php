<?php

namespace App\Models;

use App\Core\Database;

class Preset
{
    public static function findById(int $id): ?array
    {
        return Database::fetchOne(
            "SELECT * FROM presets WHERE id = ? AND deleted_at IS NULL",
            [$id]
        );
    }

    public static function findByUser(int $userId): array
    {
        return Database::fetchAll(
            "SELECT * FROM presets 
             WHERE (user_id = ? OR is_global = 1) AND deleted_at IS NULL
             ORDER BY is_global DESC, created_at DESC",
            [$userId]
        );
    }

    public static function getGlobal(): array
    {
        return Database::fetchAll(
            "SELECT * FROM presets 
             WHERE is_global = 1 AND deleted_at IS NULL
             ORDER BY created_at DESC"
        );
    }

    public static function create(array $data): int
    {
        Database::query(
            "INSERT INTO presets (user_id, name, description, is_global, is_default) 
             VALUES (?, ?, ?, ?, ?)",
            [
                $data['user_id'] ?? null,
                $data['name'],
                $data['description'] ?? null,
                $data['is_global'] ?? 0,
                $data['is_default'] ?? 0,
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
        $sql = "UPDATE presets SET " . implode(', ', $fields) . " WHERE id = ?";

        return Database::execute($sql, $params) > 0;
    }

    public static function getItems(int $presetId): array
    {
        return Database::fetchAll(
            "SELECT * FROM preset_items 
             WHERE preset_id = ?
             ORDER BY `order` ASC",
            [$presetId]
        );
    }
}
