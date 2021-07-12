#! /usr/bin/env bash

# Let the DB start
python api/backend_pre_start.py

# Run migrations
alembic upgrade heads

gunicorn -k uvicorn.workers.UvicornWorker -c /gunicorn_conf.py api.main:app
