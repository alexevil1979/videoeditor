<?php

namespace App\Controllers;

use App\Core\Database;
use App\Core\Response;
use App\Core\Session;
use App\Models\RenderJob;
use App\Models\Video;
use App\Models\Preset;
use App\Services\AuthService;

class DashboardController
{
    private AuthService $authService;

    public function __construct()
    {
        $this->authService = new AuthService();
    }

    public function index(): void
    {
        $user = $this->authService->getCurrentUser();
        if (!$user) {
            Response::redirect('/login');
            return;
        }

        $userId = $user['id'];

        // Get user balance
        $balance = Database::fetchOne(
            "SELECT credits, minutes FROM balances WHERE user_id = ?",
            [$userId]
        );

        // Get recent videos
        $videos = Video::findByUser($userId, 10);

        // Get recent jobs
        $jobs = RenderJob::findByUser($userId, 10);

        // Get presets
        $presets = Preset::findByUser($userId);

        Response::view('dashboard/index', [
            'user' => $user,
            'balance' => $balance,
            'videos' => $videos,
            'jobs' => $jobs,
            'presets' => $presets,
        ]);
    }
}
