#!/usr/bin/env bash
# Создаёт недостающие базы данных в postgres-db-ucust.
# init.sql выполняется только при первом старте пустого volume,
# поэтому новые БД нужно создавать идемпотентно при каждом деплое.
set -e

CONTAINER="postgres-db-ucust"
DB_USER="${DB_USER:-ETA_DBUser}"
DATABASES="security_service_db user_service_db business_service_db notification_service_db billing_service_db generative_orchestration_service_db"

echo "Waiting for PostgreSQL to be ready..."
for i in $(seq 1 30); do
  if docker exec "$CONTAINER" pg_isready -U "$DB_USER" >/dev/null 2>&1; then
    echo "PostgreSQL is ready."
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "ERROR: PostgreSQL did not become ready in time" >&2
    exit 1
  fi
  sleep 2
done

for db in $DATABASES; do
  exists=$(docker exec "$CONTAINER" psql -U "$DB_USER" -tAc "SELECT 1 FROM pg_database WHERE datname='$db'")
  if [ "$exists" != "1" ]; then
    echo "Creating database: $db"
    docker exec "$CONTAINER" psql -U "$DB_USER" -c "CREATE DATABASE $db"
  else
    echo "Database already exists: $db"
  fi
done
echo "Done."