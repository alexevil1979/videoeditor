# Инструкция по коммиту изменений

Все изменения готовы к коммиту. Выполните следующие команды в терминале:

```bash
# 1. Добавить все изменения
git add -A

# 2. Проверить что будет закоммичено
git status

# 3. Создать коммит
git commit -m "Fix: Remove hard PHP extension requirements, add extension checks and installation guide

- Updated composer.json to remove hard extension requirements
- Added INSTALL_PHP_EXTENSIONS.md with detailed instructions
- Added GD extension check in FFmpegService with helpful error messages
- Updated README files with PHP extension requirements
- Updated all documentation with extension installation steps"

# 4. Запушить в репозиторий
git push origin main
```

## Измененные файлы:

- `composer.json` - убраны жесткие требования к расширениям
- `app/Services/FFmpegService.php` - добавлена проверка GD расширения
- `INSTALL_PHP_EXTENSIONS.md` - новый файл с инструкциями
- `README.md` - добавлена секция Recent Updates и Important
- `README_RU.md` - добавлена секция Последние обновления
- `QUICK_START.md` - добавлено предупреждение о расширениях
- `QUICK_START_RU.md` - добавлено предупреждение о расширениях
- `INSTALLATION.md` - добавлены команды проверки расширений
- `INSTALLATION_RU.md` - добавлены команды проверки расширений
