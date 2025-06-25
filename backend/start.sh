#!/bin/bash
set -e

python manage.py wait_for_database
python manage.py migrate
python manage.py collectstatic
cp -r collected_static/. /front/static/
gunicorn --bind 0.0.0.0:8000 backend.wsgi
