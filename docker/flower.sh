#!/bin/bash

SERVICE_NAME=Redis SERVICE_HOST=${REDIS_HOST} SERVICE_PORT=${REDIS_PORT} ./docker/wait-for-service.sh

exec celery -A starwars flower --address=${FLOWER_HOST} --port=${FLOWER_PORT}