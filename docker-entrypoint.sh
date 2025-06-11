#!/bin/bash

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create test superuser
echo "Creating test superuser..."
python manage.py create_test_superuser

# Start the Django development server
echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000
