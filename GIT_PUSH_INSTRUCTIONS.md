# Инструкция по выгрузке в Git

## Проблема
Git репозиторий был инициализирован в домашней директории, а не в проекте. 

## Решение

Выполните эти команды в терминале **в директории проекта**:

```bash
# 1. Убедитесь что вы в директории проекта
cd "C:\Users\1\Documents\обработка видео"

# 2. Удалите .git из домашней директории (если есть)
Remove-Item "C:\Users\1\.git" -Recurse -Force -ErrorAction SilentlyContinue

# 3. Инициализируйте git в проекте
git init

# 4. Добавьте remote
git remote add origin https://github.com/alexevil1979/videoeditor.git

# 5. Добавьте все файлы
git add .

# 6. Сделайте коммит
git commit -m "Initial commit: Video Editor SaaS platform"

# 7. Переименуйте ветку в main
git branch -M main

# 8. Запушьте
git push -u origin main
```

## О предупреждениях LF/CRLF

Предупреждения типа:
```
warning: in the working copy of '.ollama/models/...', LF will be replaced by CRLF
```

Это **нормально** на Windows. Git автоматически конвертирует окончания строк. Это не ошибка.

## Если есть проблемы с lock файлом

```bash
Remove-Item "C:\Users\1\.git\index.lock" -Force
```
