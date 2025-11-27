#!/bin/bash

# Apply migrations
python manage.py migrate

# Collect static files (optional, if you use static files)
python manage.py collectstatic --noinput

# Run the development server
#!/bin/bash

# Use Railway PORT if exists, else default to 8000
PORT=${PORT:-8000}
python manage.py runserver 0.0.0.0:$PORT
