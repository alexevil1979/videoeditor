<?php
use App\Core\Lang;
$title = Lang::get('auth.register');
ob_start();
?>

<div class="auth-container">
    <div class="auth-box">
        <h1><?= Lang::get('auth.register_title') ?></h1>
        
        <form method="POST" action="/register">
            <div class="form-group">
                <label for="email"><?= Lang::get('auth.email') ?></label>
                <input type="email" id="email" name="email" required>
            </div>

            <div class="form-group">
                <label for="password"><?= Lang::get('auth.password') ?></label>
                <input type="password" id="password" name="password" required minlength="8">
            </div>

            <div class="form-group">
                <label for="first_name"><?= Lang::get('auth.first_name') ?> (<?= Lang::get('common.optional') ?? 'optional' ?>)</label>
                <input type="text" id="first_name" name="first_name">
            </div>

            <div class="form-group">
                <label for="last_name"><?= Lang::get('auth.last_name') ?> (<?= Lang::get('common.optional') ?? 'optional' ?>)</label>
                <input type="text" id="last_name" name="last_name">
            </div>

            <button type="submit" class="btn btn-primary"><?= Lang::get('auth.register') ?></button>
        </form>

        <p class="auth-link">
            <?= Lang::get('auth.already_have_account') ?> <a href="/login"><?= Lang::get('auth.login') ?></a>
        </p>
    </div>
</div>

<?php
$content = ob_get_clean();
require __DIR__ . '/layout.php';
?>
