#!/bin/bash

if [ "${MODE}" == "runserver" ]; then
    python3 app/manage.py makemigrations
    python3 app/manage.py migrate
    python3 app/manage.py runserver 0:8001

elif [ "${MODE}" == "celery" ]; then
    celery -A settings worker -l info --autoscale=10,0 --pidfile=/tmp/celery.pid

elif [ "${MODE}" == "celerybeat" ]; then
    celery -A settings beat -l info --schedule=/tmp/celerybeat-schedule --pidfile=/tmp/celerybeat.pid

elif [ "${MODE}" == "flower" ]; then
    celery -A settings flower --port=5566
else
    gunicorn settings.wsgi:application --workers 4 --bind 0.0.0.0:8000 --threads 4 --timeout 3 --max-requests 1000 --log-level debug
fi