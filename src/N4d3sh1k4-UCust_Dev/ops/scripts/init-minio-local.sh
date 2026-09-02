#!/bin/bash
# MinIO init script for local non-Docker development
# Usage: ./ops/scripts/init-minio-local.sh
# Requires: mc (MinIO client) — install via `choco install minio-client` or `brew install minio/stable/mc`

set -e

MC="mc"
MINIO_ENDPOINT="http://127.0.0.1:9020"
ROOT_USER="admin"
ROOT_PASSWORD="password123"

echo "=== MinIO local init ==="

# Configure alias
$MC alias set local "$MINIO_ENDPOINT" "$ROOT_USER" "$ROOT_PASSWORD"

# --- Buckets ---
echo "Creating buckets..."
$MC mb local/business-service --ignore-existing
$MC mb local/generative-orchestration --ignore-existing

# --- Policies ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
POLICY_DIR="$SCRIPT_DIR/../minio/policies"

echo "Creating policies..."
$MC admin policy create local business-service-rw "$POLICY_DIR/business-service-rw.json"
$MC admin policy create local generative-orchestration-rw "$POLICY_DIR/generative-orchestration-rw.json"

# --- Users ---
echo "Creating users..."
$MC admin user add local business-service-user bus-strong-pass
$MC admin user add local generative-orchestration-user gen-strong-pass

# Attach policies
$MC admin policy attach local business-service-rw --user business-service-user
$MC admin policy attach local generative-orchestration-rw --user generative-orchestration-user

echo "=== Done ==="
echo "Users:"
echo "  admin                    — full access (root)"
echo "  business-service-user    — read/write business-service bucket"
echo "  generative-orchestration-user — read/write generative-orchestration bucket"
