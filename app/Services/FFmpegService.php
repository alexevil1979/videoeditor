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
        $video = Video::findById($videoId);
        $preset = Preset::findById($presetId);
        $presetItems = Preset::getItems($presetId);

        if (!$video || !$preset || empty($presetItems)) {
            return ['success' => false, 'message' => 'Invalid video or preset'];
        }

        $inputPath = $video['storage_path'];
        $outputPath = $this->generateOutputPath($jobId);
        $outputDir = dirname($outputPath);

        if (!is_dir($outputDir)) {
            mkdir($outputDir, 0755, true);
        }

        // Build FFmpeg command
        $command = $this->buildFFmpegCommand($inputPath, $outputPath, $presetItems, $video);

        // Execute
        $startTime = time();
        $output = [];
        $returnCode = 0;

        exec($command . ' 2>&1', $output, $returnCode);

        if ($returnCode !== 0 || !file_exists($outputPath)) {
            return [
                'success' => false,
                'message' => 'FFmpeg processing failed',
                'error' => implode("\n", $output),
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

        // Generate overlay images first
        $overlayInputs = [];
        foreach ($presetItems as $index => $item) {
            if ($item['type'] === 'subscribe' || $item['type'] === 'like') {
                $overlayInputs[$index] = $this->generateOverlayImage($item, $index);
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
        } elseif ($type === 'subscribe' || $type === 'like') {
            $overlayIndex = $index + 1; // +1 because input 0 is the video
            return $this->buildImageOverlay($item, $x, $y, $opacity, $scale, $startTime, $endTime, $overlayIndex, $inputLabel);
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

        // Generate button image using GD
        $width = 200;
        $height = 60;
        $image = imagecreatetruecolor($width, $height);
        
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
        imagepng($image, $imagePath);
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
