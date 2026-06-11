# Library Project

Веб-приложение библиотеки на Django для учета книг, читателей и выдач.

Техническое задание под фактическую реализацию проекта находится в
[`docs/technical_specification.md`](docs/technical_specification.md).

Дополнительные материалы для диплома:

- [`docs/functional_audit.md`](docs/functional_audit.md) - соответствие проекта требованиям;
- [`docs/testing_plan.md`](docs/testing_plan.md) - план и результаты тестирования;
- [`docs/diploma_materials.md`](docs/diploma_materials.md) - архитектура, модель данных, маршруты и материалы для пояснительной записки;
- [`docs/explanatory_note_draft.md`](docs/explanatory_note_draft.md) - текстовый черновик пояснительной записки;
- [`docs/final_checklist.md`](docs/final_checklist.md) - чек-лист перед защитой;
- [`docs/presentation_outline.md`](docs/presentation_outline.md) - план презентации;
- [`docs/five_minute_speech.md`](docs/five_minute_speech.md) - текст доклада на 5 минут;
- [`docs/user_manual.md`](docs/user_manual.md) - руководство пользователя;
- [`docs/presentation.html`](docs/presentation.html) - HTML-презентация;
- [`docs/presentation.pdf`](docs/presentation.pdf) - PDF-версия презентации;
- [`docs/screenshots/`](docs/screenshots/) - скриншоты интерфейса.

## Возможности

- просмотр каталога книг и списка авторов;
- поиск книг по названию;
- фильтрация каталога по автору и жанру;
- просмотр детальной страницы книги;
- отображение года издания и обложки книги;
- регистрация, вход и личный кабинет читателя;
- выдача и возврат экземпляров книг;
- отображение просроченных книг в кабинете читателя;
- отчеты для библиотекаря:
  - книги на руках;
  - просроченные книги;
- управление данными через Django Admin.

## Стек

- Python 3.11+
- Django 5.2
- SQLite
- Pillow
- Bootstrap 5

## Быстрый старт

### Вариант 1. Через `make`

Из корня проекта:

```bash
make install
make migrate
make run
```

Если команда `make` недоступна в Windows PowerShell, используйте ручной запуск или вариант через `uv`.

После запуска приложение будет доступно по адресу:

```text
http://127.0.0.1:8000/
```

### Вариант 2. Вручную

Linux / WSL:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Вариант 3. Через `uv`

```bash
uv run --python 3.11 manage.py migrate
uv run --python 3.11 manage.py runserver
```

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Полезные команды

```bash
make superuser
make test
make check
make shell
```

Эквиваленты без `make`:

```bash
python manage.py createsuperuser
python manage.py test
python manage.py check
python manage.py shell
```

## Роли в системе

### Читатель

- просмотр каталога;
- поиск и фильтрация книг;
- регистрация и вход;
- просмотр личного кабинета;
- просмотр активных и завершенных выдач;
- получение предупреждения о просрочке;
- оформление выдачи доступного экземпляра.

### Библиотекарь

- доступ в Django Admin;
- возврат книг;
- просмотр отчетов по книгам на руках;
- просмотр отчета по просроченным книгам.

## Основные разделы

- `/catalog/` — главная страница каталога;
- `/catalog/books/` — список книг;
- `/catalog/authors/` — список авторов;
- `/profile/` — личный кабинет читателя;
- `/loans/reports/on-loan/` — книги на руках, только для staff;
- `/loans/reports/overdue/` — просроченные книги, только для staff;
- `/admin/` — административная панель Django.

## Структура проекта

```text
library_project/
├── apps/
│   ├── catalog/   # книги, авторы, жанры, экземпляры
│   ├── loans/     # выдача, возврат, отчеты
│   └── users/     # регистрация и профиль читателя
├── core/          # настройки и корневые маршруты
├── templates/     # HTML-шаблоны
├── media/         # загружаемые файлы, включая обложки
├── static/        # статические файлы
├── manage.py
├── Makefile
└── requirements.txt
```

## Тестирование

Проект покрыт тестами для:

- поиска и фильтрации каталога;
- регистрации читателя;
- выдачи и возврата книг;
- отображения профиля читателя;
- просроченных выдач;
- отчетов библиотекаря;
- защиты от двух активных выдач одного экземпляра.

Запуск:

```bash
make test
```

или

```bash
python manage.py test
```

Текущий проверенный результат:

```text
27 tests passed
```

## Сборка материалов диплома

Word-черновик пояснительной записки можно пересобрать из Markdown и скриншотов:

```powershell
$script = [System.IO.File]::ReadAllText('docs\build_explanatory_note.ps1', [System.Text.Encoding]::UTF8)
& ([scriptblock]::Create($script))
```

Скрипт обновляет файл `docs/Пояснительная записка - черновик.docx`, добавляет обновляемое содержание и встраивает скриншоты из `docs/screenshots/`.

## Медиафайлы

Обложки книг сохраняются в папке `media/books/covers/`.

В режиме разработки Django раздает медиа автоматически при `DEBUG = True`.

## Примечание

Для работы загрузки обложек и `ImageField` в зависимостях используется `Pillow`.
