#!/bin/bash
# set -e 

mypy .
black . --check
flake8 . tests
isort . --check-only
autoflake --remove-all-unused-imports --recursive --check  . | grep 'Unused imports/variables detected'