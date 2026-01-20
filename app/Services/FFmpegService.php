<?php

namespace App\Services;

use App\Core\Config;
use App\Models\Preset;
use App\Models\Video;

class FFmpegService
{
    private string $ffmpegBinary;
    private int $threads;
    private int $outputWidth;
    private int $outputHeight;
    private string $outputFormat;

    public function __construct()
    {
        $this->ffmpegBinary = Config::get('ffmpeg.binary', 'ffmpeg');
        $this->threads = Config::get('ffmpeg.threads', 4);
        $this->outputWidth = Config::get('ffmpeg.output_width', 1080);
        $this->outputHeight = Config::get('ffmpeg.output_height', 1920);
        $this->outputFormat = Config::get('ffmpeg.output_format', 'mp4');
    }

    public function processVideo(int $jobId, int $videoId, int $presetId): array
    {
        error_log("FFmpegService::processVideo called: jobId={$jobId}, videoId={$videoId}, presetId={$presetId}");
        
        $video = Video::findById($videoId);
        $preset = Preset::findById($presetId);
        $presetItems = Preset::getItems($presetId);

        if (!$video || !$preset || empty($presetItems)) {
            error_log("FFmpegService: Invalid video or preset - video=" . ($video ? 'found' : 'NOT FOUND') . ", preset=" . ($preset ? 'found' : 'NOT FOUND') . ", items=" . count($presetItems));
            return ['success' => false, 'message' => 'Invalid video or preset'];
        }
        
        error_log("FFmpegService: Video found: " . $video['storage_path']);

        $inputPath = $video['storage_path'];
        
        // Check if input file exists
        if (!file_exists($inputPath)) {
            return [
                'success' => false,
                'message' => "Input video file not found: {$inputPath}",
                'error' => "File does not exist: {$inputPath}",
            ];
        }
        
        // Check if input file is readable
        if (!is_readable($inputPath)) {
            return [
                'success' => false,
                'message' => "Input video file is not readable: {$inputPath}",
                'error' => "Permission denied: {$inputPath}",
            ];
        }
        
        $outputPath = $this->generateOutputPath($jobId);
        $outputDir = dirname($outputPath);

        if (!is_dir($outputDir)) {
            if (!mkdir($outputDir, 0755, true)) {
                return [
                    'success' => false,
                    'message' => "Failed to create output directory: {$outputDir}",
                    'error' => "Cannot create directory: {$outputDir}",
                ];
            }
        }
        
        // Check if output directory is writable
        if (!is_writable($outputDir)) {
            return [
                'success' => false,
                'message' => "Output directory is not writable: {$outputDir}",
                'error' => "Permission denied: {$outputDir}",
            ];
        }

        // Build FFmpeg command
        $command = $this->buildFFmpegCommand($inputPath, $outputPath, $presetItems, $video);
        
        // Log command for debugging
        $logsDir = Config::get('storage.logs');
        if (!is_dir($logsDir)) {
            if (!mkdir($logsDir, 0755, true)) {
                // If we can't create logs dir, continue without logging
                error_log("Warning: Cannot create logs directory: {$logsDir}");
            }
        }
        
        if (is_dir($logsDir) && is_writable($logsDir)) {
            $logFile = $logsDir . '/ffmpeg_commands.log';
            error_log("Job #{$jobId} FFmpeg command: {$command}\n", 3, $logFile);
        }

        // Execute
        $startTime = time();
        $output = [];
        $returnCode = 0;

        error_log("FFmpegService: Executing command: {$command}");
        exec($command . ' 2>&1', $output, $returnCode);
        
        error_log("FFmpegService: Command executed, returnCode={$returnCode}, outputLines=" . count($output));
        
        // Log output for debugging
        if (is_dir($logsDir) && is_writable($logsDir)) {
            $logFile = $logsDir . '/ffmpeg_commands.log';
            error_log("Job #{$jobId} FFmpeg output (code: {$returnCode}):\n" . implode("\n", $output) . "\n\n", 3, $logFile);
        }

        if ($returnCode !== 0 || !file_exists($outputPath)) {
            $errorOutput = implode("\n", $output);
            
            error_log("FFmpegService: Processing failed - returnCode={$returnCode}, outputExists=" . (file_exists($outputPath) ? 'yes' : 'no'));
            error_log("FFmpegService: Error output length=" . strlen($errorOutput));
            
            // If no output, try to get more info
            if (empty($errorOutput)) {
                $errorOutput = "FFmpeg returned code {$returnCode} but produced no output.\n";
                $errorOutput .= "Input file: {$inputPath}\n";
                $errorOutput .= "Input exists: " . (file_exists($inputPath) ? 'yes' : 'no') . "\n";
                $errorOutput .= "Output file: {$outputPath}\n";
                $errorOutput .= "Output dir exists: " . (is_dir($outputDir) ? 'yes' : 'no') . "\n";
                $errorOutput .= "Output dir writable: " . (is_writable($outputDir) ? 'yes' : 'no') . "\n";
                $errorOutput .= "Command: {$command}\n";
            }
            
            return [
                'success' => false,
                'message' => 'FFmpeg processing failed',
                'error' => $errorOutput,
            ];
        }

        $processingTime = time() - $startTime;
        $outputSize = filesize($outputPath);

        return [
            'success' => true,
            'output_path' => $outputPath,
            'output_size' => $outputSize,
            'processing_time' => $processingTime,
        ];
    }

