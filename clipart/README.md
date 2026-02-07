# Video CTA Overlay Editor

Десктопное приложение на Python для наложения анимированных призывов к действию (CTA) на видео.

## Возможности

- Загрузка видео (MP4, AVI, MKV, MOV, WebM и др.)
- Библиотека CTA-элементов: GIF-анимации, PNG-изображения (руки, стрелки, кнопки «Подписаться», «Лайк» и т.д.)
- Загрузка пользовательских файлов элементов
- Размещение элементов на видео кликом мыши
- Drag & drop для перемещения размещённых элементов
- Масштабирование угловыми маркерами
- Настройка: время появления, длительность, прозрачность, масштаб, fade in/out
- Превью в реальном времени с наложением
- Рендеринг итогового видео (MoviePy + libx264)
- Сохранение / загрузка проектов (.json)
- Автоматическая выгрузка на GitHub (GitPython)
- Undo / Redo (до 30 шагов)
- Тёмная тема, современный интерфейс

## Установка

```bash
# Клонировать репозиторий
git clone https://github.com/alexevil1979/clipart.git
cd clipart

# Установить зависимости
pip install -r requirements.txt
```

## Запуск

```bash
python main.py
```

## Структура проекта

```
clipart/
├── main.py                 # Точка входа
├── requirements.txt        # Зависимости Python
├── README.md               # Документация
├── assets/                 # CTA-элементы (GIF, PNG)
│   ├── hand_point_right.gif
│   ├── hand_point_down.gif
│   ├── arrow_right.gif
│   ├── subscribe_button.png
│   ├── like_heart.gif
│   └── ...
├── outputs/                # Готовые видео после рендеринга
├── projects/               # Сохранённые проекты (.json)
└── app/                    # Пакет приложения
    ├── __init__.py
    ├── main_window.py      # Главное окно
    ├── video_preview.py    # Превью видео + оверлеи
    ├── sidebar.py          # Библиотека + свойства элемента
    ├── elements_table.py   # Таблица наложенных элементов
    ├── render_engine.py    # Рендеринг через MoviePy
    ├── github_upload.py    # Выгрузка на GitHub
    ├── dialogs.py          # Диалоги (настройки, прогресс, о программе)
    ├── models.py           # Модели данных + Undo/Redo
    └── styles.py           # QSS-стили (тёмная тема)
```

## Содержимое папки assets/

Поместите в папку `assets/` файлы CTA-элементов. Рекомендуемый набор:

| Файл                      | Описание                                                        |
|---------------------------|-----------------------------------------------------------------|
| `hand_point_right.gif`    | Анимированная рука, указывающая вправо (→)                     |
| `hand_point_down.gif`     | Анимированная рука, указывающая вниз (↓)                       |
| `arrow_right.gif`         | Анимированная стрелка вправо                                    |
| `arrow_down.gif`          | Анимированная стрелка вниз                                      |
| `subscribe_button.png`    | Кнопка «Подписаться» (красная, YouTube-стиль)                  |
| `like_heart.gif`          | Анимированное сердце (лайк)                                     |
| `thumbs_up.gif`           | Анимированный палец вверх (лайк)                                |
| `bell_notification.gif`   | Анимированный колокольчик (уведомления)                        |
| `click_here.png`          | Надпись «Click Here» / «Нажми сюда»                            |
| `swipe_up.gif`            | Анимация свайпа вверх                                           |
| `tap_finger.gif`          | Анимация нажатия пальцем                                        |
| `circle_highlight.gif`    | Анимированный круг-подсветка                                    |

**Где взять:**
- [Giphy](https://giphy.com/) — поиск «pointing hand gif», «subscribe button» и т.д.
- [LottieFiles](https://lottiefiles.com/) — конвертировать Lottie в GIF
- [Flaticon](https://www.flaticon.com/) — PNG-иконки
- Создать самостоятельно в Canva, After Effects, или Figma

## Настройка GitHub

1. Откройте **Настройки** в приложении
2. Укажите путь к локальному клону репозитория
3. Введите GitHub Personal Access Token (с правами `repo`)
4. Создать токен: [github.com/settings/tokens](https://github.com/settings/tokens)

## Горячие клавиши

| Клавиша        | Действие                |
|----------------|-------------------------|
| `Ctrl+O`       | Открыть видео           |
| `Ctrl+S`       | Сохранить проект        |
| `Ctrl+Shift+O` | Открыть проект          |
| `Ctrl+Z`       | Отменить                |
| `Ctrl+Y`       | Повторить               |
| `Ctrl+Q`       | Выход                   |

## Технологии

- **PyQt6** — интерфейс
- **MoviePy** — рендеринг видео
- **OpenCV** — чтение видеокадров для превью
- **Pillow** — обработка GIF-анимаций
- **NumPy** — работа с массивами пикселей
- **GitPython** — интеграция с GitHub

## Лицензия

MIT
