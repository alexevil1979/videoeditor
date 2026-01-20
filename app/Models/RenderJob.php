<?php

namespace App\Models;

use App\Core\Database;

class RenderJob
{
    public static function findById(int $id): ?array
    {
        return Database::fetchOne(
            "SELECT j.*, v.original_filename, p.name as preset_name
             FROM render_jobs j
             LEFT JOIN videos v ON j.video_id = v.id
             LEFT JOIN presets p ON j.preset_id = p.id
             WHERE j.id = ?",
            [$id]
        );
    }

    public static function findByUser(int $userId, int $limit = 50, int $offset = 0): array
    {
        return Database::fetchAll(
            "SELECT j.*, v.original_filename, p.name as preset_name
             FROM render_jobs j
             LEFT JOIN videos v ON j.video_id = v.id
             LEFT JOIN presets p ON j.preset_id = p.id
             WHERE j.user_id = ?
             ORDER BY j.created_at DESC
             LIMIT ? OFFSET ?",
            [$userId, $limit, $offset]
        );
    }

    public static function create(array $data): int
    {
        Database::query(
            "INSERT INTO render_jobs (user_id, video_id, preset_id, status, priority) 
             VALUES (?, ?, ?, ?, ?)",
            [
                $data['user_id'],
                $data['video_id'],
                $data['preset_id'],
                $data['status'] ?? 'pending',
                $data['priority'] ?? 0,
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
        $sql = "UPDATE render_jobs SET " . implode(', ', $fields) . " WHERE id = ?";

        return Database::execute($sql, $params) > 0;
    }

    public static function getNextPending(): ?array
    {
        return Database::fetchOne(
            "SELECT * FROM render_jobs 
             WHERE status = 'pending' 
             ORDER BY priority DESC, created_at ASC
             LIMIT 1"
        );
    }

    public static function getAll(int $limit = 100, int $offset = 0): array
    {
        return Database::fetchAll(
            "SELECT j.*, v.original_filename, u.email as user_email, p.name as preset_name
             FROM render_jobs j
             LEFT JOIN videos v ON j.video_id = v.id
             LEFT JOIN users u ON j.user_id = u.id
             LEFT JOIN presets p ON j.preset_id = p.id
             ORDER BY j.created_at DESC
             LIMIT ? OFFSET ?",
            [$limit, $offset]
        );
    }

    public static function getQueueStats(): array
    {
        $stats = Database::fetchAll(
            "SELECT status, COUNT(*) as count 
             FROM render_jobs 
             GROUP BY status"
        );

        $result = [
            'pending' => 0,
            'processing' => 0,
            'completed' => 0,
            'failed' => 0,
        ];

        foreach ($stats as $stat) {
            $result[$stat['status']] = (int) $stat['count'];
        }

        return $result;
    }
}
