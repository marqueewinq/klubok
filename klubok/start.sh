#!/usr/bin/bash
set -euxo pipefail

echo "yes" | python3 manage.py collectstatic
python3 manage.py migrate
gunicorn klubok.wsgi
