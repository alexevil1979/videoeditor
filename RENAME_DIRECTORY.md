# Переименование каталога проекта

## Проблема
Каталог проекта содержит кириллицу: `обработка видео`
Это вызывает проблемы с PowerShell и Git командами.

## Решение
Переименовать каталог в: `videoeditor`

## Инструкция

### На Windows:

1. **Закройте все программы, использующие каталог:**
   - Закройте Cursor/IDE
   - Закройте все терминалы
   - Убедитесь что Git не выполняет операции

2. **Переименуйте каталог:**
   - Откройте проводник Windows
   - Перейдите в: `C:\Users\1\Documents\`
   - Переименуйте: `обработка видео` → `videoeditor`
   - Или через командную строку:
   ```cmd
   cd "C:\Users\1\Documents"
   ren "обработка видео" videoeditor
   ```

3. **Откройте проект в новом каталоге:**
   - Откройте Cursor/IDE
   - Откройте каталог: `C:\Users\1\Documents\videoeditor`

4. **Проверьте Git:**
   ```bash
   cd "C:\Users\1\Documents\videoeditor"
   git status
   git remote -v
   ```

5. **Отправьте изменения:**
   ```bash
   git add -A
   git commit -m "Fix: Remove FallbackResource, fix layout.php paths, remove DirectoryMatch, add create-admin script"
   git push origin main
   ```

## После переименования

- ✅ PowerShell будет работать нормально
- ✅ Git команды будут выполняться без ошибок
- ✅ Все bat-файлы будут работать корректно
- ✅ Путь на сервере остается: `/ssd/www/videoeditor`
- ✅ Локальный путь теперь: `C:\Users\1\Documents\videoeditor`

## Важно

- Git репозиторий сохранится после переименования
- Все файлы останутся на месте
- Нужно только переоткрыть проект в IDE
