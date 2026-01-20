# Автоматический деплой в Git

## Настройка

После любых изменений в проекте я буду автоматически выполнять деплой в Git.

## Процесс деплоя

1. `git add -A` - добавление всех изменений
2. `git commit -m "..."` - создание коммита
3. `git push origin main` - отправка в репозиторий

## Ручной деплой (если нужно)

Запустите файл `deploy.bat` двойным кликом.

Или в командной строке:
```bash
cd "C:\Users\1\Documents\обработка видео"
git add -A
git commit -m "Your commit message"
git push origin main
```

## После деплоя на сервере

```bash
cd /ssd/www/videoeditor
git pull origin main
```
