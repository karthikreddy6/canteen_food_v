#!/bin/sh
set -e

# Fix permissions on mounted volumes (runs as root)
chown -R onfood:onfood /app/logs
chown -R onfood:onfood /app/app/static

# Run init_db as root (it only does DB operations)
python init_db.py

# Drop to onfood user and start gunicorn
exec gosu onfood gunicorn app.main:app \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers ${WEB_CONCURRENCY:-4} \
    --timeout 120 \
    --graceful-timeout 30 \
    --access-logfile - \
    --error-logfile -
