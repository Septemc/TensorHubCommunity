#!/bin/bash
set -e

echo "Checking database state..."
python check_and_stamp.py

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000