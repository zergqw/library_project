# Library Project

Веб-приложение библиотеки на Django. Проект позволяет вести каталог книг,
авторов и жанров, регистрировать читателей, оформлять выдачу и возврат
экземпляров, а также смотреть отчеты по книгам на руках и просроченным выдачам.

## Возможности

- каталог книг с поиском и фильтрацией по автору и жанру;
- страницы книг и авторов;
- хранение года издания, ISBN и обложек книг;
- регистрация, вход и личный кабинет читателя;
- оформление выдачи доступного экземпляра;
- возврат книг сотрудником библиотеки;
- отметка активных и просроченных выдач;
- отчеты для библиотекаря;
- управление данными через Django Admin;
- команды для генерации демонстрационных данных и обложек.

## Стек

- Python 3.11+
- Django 5.2
- SQLite
- Pillow
- Bootstrap 5
- uv, опционально

## Быстрый старт

Рекомендуемый вариант запуска:

```powershell
uv run --python 3.11 manage.py migrate
uv run --python 3.11 manage.py runserver
```

После запуска приложение доступно по адресу:

```text
http://127.0.0.1:8000/
```

Если `uv` не установлен, можно использовать обычное виртуальное окружение:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

На Linux / WSL:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Настройки окружения

В репозитории есть файл `.env.example` с примером переменных:

```env
DJANGO_SECRET_KEY=change-me-generate-a-long-random-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

Для локальной разработки проект запускается и без переменных окружения:
используется безопасный для разработки fallback-ключ и `DEBUG=True`.

Для публикации или деплоя задайте переменные окружения вручную. Пример для
PowerShell:

```powershell
$env:DJANGO_SECRET_KEY="your-long-random-secret-key"
$env:DJANGO_DEBUG="False"
$env:DJANGO_ALLOWED_HOSTS="example.com,127.0.0.1,localhost"
```

Настоящий `.env` игнорируется Git. В репозиторий должен попадать только
`.env.example`.

## Демо-данные

База `db.sqlite3` и папка `media/` не хранятся в Git. После клонирования проекта
их можно восстановить командами:

```powershell
uv run --python 3.11 manage.py migrate
uv run --python 3.11 manage.py seed_demo_data
uv run --python 3.11 manage.py apply_online_covers
```

`seed_demo_data` создает жанры, авторов, книги, экземпляры, читателей и выдачи.
Также генерирует локальные обложки через Pillow.

`apply_online_covers` скачивает открытые тематические изображения из интернета,
обрабатывает их под формат обложек и сохраняет ссылки на источники в:

```text
media/books/covers/online/sources.json
```

Для вымышленных demo-книг используются тематические изображения, а не
официальные обложки.

Демо-пользователи:

```text
demo.reader1 ... demo.reader6
password: demo12345
```

Сотрудник библиотеки:

```text
demo.librarian
password: demo12345
```

## Полезные команды

Через `uv`:

```powershell
uv run --python 3.11 manage.py check
uv run --python 3.11 manage.py test
uv run --python 3.11 manage.py createsuperuser
uv run --python 3.11 manage.py shell
```

Через активированное виртуальное окружение:

```powershell
python manage.py check
python manage.py test
python manage.py createsuperuser
python manage.py shell
```

В проекте также есть `Makefile`:

```bash
make install
make migrate
make run
make test
make check
```

На Windows удобнее использовать команды через `uv` или PowerShell-вариант с
виртуальным окружением.

## Основные разделы

- `/catalog/` - главная страница каталога;
- `/catalog/books/` - список книг;
- `/catalog/books/<id>/` - страница книги;
- `/catalog/authors/` - список авторов;
- `/catalog/authors/<id>/` - страница автора;
- `/signup/` - регистрация читателя;
- `/accounts/login/` - вход;
- `/profile/` - личный кабинет;
- `/loans/reports/on-loan/` - отчет по книгам на руках;
- `/loans/reports/overdue/` - отчет по просроченным книгам;
- `/admin/` - административная панель Django.

## Структура проекта

```text
library_project/
|-- apps/
|   |-- catalog/   # книги, авторы, жанры, экземпляры
|   |-- loans/     # выдачи, возвраты, отчеты
|   `-- users/     # регистрация и профиль читателя
|-- core/          # настройки и корневые маршруты
|-- templates/     # HTML-шаблоны
|-- media/         # загружаемые файлы, игнорируется Git
|-- static/        # статические файлы проекта
|-- manage.py
|-- Makefile
|-- pyproject.toml
`-- requirements.txt
```

## Git и файлы вне репозитория

В `.gitignore` вынесены локальные и генерируемые файлы:

- `db.sqlite3`;
- `media/`;
- `docs/`;
- `.env`;
- `.venv/`, `venv/`;
- `__pycache__/` и кеши инструментов.

Это значит, что на GitHub попадает код проекта, шаблон настроек и команды для
восстановления локальных данных, но не сама база, медиафайлы и черновые
материалы.

## Тестирование

Запуск тестов:

```powershell
uv run --python 3.11 manage.py test
```

или:

```powershell
python manage.py test
```

Быстрая проверка конфигурации:

```powershell
uv run --python 3.11 manage.py check
```

## Примечания

- Для работы `ImageField` и генерации обложек используется Pillow.
- Команда `apply_online_covers` требует доступ в интернет.
- При `DJANGO_DEBUG=False` переменная `DJANGO_SECRET_KEY` обязательна.
