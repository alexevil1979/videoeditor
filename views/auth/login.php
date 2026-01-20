<?php
use App\Core\Lang;
$title = Lang::get('auth.login');
ob_start();
?>

<div class="auth-container">
    <div class="auth-box">
        <h1><?= Lang::get('auth.login_title') ?></h1>
        
        <form method="POST" action="/login">
            <div class="form-group">
                <label for="email"><?= Lang::get('auth.email') ?></label>
                <input type="email" id="email" name="email" required>
            </div>

            <div class="form-group">
                <label for="password"><?= Lang::get('auth.password') ?></label>
                <input type="password" id="password" name="password" required>
            </div>

            <button type="submit" class="btn btn-primary"><?= Lang::get('auth.login') ?></button>
        </form>

        <p class="auth-link">
            <?= Lang::get('auth.no_account') ?> <a href="/register"><?= Lang::get('auth.register') ?></a>
        </p>
    </div>
</div>

<?php
$content = ob_get_clean();
require __DIR__ . '/../layout.php';
?>
