<?php
use App\Core\Lang;
$title = Lang::get('dashboard.title');
ob_start();
?>

<div class="dashboard">
    <h1><?= Lang::get('dashboard.title') ?></h1>

    <div class="stats-grid">
        <div class="stat-card">
            <h3><?= Lang::get('dashboard.credits') ?></h3>
            <p class="stat-value"><?= number_format($balance['credits'] ?? 0, 2) ?></p>
        </div>
        <div class="stat-card">
            <h3><?= Lang::get('dashboard.videos') ?></h3>
            <p class="stat-value"><?= count($videos) ?></p>
        </div>
        <div class="stat-card">
            <h3><?= Lang::get('dashboard.jobs') ?></h3>
            <p class="stat-value"><?= count($jobs) ?></p>
        </div>
    </div>

    <div class="dashboard-section">
        <h2><?= Lang::get('dashboard.upload_video') ?></h2>
        <form id="uploadForm" enctype="multipart/form-data">
            <input type="file" name="video" accept="video/*" required>
            <button type="submit" class="btn btn-primary">Upload</button>
        </form>
        <div id="uploadStatus"></div>
    </div>

    <div class="dashboard-section">
        <h2><?= Lang::get('dashboard.my_videos') ?></h2>
        <div class="video-list">
            <?php if (empty($videos)): ?>
                <p><?= Lang::get('dashboard.no_videos') ?></p>
            <?php else: ?>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th><?= Lang::get('video.filename') ?></th>
                            <th><?= Lang::get('video.size') ?></th>
                            <th><?= Lang::get('video.duration') ?></th>
                            <th><?= Lang::get('dashboard.status') ?></th>
                            <th><?= Lang::get('dashboard.actions') ?></th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($videos as $video): ?>
                            <tr>
                                <td><?= htmlspecialchars($video['original_filename']) ?></td>
                                <td><?= number_format($video['file_size'] / 1024 / 1024, 2) ?> MB</td>
                                <td><?= number_format($video['duration'] ?? 0, 1) ?>s</td>
                                <td><span class="badge badge-<?= $video['status'] ?>"><?= $video['status'] ?></span></td>
                                <td>
                                    <select class="preset-select" data-video-id="<?= $video['id'] ?>">
                                        <option value=""><?= Lang::get('dashboard.select_preset') ?></option>
                                        <?php foreach ($presets as $preset): ?>
                                            <option value="<?= $preset['id'] ?>"><?= htmlspecialchars($preset['name']) ?></option>
                                        <?php endforeach; ?>
                                    </select>
                                    <button class="btn btn-sm btn-primary render-btn" data-video-id="<?= $video['id'] ?>"><?= Lang::get('dashboard.render') ?></button>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php endif; ?>
        </div>
    </div>

    <div class="dashboard-section">
        <h2><?= Lang::get('dashboard.render_jobs') ?></h2>
        <div class="jobs-list">
            <?php if (empty($jobs)): ?>
                <p><?= Lang::get('dashboard.no_jobs') ?></p>
            <?php else: ?>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th><?= Lang::get('video.filename') ?></th>
                            <th><?= Lang::get('dashboard.select_preset') ?></th>
                            <th><?= Lang::get('dashboard.status') ?></th>
                            <th><?= Lang::get('common.progress') ?? 'Progress' ?></th>
                            <th><?= Lang::get('dashboard.created') ?></th>
                            <th><?= Lang::get('dashboard.actions') ?></th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($jobs as $job): ?>
                            <tr>
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
                                    <?php if ($job['status'] === 'completed'): ?>
                                        <a href="/api/videos/download/<?= $job['id'] ?>" class="btn btn-sm btn-success"><?= Lang::get('dashboard.download') ?></a>
                                    <?php endif; ?>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php endif; ?>
        </div>
    </div>
</div>

<script>
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const statusDiv = document.getElementById('uploadStatus');
    
    statusDiv.textContent = '<?= Lang::get('video.uploading') ?>';
    
    try {
        const response = await fetch('/api/videos/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        if (data.success) {
            statusDiv.textContent = '<?= Lang::get('video.upload_success') ?>';
            setTimeout(() => location.reload(), 1000);
        } else {
            statusDiv.textContent = '<?= Lang::get('common.error') ?>: ' + data.message;
        }
    } catch (error) {
        statusDiv.textContent = '<?= Lang::get('video.upload_error') ?>: ' + error.message;
    }
});

document.querySelectorAll('.render-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
        const videoId = btn.dataset.videoId;
        const presetSelect = document.querySelector(`.preset-select[data-video-id="${videoId}"]`);
        const presetId = presetSelect.value;
        
        if (!presetId) {
            alert('<?= Lang::get('dashboard.select_preset') ?>');
            return;
        }
        
        const formData = new FormData();
        formData.append('video_id', videoId);
        formData.append('preset_id', presetId);
        
        try {
            const response = await fetch('/api/videos/render', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            if (data.success) {
                alert('Render job created!');
                location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        } catch (error) {
            alert('Failed: ' + error.message);
        }
    });
});
</script>

<?php
$content = ob_get_clean();
require __DIR__ . '/../layout.php';
?>
