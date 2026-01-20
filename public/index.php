<?php

require_once __DIR__ . '/../vendor/autoload.php';

use App\Core\Config;
use App\Core\Router;
use App\Core\Session;
use App\Core\Lang;
use App\Middleware\AuthMiddleware;
use App\Middleware\AdminMiddleware;

// Load configuration
Config::load(__DIR__ . '/../config/config.php');

// Start session
Session::start();

// Initialize language system
Lang::init();

// Initialize router
$router = new Router();

// Public routes
$router->get('/', function() {
    if (\App\Core\Session::has('user_id')) {
        \App\Core\Response::redirect('/dashboard');
    } else {
        \App\Core\Response::redirect('/login');
    }
});

$router->get('/login', 'AuthController@login');
$router->post('/login', 'AuthController@login');
$router->get('/register', 'AuthController@register');
$router->post('/register', 'AuthController@register');
$router->get('/logout', 'AuthController@logout');

// Language switching
$router->get('/lang/{lang}', 'LanguageController@switch');

// Protected user routes
$router->get('/dashboard', 'DashboardController@index', [AuthMiddleware::class]);
$router->get('/api/videos', 'VideoController@list', [AuthMiddleware::class]);
$router->post('/api/videos/upload', 'VideoController@upload', [AuthMiddleware::class]);
$router->post('/api/videos/render', 'VideoController@render', [AuthMiddleware::class]);
$router->get('/api/videos/job/{id}', 'VideoController@status', [AuthMiddleware::class]);
$router->get('/api/videos/download/{id}', 'VideoController@download', [AuthMiddleware::class]);
$router->get('/api/presets', 'PresetController@list', [AuthMiddleware::class]);
$router->post('/api/presets', 'PresetController@create', [AuthMiddleware::class]);
$router->get('/api/presets/{id}', 'PresetController@get', [AuthMiddleware::class]);

// Admin routes
$router->get('/admin', 'AdminController@dashboard', [AuthMiddleware::class, AdminMiddleware::class]);
$router->get('/admin/users', 'AdminController@users', [AuthMiddleware::class, AdminMiddleware::class]);
$router->get('/admin/jobs', 'AdminController@jobs', [AuthMiddleware::class, AdminMiddleware::class]);
$router->post('/admin/balance', 'AdminController@updateBalance', [AuthMiddleware::class, AdminMiddleware::class]);
$router->post('/admin/jobs/{id}/cancel', 'AdminController@cancelJob', [AuthMiddleware::class, AdminMiddleware::class]);
$router->post('/admin/jobs/{id}/restart', 'AdminController@restartJob', [AuthMiddleware::class, AdminMiddleware::class]);

// Dispatch
$router->dispatch();
