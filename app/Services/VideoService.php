<?php

namespace App\Services;

use App\Core\Config;
use App\Core\Database;
use App\Models\Video;
use App\Models\RenderJob;

class VideoService
{
    public function upload(int $userId, array $file): array
    {
        // Validate file
        $maxSize = Config::get('limits.max_upload_size', 100 * 1024 * 1024);
        $allowedFormats = Config::get('limits.allowed_video_formats', ['mp4', 'mov', 'avi']);

        if ($file['error'] !== UPLOAD_ERR_OK) {
            return ['success' => false, 'message' => 'Upload error'];
        }

        if ($file['size'] > $maxSize) {
            return ['success' => false, 'message' => 'File too large'];
        }

        $extension = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        if (!in_array($extension, $allowedFormats)) {
            return ['success' => false, 'message' => 'Invalid file format'];
        }

        // Generate unique filename
        $filename = uniqid('video_', true) . '.' . $extension;
        $uploadPath = Config::get('storage.uploads');
        $storagePath = $uploadPath . '/' . $filename;

        // Create directory if needed
        if (!is_dir($uploadPath)) {
            mkdir($uploadPath, 0755, true);
        }

        // Move uploaded file
        if (!move_uploaded_file($file['tmp_name'], $storagePath)) {
            return ['success' => false, 'message' => 'Failed to save file'];
        }

        // Get video metadata
        $metadata = $this->getVideoMetadata($storagePath);

        // Save to database
        $videoId = Video::create([
            'user_id' => $userId,
            'original_filename' => $file['name'],
            'storage_path' => $storagePath,
            'file_size' => $file['size'],
            'duration' => $metadata['duration'] ?? null,
            'width' => $metadata['width'] ?? null,
            'height' => $metadata['height'] ?? null,
            'format' => $extension,
            'status' => 'uploaded',
            'metadata' => json_encode($metadata),
        ]);

        return ['success' => true, 'video_id' => $videoId, 'video' => Video::findById($videoId)];
    }

    public function createRenderJob(int $userId, int $videoId, int $presetId): array
    {
        // Verify ownership
        $video = Video::findById($videoId);
        if (!$video || $video['user_id'] != $userId) {
            return ['success' => false, 'message' => 'Video not found'];
        }

        // Check balance
        $balance = Database::fetchOne(
            "SELECT credits FROM balances WHERE user_id = ?",
            [$userId]
        );

        $costPerMinute = Config::get('pricing.credit_cost_per_minute', 1.0);
        $duration = (float) ($video['duration'] ?? 60);
        $cost = $costPerMinute * ($duration / 60);

        if (($balance['credits'] ?? 0) < $cost) {
            return ['success' => false, 'message' => 'Insufficient credits'];
        }

        // Deduct credits
        Database::query(
            "UPDATE balances SET credits = credits - ? WHERE user_id = ?",
            [$cost, $userId]
        );

        // Log transaction
        Database::query(
            "INSERT INTO balance_transactions (user_id, type, amount, description, reference_id) 
             VALUES (?, 'debit', ?, ?, ?)",
            [$userId, $cost, "Render job for video #{$videoId}", $videoId]
        );

        // Create job
        $jobId = RenderJob::create([
            'user_id' => $userId,
            'video_id' => $videoId,
            'preset_id' => $presetId,
            'status' => 'pending',
            'priority' => 0,
        ]);

        return ['success' => true, 'job_id' => $jobId];
    }

    private function getVideoMetadata(string $filePath): array
    {
        $ffprobe = Config::get('ffmpeg.binary', 'ffmpeg');
        $ffprobe = str_replace('ffmpeg', 'ffprobe', $ffprobe);

        $command = escapeshellarg($ffprobe) . 
                   ' -v quiet -print_format json -show_format -show_streams ' . 
                   escapeshellarg($filePath) . ' 2>&1';

        $output = shell_exec($command);
        $data = json_decode($output, true);

        if (!$data) {
            return [];
        }

        $videoStream = null;
        foreach ($data['streams'] ?? [] as $stream) {
            if ($stream['codec_type'] === 'video') {
                $videoStream = $stream;
                break;
            }
        }

        return [
            'duration' => (float) ($data['format']['duration'] ?? 0),
            'width' => (int) ($videoStream['width'] ?? 0),
            'height' => (int) ($videoStream['height'] ?? 0),
            'bitrate' => (int) ($data['format']['bit_rate'] ?? 0),
        ];
    }
}
