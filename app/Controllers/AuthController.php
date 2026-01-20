<?php

namespace App\Controllers;

use App\Core\Response;
use App\Core\Lang;
use App\Services\AuthService;

class AuthController
{
    private AuthService $authService;

    public function __construct()
    {
        $this->authService = new AuthService();
    }

    public function login(): void
    {
        if ($_SERVER['REQUEST_METHOD'] === 'GET') {
            Response::view('auth/login');
            return;
        }

        $email = $_POST['email'] ?? '';
        $password = $_POST['password'] ?? '';

        $result = $this->authService->login($email, $password);

        if ($result['success']) {
            // Инициализируем язык из профиля пользователя
            Lang::init();
            Response::redirect('/dashboard');
        } else {
            $errorMessage = $result['message'] === 'Invalid credentials' 
                ? Lang::get('auth.invalid_credentials')
                : $result['message'];
            Response::view('auth/login', ['error' => $errorMessage]);
        }
    }

    public function register(): void
    {
        if ($_SERVER['REQUEST_METHOD'] === 'GET') {
            Response::view('auth/register');
            return;
        }

        $email = $_POST['email'] ?? '';
        $password = $_POST['password'] ?? '';
        $firstName = $_POST['first_name'] ?? null;
        $lastName = $_POST['last_name'] ?? null;

        $result = $this->authService->register($email, $password, $firstName, $lastName);

        if ($result['success']) {
            // Auto-login after registration
            $this->authService->login($email, $password);
            Lang::init();
            Response::redirect('/dashboard');
        } else {
            $errorMessage = $result['message'];
            if ($result['message'] === 'Email already exists') {
                $errorMessage = Lang::get('auth.email_exists');
            } elseif ($result['message'] === 'Password must be at least 8 characters') {
                $errorMessage = Lang::get('auth.password_min');
            }
            Response::view('auth/register', ['error' => $errorMessage]);
        }
    }

    public function logout(): void
    {
        $this->authService->logout();
        Response::redirect('/login');
    }
}