    private function buildFFmpegCommand(string $inputPath, string $outputPath, array $presetItems, array $video): string
    {
        $ffmpeg = escapeshellarg($this->ffmpegBinary);
        $input = escapeshellarg($inputPath);
        $output = escapeshellarg($outputPath);

        // Generate overlay images first (only if GD is available)
        $overlayInputs = [];
        foreach ($presetItems as $index => $item) {
            if (($item['type'] === 'subscribe' || $item['type'] === 'like') && extension_loaded('gd')) {
                try {
                    $overlayInputs[$index] = $this->generateOverlayImage($item, $index);
                } catch (\Exception $e) {
                    // Skip image generation if GD fails, will use text overlay instead
                    error_log("GD image generation failed: " . $e->getMessage());
                }
            }
        }

        // Base command
        $cmd = "{$ffmpeg} -i {$input}";

        // Add overlay image inputs
        foreach ($overlayInputs as $index => $imagePath) {
            $cmd .= " -i " . escapeshellarg($imagePath);
        }

        // Video filters
        $filters = [];
        
        // Scale and pad to target resolution
        $scaleFilter = $this->buildScaleFilter($video);
        $filters[] = $scaleFilter;

        // Add overlay filters for each preset item
        $currentLabel = 'v';
        foreach ($presetItems as $index => $item) {
            $filter = $this->buildOverlayFilter($item, $index, $currentLabel, $overlayInputs);
            if ($filter) {
                $filters[] = $filter;
                $currentLabel = 'v'; // Update label for next filter
            }
        }

        // Combine filters
        if (!empty($filters)) {
            $filterComplex = implode(';', $filters);
            $cmd .= " -filter_complex " . escapeshellarg($filterComplex);
            $cmd .= " -map \"[{$currentLabel}]\"";
        } else {
            $cmd .= " -map 0:v";
        }

        // Map audio (if exists)
        $cmd .= " -map 0:a?";

        // Video codec settings
        $cmd .= " -c:v " . escapeshellarg(Config::get('ffmpeg.video_codec', 'libx264'));
        $cmd .= " -c:a " . escapeshellarg(Config::get('ffmpeg.audio_codec', 'aac'));
        $cmd .= " -crf " . Config::get('ffmpeg.crf', 23);
        $cmd .= " -preset " . escapeshellarg(Config::get('ffmpeg.preset', 'medium'));
        $cmd .= " -threads {$this->threads}";
        $cmd .= " -movflags +faststart"; // Web optimization

        // Output
        $cmd .= " -y {$output}"; // -y to overwrite

        return $cmd;
    }

    private function buildScaleFilter(array $video): string
    {
        $inputWidth = (int) ($video['width'] ?? $this->outputWidth);
        $inputHeight = (int) ($video['height'] ?? $this->outputHeight);
        $outputWidth = $this->outputWidth;
        $outputHeight = $this->outputHeight;

        // Calculate scale to fit while maintaining aspect ratio
        $scaleW = $outputWidth;
        $scaleH = -1; // Maintain aspect ratio
        $padX = 0;
        $padY = 0;

        // Scale first
        $filter = "[0:v]scale={$scaleW}:{$scaleH}";

        // Then pad to exact dimensions if needed
        $scaledHeight = (int) ($inputHeight * $outputWidth / $inputWidth);
        if ($scaledHeight < $outputHeight) {
            $padY = ($outputHeight - $scaledHeight) / 2;
            $filter .= ",pad={$outputWidth}:{$outputHeight}:0:{$padY}:black";
        } elseif ($scaledHeight > $outputHeight) {
            // Crop if too tall
            $cropY = ($scaledHeight - $outputHeight) / 2;
            $filter .= ",crop={$outputWidth}:{$outputHeight}:0:{$cropY}";
        }

        $filter .= "[v]";

        return $filter;
    }

    private function buildOverlayFilter(array $item, int $index, string $inputLabel, array $overlayInputs): string
    {
        $type = $item['type'];
        $x = $this->parsePosition($item['position_x'], $this->outputWidth);
        $y = $this->parsePosition($item['position_y'], $this->outputHeight);
        $opacity = (float) ($item['opacity'] ?? 1.0);
        $scale = (float) ($item['scale'] ?? 1.0);
        $startTime = (float) ($item['start_time'] ?? 0);
        $endTime = $item['end_time'] ? (float) $item['end_time'] : null;

        if ($type === 'title') {
            return $this->buildTextOverlay($item, $x, $y, $opacity, $startTime, $endTime, $inputLabel);
        } elseif (($type === 'subscribe' || $type === 'like') && isset($overlayInputs[$index])) {
            // Only use image overlay if image was generated
            $overlayIndex = $index + 1; // +1 because input 0 is the video
            return $this->buildImageOverlay($item, $x, $y, $opacity, $scale, $startTime, $endTime, $overlayIndex, $inputLabel);
        } elseif ($type === 'subscribe' || $type === 'like') {
            // Fallback to text overlay if GD is not available
            $text = strtoupper($type);
            $item['text'] = $text;
            return $this->buildTextOverlay($item, $x, $y, $opacity, $startTime, $endTime, $inputLabel);
        }

        return '';
    }

