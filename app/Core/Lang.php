<?php

namespace App\Core;

/**
 * Класс для работы с переводами и мультиязычностью
 * Поддерживает: английский, русский, тайский, китайский
 */
class Lang
{
    private static array $translations = [];
    private static string $currentLang = 'en';
    private static array $supportedLangs = ['en', 'ru', 'th', 'zh'];

    /**
     * Инициализация системы переводов
     * @param string $lang Код языка (en, ru, th, zh)
     */
    public static function init(string $lang = 'en'): void
    {
        // Проверяем язык из сессии
        if (Session::has('language')) {
            $lang = Session::get('language');
        }

        // Проверяем язык из GET параметра
        if (isset($_GET['lang']) && in_array($_GET['lang'], self::$supportedLangs)) {
            $lang = $_GET['lang'];
            Session::set('language', $lang);
        }

        // Проверяем язык из профиля пользователя
        if (Session::has('user_id')) {
            $userId = Session::get('user_id');
            $profile = \App\Core\Database::fetchOne(
                "SELECT language FROM user_profiles WHERE user_id = ?",
                [$userId]
            );
            if ($profile && $profile['language']) {
                $lang = $profile['language'];
            }
        }

        // Валидация языка
        if (!in_array($lang, self::$supportedLangs)) {
            $lang = 'en';
        }

        self::$currentLang = $lang;
        self::loadTranslations($lang);
    }

    /**
     * Загружает переводы для указанного языка
     * @param string $lang Код языка
     */
    private static function loadTranslations(string $lang): void
    {
        $langFile = __DIR__ . "/../../lang/{$lang}.php";
        
        if (file_exists($langFile)) {
            self::$translations = require $langFile;
        } else {
            // Fallback на английский
            $enFile = __DIR__ . "/../../lang/en.php";
            if (file_exists($enFile)) {
                self::$translations = require $enFile;
            }
        }
    }

    /**
     * Получает перевод по ключу
     * @param string $key Ключ перевода (поддерживает вложенность через точку)
     * @param array $params Параметры для замены в строке
     * @return string
     */
    public static function get(string $key, array $params = []): string
    {
        $keys = explode('.', $key);
        $value = self::$translations;

        foreach ($keys as $k) {
            if (!isset($value[$k])) {
                // Возвращаем ключ, если перевод не найден
                return $key;
            }
            $value = $value[$k];
        }

        $translation = is_string($value) ? $value : $key;

        // Замена параметров
        if (!empty($params)) {
            foreach ($params as $paramKey => $paramValue) {
                $translation = str_replace(':' . $paramKey, $paramValue, $translation);
            }
        }

        return $translation;
    }

    /**
     * Получает текущий язык
     * @return string
     */
    public static function current(): string
    {
        return self::$currentLang;
    }
    
    /**
     * Получает текущий язык (алиас для current)
     * @return string
     */
    public static function getCurrent(): string
    {
        return self::$currentLang;
    }

    /**
     * Получает список поддерживаемых языков
     * @return array
     */
    public static function supported(): array
    {
        return self::$supportedLangs;
    }

    /**
     * Устанавливает язык
     * @param string $lang Код языка
     */
    public static function set(string $lang): void
    {
        if (in_array($lang, self::$supportedLangs)) {
            self::$currentLang = $lang;
            Session::set('language', $lang);
            self::loadTranslations($lang);
            
            // Обновляем язык в профиле пользователя
            if (Session::has('user_id')) {
                $userId = Session::get('user_id');
                \App\Core\Database::query(
                    "UPDATE user_profiles SET language = ? WHERE user_id = ?",
                    [$lang, $userId]
                );
            }
        }
    }

    /**
     * Получает название языка
     * @param string $lang Код языка
     * @return string
     */
    public static function name(string $lang): string
    {
        $names = [
            'en' => 'English',
            'ru' => 'Русский',
            'th' => 'ไทย',
            'zh' => '中文',
        ];
        
        return $names[$lang] ?? $lang;
    }
}
