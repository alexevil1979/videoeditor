<?php
use App\Core\Lang;
$currentLang = Lang::current();
$supportedLangs = Lang::supported();
?>
<!DOCTYPE html>
<html lang="<?= $currentLang ?>">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= $title ?? Lang::get('app.title') ?></title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a href="/" class="logo">Video Editor</a>
            <div class="nav-right">
                <?php if (isset($user)): ?>
                    <div class="nav-links">
                        <a href="/dashboard"><?= Lang::get('dashboard.title') ?></a>
                        <?php if ($user['role'] === 'admin'): ?>
                            <a href="/admin"><?= Lang::get('admin.title') ?></a>
                        <?php endif; ?>
                        <a href="/logout"><?= Lang::get('auth.logout') ?></a>
                    </div>
                <?php endif; ?>
                <div class="language-selector">
                    <select id="languageSelect" onchange="switchLanguage(this.value)">
                        <?php foreach ($supportedLangs as $lang): ?>
                            <option value="<?= $lang ?>" <?= $lang === $currentLang ? 'selected' : '' ?>>
                                <?= Lang::name($lang) ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>
            </div>
        </div>
    </nav>

    <main class="container">
        <?php if (isset($error)): ?>
            <div class="alert alert-error"><?= htmlspecialchars($error) ?></div>
        <?php endif; ?>
        <?php if (isset($success)): ?>
            <div class="alert alert-success"><?= htmlspecialchars($success) ?></div>
        <?php endif; ?>

        <?= $content ?? '' ?>
    </main>

    <footer>
        <div class="container">
            <p>&copy; <?= date('Y') ?> <?= Lang::get('app.name') ?>. <?= Lang::get('common.all_rights_reserved') ?? 'All rights reserved.' ?></p>
        </div>
    </footer>

    <script src="/assets/js/app.js"></script>
    <script>
        function switchLanguage(lang) {
            window.location.href = '/lang/' + lang + '?redirect=' + encodeURIComponent(window.location.pathname);
        }
    </script>
</body>
</html>
