<?php

namespace App\Controllers;

use App\Core\Database;
use App\Core\Response;
use App\Models\User;
use App\Models\Video;
use App\Models\RenderJob;
use App\Models\Preset;
use App\Services\AuthService;

class AdminController
{
    private AuthService $authService;

    public function __construct()
    {
        $this->authService = new AuthService();
    }

    public function dashboard(): void
    {
        $user = $this->authService->getCurrentUser();
        if (!$user || $user['role'] !== 'admin') {
            Response::redirect('/dashboard');
            return;
        }

        // Statistics
        $stats = [
            'total_users' => User::count(),
            'total_videos' => Database::fetchOne("SELECT COUNT(*) as count FROM videos WHERE deleted_at IS NULL")['count'] ?? 0,
            'total_jobs' => Database::fetchOne("SELECT COUNT(*) as count FROM render_jobs")['count'] ?? 0,
            'queue_stats' => RenderJob::getQueueStats(),
        ];

        // Recent activity
        $recentJobs = RenderJob::getAll(20);
        $recentUsers = User::getAll(10);

        Response::view('admin/dashboard', [
            'stats' => $stats,
            'recent_jobs' => $recentJobs,
            'recent_users' => $recentUsers,
        ]);
    }

    public function users(): void
    {
        $users = User::getAll(100);
        Response::view('admin/users', ['users' => $users]);
    }

    public function jobs(): void
    {
        $jobs = RenderJob::getAll(100);
        Response::view('admin/jobs', ['jobs' => $jobs]);
    }

    public function updateBalance(): void
    {
        $userId = (int) ($_POST['user_id'] ?? 0);
        $amount = (float) ($_POST['amount'] ?? 0);
        $type = $_POST['type'] ?? 'credit';

        if (!$userId || !$amount) {
            Response::error('Invalid parameters');
            return;
        }

        Database::query(
            "UPDATE balances SET credits = credits + ? WHERE user_id = ?",
            [$type === 'credit' ? $amount : -$amount, $userId]
        );

        Database::query(
            "INSERT INTO balance_transactions (user_id, type, amount, description) 
             VALUES (?, ?, ?, ?)",
            [$userId, $type, abs($amount), 'Admin adjustment']
        );

        Response::success([], 'Balance updated');
    }

    public function cancelJob(int $jobId): void
    {
        RenderJob::update($jobId, ['status' => 'cancelled']);
        Response::success([], 'Job cancelled');
    }

    public function restartJob(int $jobId): void
    {
        RenderJob::update($jobId, [
            'status' => 'pending',
            'retry_count' => 0,
            'error_message' => null,
        ]);
        Response::success([], 'Job restarted');
    }
}
