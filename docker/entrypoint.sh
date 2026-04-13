#!/bin/sh
set -e

TRIES=0
MAX_TRIES=30

until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; do
  TRIES=$((TRIES + 1))
  if [ "$TRIES" -ge "$MAX_TRIES" ]; then
    echo "Database is not ready after $MAX_TRIES attempts."
    exit 1
  fi

  echo "Waiting for PostgreSQL... ($TRIES/$MAX_TRIES)"
  sleep 2
done

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  python manage.py migrate --no-input
fi

if [ "${RUN_COLLECTSTATIC:-false}" = "true" ]; then
  python manage.py collectstatic --no-input
fi

exec "$@"
