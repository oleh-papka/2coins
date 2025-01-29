#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z "$DATABASE_HOST" "$DATABASE_PORT"; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

echo "Creating database migrations..."
python manage.py makemigrations

echo "Applying database migrations..."
python manage.py migrate

echo "Loading initial data..."
python manage.py loaddata currencies.json

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000