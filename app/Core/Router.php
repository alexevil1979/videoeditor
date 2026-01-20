<?php

namespace App\Core;

class Router
{
    private array $routes = [];
    private array $middleware = [];

    public function get(string $path, $handler, array $middleware = []): void
    {
        $this->addRoute('GET', $path, $handler, $middleware);
    }

    public function post(string $path, $handler, array $middleware = []): void
    {
        $this->addRoute('POST', $path, $handler, $middleware);
    }

    public function put(string $path, $handler, array $middleware = []): void
    {
        $this->addRoute('PUT', $path, $handler, $middleware);
    }

    public function delete(string $path, $handler, array $middleware = []): void
    {
        $this->addRoute('DELETE', $path, $handler, $middleware);
    }

    private function addRoute(string $method, string $path, $handler, array $middleware): void
    {
        $this->routes[] = [
            'method' => $method,
            'path' => $path,
            'handler' => $handler,
            'middleware' => $middleware,
        ];
    }

    public function dispatch(): void
    {
        $method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
        $uri = $this->getUri();
        
        // Логирование для отладки
        error_log("Router dispatch: method=$method, uri=$uri");
        error_log("Registered routes: " . count($this->routes));

        foreach ($this->routes as $route) {
            if ($route['method'] !== $method) {
                continue;
            }

            $pattern = $this->convertToRegex($route['path']);
            if (preg_match($pattern, $uri, $matches)) {
                array_shift($matches); // Remove full match

                // Execute middleware
                foreach ($route['middleware'] as $middlewareClass) {
                    $middleware = new $middlewareClass();
                    if (!$middleware->handle()) {
                        return; // Middleware blocked the request
                    }
                }

                // Execute handler
                $this->executeHandler($route['handler'], $matches);
                return;
            }
        }

        // 404 Not Found
        http_response_code(404);
        // Для отладки - показать какой URI был запрошен
        if (isset($_GET['debug'])) {
            echo json_encode([
                'error' => 'Route not found',
                'method' => $method,
                'uri' => $uri,
                'routes' => array_map(function($r) {
                    return $r['method'] . ' ' . $r['path'];
                }, $this->routes)
            ], JSON_PRETTY_PRINT);
        } else {
            // Показать HTML страницу 404 для браузера
            header('Content-Type: text/html; charset=utf-8');
            echo '<!DOCTYPE html><html><head><title>404 Not Found</title></head><body>';
            echo '<h1>404 - Страница не найдена</h1>';
            echo '<p>Запрошенный путь: ' . htmlspecialchars($uri) . '</p>';
            echo '<p>Метод: ' . htmlspecialchars($method) . '</p>';
            echo '<p><a href="/">Вернуться на главную</a></p>';
            echo '</body></html>';
        }
    }

    private function getUri(): string
    {
        $uri = $_SERVER['REQUEST_URI'] ?? '/';
        $uri = parse_url($uri, PHP_URL_PATH);
        $uri = rtrim($uri, '/') ?: '/';
        return $uri;
    }

    private function convertToRegex(string $path): string
    {
        $pattern = preg_replace('/\{(\w+)\}/', '([^/]+)', $path);
        return '#^' . $pattern . '$#';
    }

    private function executeHandler($handler, array $params): void
    {
        if (is_string($handler) && strpos($handler, '@') !== false) {
            [$controller, $method] = explode('@', $handler);
            $controllerClass = "App\\Controllers\\{$controller}";
            
            if (class_exists($controllerClass)) {
                $controllerInstance = new $controllerClass();
                if (method_exists($controllerInstance, $method)) {
                    call_user_func_array([$controllerInstance, $method], $params);
                    return;
                }
            }
        } elseif (is_callable($handler)) {
            call_user_func_array($handler, $params);
            return;
        }

        http_response_code(500);
        echo json_encode(['error' => 'Invalid route handler']);
    }
}
