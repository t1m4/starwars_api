#!/bin/bash

mypy .
black .
autoflake --remove-all-unused-imports --recursive --in-place .
flake8 .
isort .