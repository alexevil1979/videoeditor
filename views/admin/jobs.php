<?php
$title = 'Jobs Management';
ob_start();
?>

<div class="admin-page">
    <h1>Render Jobs Management</h1>
    <a href="/admin" class="btn btn-secondary">Back to Dashboard</a>
    
    <table class="data-table">
        <thead>
            <tr>
                <th>ID</th>
                <th>User</th>
                <th>Video</th>
                <th>Preset</th>
                <th>Status</th>
                <th>Progress</th>
                <th>Created</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($jobs as $job): ?>
                <tr>
                    <td><?= $job['id'] ?></td>
                    <td><?= htmlspecialchars($job['user_email'] ?? 'N/A') ?></td>
                    <td><?= htmlspecialchars($job['original_filename'] ?? 'N/A') ?></td>
                    <td><?= htmlspecialchars($job['preset_name'] ?? 'N/A') ?></td>
                    <td><span class="badge badge-<?= $job['status'] ?>"><?= $job['status'] ?></span></td>
                    <td>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: <?= $job['progress'] ?>%"></div>
                        </div>
                    </td>
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
</script>

<?php
$content = ob_get_clean();
require __DIR__ . '/../layout.php';
?>
