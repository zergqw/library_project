# Деплой на Render

Проект подготовлен к деплою как Django Web Service с PostgreSQL, WhiteNoise и Gunicorn.

## Вариант 1: через Blueprint

1. Запушить проект в GitHub/GitLab.
2. В Render открыть `Blueprints` -> `New Blueprint Instance`.
3. Выбрать репозиторий с проектом.
4. Render прочитает `render.yaml` и создаст:
   - web service `library-project`;
   - PostgreSQL database `library-project-db`;
   - переменные окружения `DATABASE_URL`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`.
5. Дождаться завершения build/deploy.

## Вариант 2: вручную

1. Создать PostgreSQL database на Render.
2. Создать Web Service из репозитория.
3. Указать:

```bash
Build Command: bash build.sh
Start Command: python -m gunicorn core.wsgi:application
```

4. Добавить переменные окружения:

```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<generate value>
DATABASE_URL=<Internal Database URL from Render PostgreSQL>
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=<your admin password>
DJANGO_SEED_DEMO_DATA=True
WEB_CONCURRENCY=4
```

`DJANGO_ALLOWED_HOSTS` можно не указывать для стандартного домена Render: приложение автоматически добавляет `RENDER_EXTERNAL_HOSTNAME`.

## Что делает build.sh

```bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py ensure_superuser
```

Если `DJANGO_SEED_DEMO_DATA=True`, build дополнительно выполнит:

```bash
python manage.py seed_demo_data
```

## После деплоя

Если Render Shell недоступен на тарифе, администратор создается автоматически во время build по переменным:

```env
DJANGO_SUPERUSER_USERNAME
DJANGO_SUPERUSER_EMAIL
DJANGO_SUPERUSER_PASSWORD
```

Если `DJANGO_SUPERUSER_PASSWORD` не задан, команда `ensure_superuser` пропустит создание администратора и деплой не упадет.

Демонстрационные данные создаются автоматически, если задано `DJANGO_SEED_DEMO_DATA=True`.

## Важно про media

Static-файлы (`static`) собираются в `staticfiles` и отдаются через WhiteNoise.

Загружаемые файлы (`media`), например обложки книг, на бесплатном web service Render не являются надежным постоянным хранилищем. Для дипломной демонстрации это допустимо, но для реального использования лучше подключить Render Disk, S3 или Cloudinary.
