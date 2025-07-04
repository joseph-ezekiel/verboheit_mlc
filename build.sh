#!/usr/bin/env bash

set -o errexit

echo "ÔøΩÔøΩ Installing dependencies..."
uv pip install -r requirements.txt 

echo "Ìª† Running migrations..."
python manage.py migrate

echo "Ì≥Å Collecting static files..."
python manage.py collectstatic --noinput
