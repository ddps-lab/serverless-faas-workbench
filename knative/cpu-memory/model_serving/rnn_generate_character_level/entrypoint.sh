#!/bin/sh

# Defaults (can be overridden with env vars)
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-1}"
THREADS="${THREADS:-1}"
TIMEOUT="${TIMEOUT:-0}"

# Run gunicorn with dynamic values
exec gunicorn \
    --bind ":${PORT}" \
    --workers "${WORKERS}" \
    --threads "${THREADS}" \
    --timeout "${TIMEOUT}" \
    app:app

# docker run -t -v /mnt/data:/data --name wfbench --cpus=2 -p 127.0.0.1:80:8080/tcp andersonandrei/wfbench-knative:wfbench-local