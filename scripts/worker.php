<?php

/**
 * Video Render Queue Worker
 * Run this as a systemd service for continuous processing
 */

require_once __DIR__ . '/../vendor/autoload.php';

use App\Core\Config;
use App\Core\Database;
use App\Models\RenderJob;
use App\Services\FFmpegService;

// Load configuration
Config::load(__DIR__ . '/../config/config.php');

// Worker configuration
$workerId = gethostname() . '_' . getmypid();
$sleepInterval = Config::get('queue.worker_sleep', 2);
$maxRetries = Config::get('queue.max_retries', 3);
$timeout = Config::get('queue.timeout', 3600);

echo "Worker started: {$workerId}\n";

$ffmpegService = new FFmpegService();

while (true) {
    try {
        // Get next pending job
        $job = RenderJob::getNextPending();

        if (!$job) {
            sleep($sleepInterval);
            continue;
        }

        $jobId = $job['id'];
        $videoId = $job['video_id'];
        $presetId = $job['preset_id'];

        echo "Processing job #{$jobId} (video: {$videoId}, preset: {$presetId})\n";

        // Lock job (update status to processing)
        RenderJob::update($jobId, [
            'status' => 'processing',
            'started_at' => date('Y-m-d H:i:s'),
            'worker_id' => $workerId,
            'progress' => 10,
        ]);

        // Process video
        $startTime = time();
        try {
            $result = $ffmpegService->processVideo($jobId, $videoId, $presetId);
        } catch (\Exception $e) {
            $result = [
                'success' => false,
                'message' => 'Exception during processing: ' . $e->getMessage(),
                'error' => $e->getTraceAsString(),
            ];
            echo "EXCEPTION: " . $e->getMessage() . "\n";
        }

        if ($result['success']) {
            // Update job as completed
            $outputFilename = basename($result['output_path']);
            
            RenderJob::update($jobId, [
                'status' => 'completed',
                'completed_at' => date('Y-m-d H:i:s'),
                'output_path' => $result['output_path'],
                'output_filename' => $outputFilename,
                'output_size' => $result['output_size'],
                'progress' => 100,
            ]);

            // Update video status
            Database::query(
                "UPDATE videos SET status = 'ready' WHERE id = ?",
                [$videoId]
            );

            $processingTime = time() - $startTime;
            echo "Job #{$jobId} completed in {$processingTime}s\n";
        } else {
            // Handle failure - save detailed error message
            $errorMessage = $result['message'] ?? 'Processing failed';
            $errorDetails = $result['error'] ?? '';
            
            // Combine error message and details
            $fullError = $errorMessage;
            if ($errorDetails) {
                $fullError .= "\n\nFFmpeg Error:\n" . $errorDetails;
            }
            
            // Log error to file
            $logFile = __DIR__ . '/../storage/logs/worker_errors.log';
            $logDir = dirname($logFile);
            if (!is_dir($logDir)) {
                mkdir($logDir, 0755, true);
            }
            error_log("Job #{$jobId} failed: {$fullError}\n", 3, $logFile);
            
            $retryCount = $job['retry_count'] + 1;
            
            if ($retryCount < $maxRetries) {
                // Retry
                RenderJob::update($jobId, [
                    'status' => 'pending',
                    'retry_count' => $retryCount,
                    'error_message' => $fullError,
                    'worker_id' => null,
                ]);
                echo "Job #{$jobId} failed, will retry (attempt {$retryCount}/{$maxRetries})\n";
                echo "=== ERROR DETAILS ===\n";
                echo "Message: {$errorMessage}\n";
                if ($errorDetails) {
                    echo "FFmpeg Output:\n";
                    echo substr($errorDetails, 0, 500) . "\n";
                    if (strlen($errorDetails) > 500) {
                        echo "... (truncated, see logs for full output)\n";
                    }
                }
                echo "=====================\n";
            } else {
                // Max retries reached
                RenderJob::update($jobId, [
                    'status' => 'failed',
                    'error_message' => $fullError,
                    'worker_id' => null,
                ]);
                echo "Job #{$jobId} failed permanently\n";
                echo "=== ERROR DETAILS ===\n";
                echo "Message: {$errorMessage}\n";
                if ($errorDetails) {
                    echo "FFmpeg Output:\n";
                    echo substr($errorDetails, 0, 500) . "\n";
                    if (strlen($errorDetails) > 500) {
                        echo "... (truncated, see logs for full output)\n";
                    }
                }
                echo "=====================\n";
                echo "Full error saved to: /ssd/www/videoeditor/storage/logs/worker_errors.log\n";
            }
        }

    } catch (\Exception $e) {
        echo "Error: " . $e->getMessage() . "\n";
        echo $e->getTraceAsString() . "\n";
        
        // Log error
        if (isset($jobId)) {
            RenderJob::update($jobId, [
                'status' => 'failed',
                'error_message' => $e->getMessage(),
                'worker_id' => null,
            ]);
        }
    }

    // Small delay between jobs
    usleep(500000); // 0.5 seconds
}