    private function buildTextOverlay(array $item, int $x, int $y, float $opacity, float $startTime, ?float $endTime, string $inputLabel): string
    {
        $text = $item['text'] ?? 'Video Title';
        $fontSize = (int) ($item['font_size'] ?? 24);
        $fontColor = $item['font_color'] ?? '#FFFFFF';
        $bgColor = $item['background_color'] ?? null;

        // Escape text for FFmpeg
        $text = str_replace(['\\', ':', "'"], ['\\\\', '\\:', "\\'"], $text);

        $filter = "[{$inputLabel}]drawtext=";
        $filter .= "text='" . $text . "':";
        $filter .= "fontsize={$fontSize}:";
        $filter .= "fontcolor={$fontColor}:";
        $filter .= "x={$x}:";
        $filter .= "y={$y}:";

        if ($bgColor) {
            $filter .= "box=1:boxcolor={$bgColor}@0.5:";
        }

        if ($startTime > 0 || $endTime) {
            $filter .= "enable='between(t,{$startTime}";
            if ($endTime) {
                $filter .= ",{$endTime}";
            } else {
                $filter .= ",10000"; // Large number
            }
            $filter .= ")'";
        }

        $filter .= ":";
        $filter .= "[{$inputLabel}]";

        return $filter;
    }

    private function buildImageOverlay(array $item, int $x, int $y, float $opacity, float $scale, float $startTime, ?float $endTime, int $overlayIndex, string $inputLabel): string
    {
        $filter = "[{$inputLabel}][{$overlayIndex}:v]overlay=";
        $filter .= "x={$x}:";
        $filter .= "y={$y}:";
        
        if ($opacity < 1.0) {
            $filter .= "format=yuva420p,";
        }

        if ($startTime > 0 || $endTime) {
            $filter .= "enable='between(t,{$startTime}";
            if ($endTime) {
                $filter .= ",{$endTime}";
            } else {
                $filter .= ",10000";
            }
            $filter .= ")'";
        }

        $filter .= ":";
        $filter .= "[{$inputLabel}]";

        return $filter;
    }

    private function generateOverlayImage(array $item, int $index): string
    {
        $type = $item['type'];
        $cacheDir = Config::get('storage.cache') . '/overlays';
        if (!is_dir($cacheDir)) {
            mkdir($cacheDir, 0755, true);
        }

        $imagePath = $cacheDir . "/overlay_{$type}_{$index}.png";

        // Check if file already exists
        if (file_exists($imagePath)) {
            return $imagePath;
        }

        // Check if GD extension is available
        if (!extension_loaded('gd')) {
            // Return empty string - caller should handle fallback
            throw new \RuntimeException('GD extension is not available. Image overlays will be skipped.');
        }

        // Generate button image using GD
        $width = 200;
        $height = 60;
        $image = imagecreatetruecolor($width, $height);
        
        if (!$image) {
            throw new \RuntimeException('Failed to create image with GD');
        }
        
        // Background
        $bgColor = imagecolorallocate($image, 255, 0, 0); // Red for subscribe
        if ($type === 'like') {
            $bgColor = imagecolorallocate($image, 0, 150, 255); // Blue for like
        }
        imagefilledrectangle($image, 0, 0, $width, $height, $bgColor);

        // Text
        $textColor = imagecolorallocate($image, 255, 255, 255);
        $text = strtoupper($type);
        $fontSize = 5;
        $textX = ($width - strlen($text) * imagefontwidth($fontSize)) / 2;
        $textY = ($height - imagefontheight($fontSize)) / 2;
        imagestring($image, $fontSize, $textX, $textY, $text, $textColor);

        // Save
        if (!imagepng($image, $imagePath)) {
            imagedestroy($image);
            throw new \RuntimeException("Failed to save overlay image to: {$imagePath}");
        }
        imagedestroy($image);

        return $imagePath;
    }

    private function parsePosition(string $position, int $max): int
    {
        if (is_numeric($position)) {
            return (int) $position;
        }

        switch (strtolower($position)) {
            case 'left':
            case 'top':
                return 20;
            case 'right':
            case 'bottom':
                return $max - 20;
            case 'center':
            default:
                return (int) ($max / 2);
        }
    }

    private function generateOutputPath(int $jobId): string
    {
        $renderDir = Config::get('storage.renders');
        $filename = "render_{$jobId}_" . time() . ".{$this->outputFormat}";
        return $renderDir . '/' . $filename;
    }
}
