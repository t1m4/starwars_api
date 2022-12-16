#!/bin/bash
set -e

SERVICE_NAME=Redis SERVICE_HOST=${REDIS_HOST} SERVICE_PORT=${REDIS_PORT} ./docker/wait-for-service.sh

if [[ $ENVIRONMENT == "local" ]]; then
    bash docker/init.sh
    exec python manage.py runserver 0.0.0.0:8000 --traceback --insecure
else
    exec gunicorn -b 0.0.0.0:8000 wsgi --timeout=360 --worker-class=gevent --workers ${GUNICORN_WORKERS} --statsd-host ${DATADOG_STATSD_HOST}:${DATADOG_STATSD_PORT} --dogstatsd-tags facebook-instagram
fi
