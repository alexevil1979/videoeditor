<?php

return [
    'app' => [
        'name' => 'Video Editor SaaS',
        'url' => 'http://localhost',
        'timezone' => 'UTC',
        'debug' => false,
    ],

    'database' => [
        'host' => 'localhost',
        'port' => 3306,
        'name' => 'video_overlay',
        'user' => 'video_user',
        'password' => 'secure_password',
        'charset' => 'utf8mb4',
    ],

    'storage' => [
        'base_path' => __DIR__ . '/../storage',
        'uploads' => __DIR__ . '/../storage/uploads',
        'renders' => __DIR__ . '/../storage/renders',
        'logs' => __DIR__ . '/../storage/logs',
        'cache' => __DIR__ . '/../storage/cache',
    ],

    'ffmpeg' => [
        'binary' => 'ffmpeg',
        'threads' => 4,
        'output_width' => 1080,
        'output_height' => 1920,
        'output_format' => 'mp4',
        'video_codec' => 'libx264',
        'audio_codec' => 'aac',
        'crf' => 23,
        'preset' => 'medium',
    ],

    'security' => [
        'session_name' => 'video_overlay_session',
        'session_lifetime' => 7200, // 2 hours
        'csrf_token_name' => 'csrf_token',
        'password_min_length' => 8,
    ],

    'limits' => [
        'max_upload_size' => 100 * 1024 * 1024, // 100MB
        'max_render_duration' => 300, // 5 minutes
        'allowed_video_formats' => ['mp4', 'mov', 'avi', 'mkv', 'webm'],
    ],

    'pricing' => [
        'credit_cost_per_minute' => 1.0,
        'free_credits_on_signup' => 10.0,
    ],

    'queue' => [
        'worker_sleep' => 2, // seconds between job checks
        'max_retries' => 3,
        'timeout' => 3600, // 1 hour max per job
    ],
];
