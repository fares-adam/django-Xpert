#!/bin/sh

# Wait for MySQL to be ready
echo "Waiting for MySQL..."
dockerize -wait tcp://db:3306 -timeout 60s

# Run migrations
python manage.py migrate

# Collect static files (if needed)
# python manage.py collectstatic --noinput

exec "$@"