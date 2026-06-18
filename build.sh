#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py ensure_superuser

if [ "$DJANGO_SEED_DEMO_DATA" = "True" ] || [ "$DJANGO_SEED_DEMO_DATA" = "true" ] || [ "$DJANGO_SEED_DEMO_DATA" = "1" ]; then
    python manage.py seed_demo_data
fi
