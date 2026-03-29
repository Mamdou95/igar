#!/bin/sh
set -e

until mc alias set myminio http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"; do
  echo "Waiting for MinIO..."
  sleep 2
done

mc mb --ignore-existing myminio/igar-temp
mc mb --ignore-existing --with-lock myminio/igar-vault
mc mb --ignore-existing myminio/igar-thumbnails

# Development lifecycle and retention settings.
mc ilm rule add myminio/igar-temp --expire-days 1 || true
mc retention set --default GOVERNANCE 1d myminio/igar-vault

echo "MinIO buckets initialized successfully."
