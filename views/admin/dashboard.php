<?php
use App\Core\Lang;
$title = Lang::get('admin.title');
ob_start();
?>

<div class="admin-dashboard">
    <h1><?= Lang::get('admin.title') ?></h1>

    <div class="stats-grid">
        <div class="stat-card">
            <h3><?= Lang::get('admin.total_users') ?></h3>
            <p class="stat-value"><?= $stats['total_users'] ?></p>
        </div>
        <div class="stat-card">
            <h3><?= Lang::get('admin.total_videos') ?></h3>
            <p class="stat-value"><?= $stats['total_videos'] ?></p>
        </div>
        <div class="stat-card">
            <h3><?= Lang::get('admin.total_jobs') ?></h3>
            <p class="stat-value"><?= $stats['total_jobs'] ?></p>
        </div>
        <div class="stat-card">
            <h3><?= Lang::get('admin.queue_status') ?></h3>
            <p><?= Lang::get('admin.pending') ?>: <?= $stats['queue_stats']['pending'] ?></p>
            <p><?= Lang::get('admin.processing') ?>: <?= $stats['queue_stats']['processing'] ?></p>
            <p><?= Lang::get('admin.completed') ?>: <?= $stats['queue_stats']['completed'] ?></p>
            <p><?= Lang::get('admin.failed') ?>: <?= $stats['queue_stats']['failed'] ?></p>
        </div>
    </div>

    <div class="dashboard-section">
        <h2><?= Lang::get('admin.recent_jobs') ?></h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>User</th>
                    <th>Video</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($recent_jobs as $job): ?>
                    <tr>
                        <td><?= $job['id'] ?></td>
                        <td><?= htmlspecialchars($job['user_email'] ?? 'N/A') ?></td>
                        <td><?= htmlspecialchars($job['original_filename'] ?? 'N/A') ?></td>
                        <td><span class="badge badge-<?= $job['status'] ?>"><?= $job['status'] ?></span></td>
                        <td><?= date('Y-m-d H:i', strtotime($job['created_at'])) ?></td>
                        <td>
                            <?php if ($job['status'] === 'pending' || $job['status'] === 'processing'): ?>
                                <button class="btn btn-sm btn-danger" onclick="cancelJob(<?= $job['id'] ?>)">Cancel</button>
                            <?php endif; ?>
                            <?php if ($job['status'] === 'failed'): ?>
                                <button class="btn btn-sm btn-primary" onclick="restartJob(<?= $job['id'] ?>)">Restart</button>
                            <?php endif; ?>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>

    <div class="dashboard-section">
        <h2>Recent Users</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Email</th>
                    <th>Name</th>
                    <th>Credits</th>
                    <th>Created</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($recent_users as $user): ?>
                    <tr>
                        <td><?= $user['id'] ?></td>
                        <td><?= htmlspecialchars($user['email']) ?></td>
                        <td><?= htmlspecialchars(($user['first_name'] ?? '') . ' ' . ($user['last_name'] ?? '')) ?></td>
                        <td><?= number_format($user['credits'] ?? 0, 2) ?></td>
                        <td><?= date('Y-m-d H:i', strtotime($user['created_at'])) ?></td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="editBalance(<?= $user['id'] ?>)">Edit Balance</button>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>

<script>
function cancelJob(jobId) {
    if (!confirm('Cancel this job?')) return;
    
    fetch(`/admin/jobs/${jobId}/cancel`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        });
}

function restartJob(jobId) {
    fetch(`/admin/jobs/${jobId}/restart`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        });
}

function editBalance(userId) {
    const amount = prompt('Enter amount (positive to add, negative to subtract):');
    if (amount === null) return;
    
    const type = parseFloat(amount) >= 0 ? 'credit' : 'debit';
    
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('amount', Math.abs(parseFloat(amount)));
    formData.append('type', type);
    
    fetch('/admin/balance', { method: 'POST', body: formData })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        });
}
</script>

<?php
$content = ob_get_clean();
require __DIR__ . '/../layout.php';
?>
