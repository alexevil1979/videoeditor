<?php

namespace App\Middleware;

use App\Core\Response;
use App\Core\Session;

class AuthMiddleware
{
    public function handle(): bool
    {
        if (!Session::has('user_id')) {
            if ($this->isApiRequest()) {
                Response::error('Unauthorized', 401);
            } else {
                Response::redirect('/login');
            }
            return false;
        }

        return true;
    }

    private function isApiRequest(): bool
    {
        return strpos($_SERVER['REQUEST_URI'] ?? '', '/api/') !== false;
    }
}
