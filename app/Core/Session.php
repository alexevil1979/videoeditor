<?php

namespace App\Core;

class Session
{
    private static bool $started = false;

    public static function start(): void
    {
        if (!self::$started) {
            $sessionName = Config::get('security.session_name', 'video_overlay_session');
            session_name($sessionName);
            session_start();
            self::$started = true;
        }
    }

    public static function get(string $key, $default = null)
    {
        self::start();
        return $_SESSION[$key] ?? $default;
    }

    public static function set(string $key, $value): void
    {
        self::start();
        $_SESSION[$key] = $value;
    }

    public static function has(string $key): bool
    {
        self::start();
        return isset($_SESSION[$key]);
    }

    public static function remove(string $key): void
    {
        self::start();
        unset($_SESSION[$key]);
    }

    public static function destroy(): void
    {
        self::start();
        session_destroy();
        self::$started = false;
    }

    public static function regenerate(): void
    {
        self::start();
        session_regenerate_id(true);
    }

    public static function flash(string $key, $value = null)
    {
        self::start();
        if ($value === null) {
            $flash = $_SESSION['_flash'][$key] ?? null;
            unset($_SESSION['_flash'][$key]);
            return $flash;
        }
        $_SESSION['_flash'][$key] = $value;
    }
}
