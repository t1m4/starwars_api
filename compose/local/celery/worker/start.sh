#!/bin/bash
celery -A starwars worker --concurrency=10 -l INFO