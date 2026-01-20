<?php

namespace App\Controllers;

use App\Core\Response;
use App\Core\Session;
use App\Models\Video;
use App\Models\RenderJob;
use App\Services\AuthService;
use App\Services\VideoService;

class VideoController
{
    private AuthService $authService;
    private VideoService $videoService;

    public function __construct()
    {
        $this->authService = new AuthService();
        $this->videoService = new VideoService();
    }

    public function upload(): void
    {
        $user = $this->authService->getCurrentUser();
        if (!$user) {
            Response::error('Unauthorized', 401);
            return;
        }

        if (!isset($_FILES['video'])) {
            Response::error('No file uploaded');
            return;
        }

        $result = $this->videoService->upload($user['id'], $_FILES['video']);

        if ($result['success']) {
            Response::success($result, 'Video uploaded successfully');
        } else {
            Response::error($result['message']);
        }
    }

    public function list(): void
    {
        $user = $this->authService->getCurrentUser();
        if (!$user) {
            Response::error('Unauthorized', 401);
            return;
        }

        $videos = Video::findByUser($user['id']);
        Response::success(['videos' => $videos]);
    }

    public function render(): void
    {
        $user = $this->authService->getCurrentUser();
        if (!$user) {
            Response::error('Unauthorized', 401);
            return;
        }

        $videoId = (int) ($_POST['video_id'] ?? 0);
        $presetId = (int) ($_POST['preset_id'] ?? 0);

        if (!$videoId || !$presetId) {
            Response::error('Missing video_id or preset_id');
            return;
        }

        $result = $this->videoService->createRenderJob($user['id'], $videoId, $presetId);

        if ($result['success']) {
            Response::success($result, 'Render job created');
        } else {
            Response::error($result['message']);
        }
    }

    public function download(int $jobId): void
    {
        $user = $this->authService->getCurrentUser();
        if (!$user) {
            Response::error('Unauthorized', 401);
            return;
        }

        $job = RenderJob::findById($jobId);
        if (!$job || $job['user_id'] != $user['id'] || $job['status'] !== 'completed') {
            Response::error('Job not found or not ready');
            return;
        }

        if (!file_exists($job['output_path'])) {
            Response::error('File not found');
            return;
        }

        $filename = $job['output_filename'] ?? 'video_' . $jobId . '.mp4';

        header('Content-Type: video/mp4');
        header('Content-Disposition: attachment; filename="' . $filename . '"');
        header('Content-Length: ' . filesize($job['output_path']));
        readfile($job['output_path']);
        exit;
    }

    public function status(int $jobId): void
    {
        $user = $this->authService->getCurrentUser();
        if (!$user) {
            Response::error('Unauthorized', 401);
            return;
        }

        $job = RenderJob::findById($jobId);
        if (!$job || $job['user_id'] != $user['id']) {
            Response::error('Job not found');
            return;
        }

        Response::success(['job' => $job]);
    }
}
