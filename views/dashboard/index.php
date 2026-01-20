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
        <h2>Мои пресеты</h2>
        <button type="button" class="btn btn-primary" onclick="showCreatePresetModal()">Создать новый пресет</button>
        <div class="presets-list" style="margin-top: 20px;">
            <?php if (empty($presets)): ?>
                <p>У вас пока нет пресетов. Создайте первый пресет для наложения кнопок на видео.</p>
            <?php else: ?>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Название</th>
                            <th>Описание</th>
                            <th>Элементы</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($presets as $preset): ?>
                            <tr>
                                <td><?= htmlspecialchars($preset['name']) ?></td>
                                <td><?= htmlspecialchars($preset['description'] ?? '') ?></td>
                                <td>
                                    <?php
                                    $items = \App\Models\Preset::getItems($preset['id']);
                                    $itemTypes = array_map(function($item) {
                                        return $item['type'];
                                    }, $items);
                                    echo implode(', ', array_unique($itemTypes));
                                    ?>
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-info" onclick="viewPreset(<?= $preset['id'] ?>)">Просмотр</button>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php endif; ?>
        </div>
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

<!-- Modal для создания пресета -->
<div id="createPresetModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; overflow-y: auto;">
    <div style="background: white; margin: 50px auto; padding: 30px; max-width: 800px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2>Создать новый пресет</h2>
        <form id="createPresetForm">
            <div class="form-group" style="margin-bottom: 15px;">
                <label>Название пресета:</label>
                <input type="text" name="preset_name" required style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            
            <div class="form-group" style="margin-bottom: 15px;">
                <label>Описание (необязательно):</label>
                <textarea name="preset_description" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; min-height: 60px;"></textarea>
            </div>

            <h3>Добавить элементы оверлея:</h3>
            <div id="presetItems" style="margin-bottom: 20px;">
                <!-- Элементы будут добавляться динамически -->
            </div>

            <div style="margin-bottom: 15px;">
                <button type="button" class="btn btn-secondary" onclick="addPresetItem('subscribe')">Добавить кнопку Subscribe</button>
                <button type="button" class="btn btn-secondary" onclick="addPresetItem('like')">Добавить кнопку Like</button>
                <button type="button" class="btn btn-secondary" onclick="addPresetItem('title')">Добавить заголовок</button>
            </div>

            <div style="display: flex; gap: 10px;">
                <button type="submit" class="btn btn-primary">Создать пресет</button>
                <button type="button" class="btn btn-secondary" onclick="hideCreatePresetModal()">Отмена</button>
            </div>
        </form>
    </div>
</div>

<script>
let presetItemCounter = 0;

function showCreatePresetModal() {
    document.getElementById('createPresetModal').style.display = 'block';
    presetItemCounter = 0;
    document.getElementById('presetItems').innerHTML = '';
}

function hideCreatePresetModal() {
    document.getElementById('createPresetModal').style.display = 'none';
}

function addPresetItem(type) {
    const itemsDiv = document.getElementById('presetItems');
    const itemId = presetItemCounter++;
    
    const itemDiv = document.createElement('div');
    itemDiv.className = 'preset-item';
    itemDiv.style.cssText = 'border: 1px solid #ddd; padding: 15px; margin-bottom: 10px; border-radius: 4px; background: #f9f9f9;';
    itemDiv.id = 'item-' + itemId;
    
    let itemHtml = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <strong>${type === 'subscribe' ? 'Кнопка Subscribe' : type === 'like' ? 'Кнопка Like' : 'Заголовок'}</strong>
            <button type="button" class="btn btn-sm btn-danger" onclick="removePresetItem(${itemId})">Удалить</button>
        </div>
        <input type="hidden" name="items[${itemId}][type]" value="${type}">
    `;
    
    if (type === 'title') {
        itemHtml += `
            <div class="form-group" style="margin-bottom: 10px;">
                <label>Текст заголовка:</label>
                <input type="text" name="items[${itemId}][text]" placeholder="Введите текст" style="width: 100%; padding: 6px;">
            </div>
        `;
    }
    
    itemHtml += `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
            <div>
                <label>Позиция X:</label>
                <select name="items[${itemId}][position_x]" style="width: 100%; padding: 6px;">
                    <option value="left">Слева</option>
                    <option value="center" selected>По центру</option>
                    <option value="right">Справа</option>
                </select>
            </div>
            <div>
                <label>Позиция Y:</label>
                <select name="items[${itemId}][position_y]" style="width: 100%; padding: 6px;">
                    <option value="top">Сверху</option>
                    <option value="center" selected>По центру</option>
                    <option value="bottom">Снизу</option>
                </select>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div>
                <label>Время появления (сек):</label>
                <input type="number" name="items[${itemId}][start_time]" value="0" step="0.1" min="0" style="width: 100%; padding: 6px;">
            </div>
            <div>
                <label>Время исчезновения (сек, необязательно):</label>
                <input type="number" name="items[${itemId}][end_time]" value="" step="0.1" min="0" style="width: 100%; padding: 6px;" placeholder="Оставить до конца">
            </div>
        </div>
    `;
    
    itemDiv.innerHTML = itemHtml;
    itemsDiv.appendChild(itemDiv);
}

function removePresetItem(itemId) {
    const itemDiv = document.getElementById('item-' + itemId);
    if (itemDiv) {
        itemDiv.remove();
    }
}

document.getElementById('createPresetForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const items = [];
    
    // Собираем все элементы пресета из DOM
    const itemDivs = document.querySelectorAll('#presetItems .preset-item');
    
    itemDivs.forEach((itemDiv) => {
        const itemId = itemDiv.id.replace('item-', '');
        const type = form.querySelector(`input[name="items[${itemId}][type]"]`)?.value;
        if (!type) return;
        
        const item = {
            type: type,
            position_x: form.querySelector(`select[name="items[${itemId}][position_x]"]`)?.value || 'center',
            position_y: form.querySelector(`select[name="items[${itemId}][position_y]"]`)?.value || 'center',
            start_time: parseFloat(form.querySelector(`input[name="items[${itemId}][start_time]"]`)?.value || 0),
            opacity: 1.0,
            scale: 1.0,
            animation: 'none',
            font_size: 24,
            font_color: '#FFFFFF'
        };
        
        const endTimeInput = form.querySelector(`input[name="items[${itemId}][end_time]"]`);
        if (endTimeInput && endTimeInput.value) {
            item.end_time = parseFloat(endTimeInput.value);
        }
        
        if (type === 'title') {
            const textInput = form.querySelector(`input[name="items[${itemId}][text]"]`);
            item.text = textInput ? textInput.value : '';
        }
        
        items.push(item);
    });
    
    if (items.length === 0) {
        alert('Добавьте хотя бы один элемент оверлея!');
        return;
    }
    
    const submitData = new FormData();
    submitData.append('name', form.querySelector('input[name="preset_name"]').value);
    submitData.append('description', form.querySelector('textarea[name="preset_description"]')?.value || '');
    submitData.append('items', JSON.stringify(items));
    
    try {
        const response = await fetch('/api/presets', {
            method: 'POST',
            body: submitData
        });
        
        const data = await response.json();
        if (data.success) {
            alert('Пресет успешно создан!');
            hideCreatePresetModal();
            location.reload();
        } else {
            alert('Ошибка: ' + data.message);
        }
    } catch (error) {
        alert('Ошибка при создании пресета: ' + error.message);
    }
});

function viewPreset(presetId) {
    window.location.href = '/api/presets/' + presetId;
}
</script>

<?php
$content = ob_get_clean();
require __DIR__ . '/../layout.php';
?>
