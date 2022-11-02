#!/usr/bin/bash
set -euxo pipefail

echo "yes" | python3 manage.py collectstatic
python3 manage.py migrate
uvicorn --host ${HOST:-0.0.0.0} --port ${PORT:-80} klubok.asgi:application
