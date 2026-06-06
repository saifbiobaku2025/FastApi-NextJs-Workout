#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$ROOT/.." && pwd)"

cd "$REPO_ROOT"

echo "Starting E2E stack and running Selenium pytest in Docker..."
docker compose -f docker-compose.e2e.yml --env-file .env.e2e \
  --profile selenium run --rm --build selenium-tests
