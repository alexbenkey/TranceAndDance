#!/bin/bash

# dont want to make unecessary migrations everytime i make an image
# run migrations only if there are unapplied changes
echo "Checking for pending migrations..."
python manage.py makemigrations --check --dry-run

if [ $? -eq 0 ]; then
  echo "Applying migrations..."
  python manage.py migrate
else
  echo "No migrations needed."
fi

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
