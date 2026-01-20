<?php

namespace App\Core;

/**
 * Класс управления конфигурацией приложения
 * Позволяет загружать и получать настройки из конфигурационных файлов
 */
class Config
{
    private static array $config = [];

    /**
     * Загружает конфигурационный файл
     * @param string $configFile Путь к файлу конфигурации
     */
    public static function load(string $configFile): void
    {
        if (file_exists($configFile)) {
            self::$config = require $configFile;
        }
    }

    /**
     * Получает значение конфигурации по ключу (поддерживает вложенность через точку)
     * @param string $key Ключ конфигурации (например: 'database.host')
     * @param mixed $default Значение по умолчанию, если ключ не найден
     * @return mixed
     */
    public static function get(string $key, $default = null)
    {
        $keys = explode('.', $key);
        $value = self::$config;

        foreach ($keys as $k) {
            if (!isset($value[$k])) {
                return $default;
            }
            $value = $value[$k];
        }

        return $value;
    }

    /**
     * Устанавливает значение конфигурации
     * @param string $key Ключ конфигурации
     * @param mixed $value Значение
     */
    public static function set(string $key, $value): void
    {
        $keys = explode('.', $key);
        $config = &self::$config;

        foreach ($keys as $k) {
            if (!isset($config[$k]) || !is_array($config[$k])) {
                $config[$k] = [];
            }
            $config = &$config[$k];
        }

        $config = $value;
    }

    /**
     * Возвращает всю конфигурацию
     * @return array
     */
    public static function all(): array
    {
        return self::$config;
    }
}
