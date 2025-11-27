#!/bin/bash

# Use Railway PORT if defined, otherwise default to 8000
PORT=${PORT:-8000}

# Apply migrations
python manage.py migrate

# Collect static files (optional)
python manage.py collectstatic --noinput

# Start the app with Gunicorn
gunicorn myproject.wsgi:application --bind 0.0.0.0:$PORT
