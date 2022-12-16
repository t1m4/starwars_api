#!/bin/bash

SERVICE_NAME=Redis SERVICE_HOST=${REDIS_HOST} SERVICE_PORT=${REDIS_PORT} ./docker/wait-for-service.sh

./manage.py migrate  --no-input --traceback