#!/bin/bash
echo "=======LOAD MODULE========"
echo $DJANGO_SETTINGS_MODULE
echo "=========================="
source /app/.venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py create_fixtures
touch /var/run/supervisor.sock && chmod 777 /var/run/supervisor.sock
supervisord -c /etc/supervisor/conf.d/supervisord.conf -n