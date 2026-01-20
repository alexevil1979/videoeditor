<?php

namespace App\Services;

use App\Core\Database;
use App\Core\Session;
use App\Models\User;

class AuthService
{
    public function login(string $email, string $password): array
    {
        $user = User::findByEmail($email);

        if (!$user || $user['status'] !== 'active') {
            return ['success' => false, 'message' => 'Invalid credentials'];
        }

        if (!password_verify($password, $user['password_hash'])) {
            return ['success' => false, 'message' => 'Invalid credentials'];
        }

        // Create session
        Session::regenerate();
        Session::set('user_id', $user['id']);
        Session::set('user_email', $user['email']);
        Session::set('user_role', $user['role']);

        // Store session in database
        $sessionId = session_id();
        Database::query(
            "INSERT INTO sessions (id, user_id, ip_address, user_agent) 
             VALUES (?, ?, ?, ?)
             ON DUPLICATE KEY UPDATE 
             user_id = VALUES(user_id), 
             ip_address = VALUES(ip_address),
             user_agent = VALUES(user_agent),
             last_activity = CURRENT_TIMESTAMP",
            [$sessionId, $user['id'], $_SERVER['REMOTE_ADDR'] ?? null, $_SERVER['HTTP_USER_AGENT'] ?? null]
        );

        return ['success' => true, 'user' => $user];
    }

    public function register(string $email, string $password, string $firstName = null, string $lastName = null): array
    {
        // Validate
        if (User::findByEmail($email)) {
            return ['success' => false, 'message' => 'Email already exists'];
        }

        if (strlen($password) < 8) {
            return ['success' => false, 'message' => 'Password must be at least 8 characters'];
        }

        // Create user
        $initialCredits = \App\Core\Config::get('pricing.free_credits_on_signup', 10.0);
        
        $userId = User::create([
            'email' => $email,
            'password_hash' => password_hash($password, PASSWORD_DEFAULT),
            'role' => 'user',
            'status' => 'active',
            'email_verified' => 0,
            'initial_credits' => $initialCredits,
        ]);

        // Update profile
        if ($firstName || $lastName) {
            Database::query(
                "UPDATE user_profiles SET first_name = ?, last_name = ? WHERE user_id = ?",
                [$firstName, $lastName, $userId]
            );
        }

        // Log transaction
        Database::query(
            "INSERT INTO balance_transactions (user_id, type, amount, description) 
             VALUES (?, 'credit', ?, ?)",
            [$userId, $initialCredits, 'Welcome bonus']
        );

        return ['success' => true, 'user_id' => $userId];
    }

    public function logout(): void
    {
        $sessionId = session_id();
        Database::query("DELETE FROM sessions WHERE id = ?", [$sessionId]);
        Session::destroy();
    }

    public function getCurrentUser(): ?array
    {
        $userId = Session::get('user_id');
        if (!$userId) {
            return null;
        }

        $user = User::findById($userId);
        if (!$user) {
            Session::destroy();
            return null;
        }

        return $user;
    }
}
