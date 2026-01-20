<?php

namespace App\Middleware;

use App\Core\Response;
use App\Core\Session;
use App\Models\User;

class AdminMiddleware
{
    public function handle(): bool
    {
        $userId = Session::get('user_id');
        
        if (!$userId) {
            Response::error('Unauthorized', 401);
            return false;
        }

        $user = User::findById($userId);
        
        if (!$user || $user['role'] !== 'admin') {
            Response::error('Forbidden', 403);
            return false;
        }

        return true;
    }
}
