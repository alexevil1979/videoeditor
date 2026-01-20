<?php

namespace App\Controllers;

use App\Core\Lang;
use App\Core\Response;

/**
 * Контроллер для управления языками
 */
class LanguageController
{
    /**
     * Переключает язык приложения
     * @param string $lang Код языка (en, ru, th, zh)
     */
    public function switch(string $lang): void
    {
        Lang::set($lang);
        
        // Перенаправляем обратно на предыдущую страницу или главную
        $referer = $_SERVER['HTTP_REFERER'] ?? '/';
        Response::redirect($referer);
    }
}
