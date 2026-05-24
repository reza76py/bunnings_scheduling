#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/var/www/bunnings_scheduling"
COMPOSE_FILE="docker-compose.prod.yml"

cd "$PROJECT_DIR"

git fetch origin
git reset --hard origin/main

docker compose -f "$COMPOSE_FILE" build --pull

docker compose -f "$COMPOSE_FILE" up -d --wait db
docker compose -f "$COMPOSE_FILE" up -d --scale backend=2 backend

docker compose -f "$COMPOSE_FILE" exec -T backend python manage.py migrate --settings=config.settings.production
docker compose -f "$COMPOSE_FILE" exec -T backend python manage.py collectstatic --noinput --settings=config.settings.production

docker compose -f "$COMPOSE_FILE" up -d frontend
docker compose -f "$COMPOSE_FILE" up -d --remove-orphans