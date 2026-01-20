<?php

namespace App\Controllers;

use App\Core\Database;
use App\Core\Response;
use App\Models\Preset;
use App\Services\AuthService;

class PresetController
{
    private AuthService $authService;

    public function __construct()
    {
        $this->authService = new AuthService();
    }

    public function list(): void
    {
        $user = $this->authService->getCurrentUser();
        if (!$user) {
            Response::error('Unauthorized', 401);
            return;
        }

        $presets = Preset::findByUser($user['id']);
        Response::success(['presets' => $presets]);
    }

    public function create(): void
    {
        $user = $this->authService->getCurrentUser();
        if (!$user) {
            Response::error('Unauthorized', 401);
            return;
        }

        $name = $_POST['name'] ?? '';
        $description = $_POST['description'] ?? '';
        $items = json_decode($_POST['items'] ?? '[]', true);

        if (empty($name) || empty($items)) {
            Response::error('Name and items are required');
            return;
        }

        Database::beginTransaction();

        try {
            $presetId = Preset::create([
                'user_id' => $user['id'],
                'name' => $name,
                'description' => $description,
                'is_global' => 0,
            ]);

            // Create preset items
            foreach ($items as $order => $item) {
                Database::query(
                    "INSERT INTO preset_items (preset_id, type, position_x, position_y, start_time, end_time, opacity, scale, animation, text, font_size, font_color, background_color, `order`) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        $presetId,
                        $item['type'] ?? 'title',
                        $item['position_x'] ?? 'center',
                        $item['position_y'] ?? 'center',
                        $item['start_time'] ?? 0,
                        $item['end_time'] ?? null,
                        $item['opacity'] ?? 1.0,
                        $item['scale'] ?? 1.0,
                        $item['animation'] ?? 'none',
                        $item['text'] ?? null,
                        $item['font_size'] ?? 24,
                        $item['font_color'] ?? '#FFFFFF',
                        $item['background_color'] ?? null,
                        $order,
                    ]
                );
            }

            Database::commit();
            Response::success(['preset_id' => $presetId], 'Preset created');
        } catch (\Exception $e) {
            Database::rollback();
            Response::error('Failed to create preset: ' . $e->getMessage());
        }
    }

    public function get(int $id): void
    {
        $user = $this->authService->getCurrentUser();
        if (!$user) {
            Response::error('Unauthorized', 401);
            return;
        }

        $preset = Preset::findById($id);
        if (!$preset) {
            Response::error('Preset not found', 404);
            return;
        }

        // Check access (user's preset or global)
        if ($preset['user_id'] != $user['id'] && !$preset['is_global']) {
            Response::error('Access denied', 403);
            return;
        }

        $items = Preset::getItems($id);
        $preset['items'] = $items;

        Response::success(['preset' => $preset]);
    }
}
