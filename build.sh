#!/usr/bin/env bash

set -o errexit

echo "ÔøΩÔøΩ Installing dependencies..."
pip install -r requirements.txt 

echo "Ìª† Running migrations..."
python manage.py migrate

echo "Ì≥Å Collecting static files..."
python manage.py collectstatic --noinput

