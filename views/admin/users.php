<?php
$title = 'Users Management';
ob_start();
?>

<div class="admin-page">
    <h1>Users Management</h1>
    <a href="/admin" class="btn btn-secondary">Back to Dashboard</a>
    
    <table class="data-table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Email</th>
                <th>Name</th>
                <th>Role</th>
                <th>Credits</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($users as $user): ?>
                <tr>
                    <td><?= $user['id'] ?></td>
                    <td><?= htmlspecialchars($user['email']) ?></td>
                    <td><?= htmlspecialchars(($user['first_name'] ?? '') . ' ' . ($user['last_name'] ?? '')) ?></td>
                    <td><span class="badge"><?= $user['role'] ?></span></td>
                    <td><?= number_format($user['credits'] ?? 0, 2) ?></td>
                    <td><span class="badge badge-<?= $user['status'] ?>"><?= $user['status'] ?></span></td>
                    <td><?= date('Y-m-d H:i', strtotime($user['created_at'])) ?></td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editBalance(<?= $user['id'] ?>)">Edit Balance</button>
                    </td>
                </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
</div>

<script>
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
