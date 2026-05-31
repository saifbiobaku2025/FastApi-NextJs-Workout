#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$ROOT/.." && pwd)"

cd "$REPO_ROOT"

echo "Starting E2E stack and running Playwright in Docker..."
docker compose -f docker-compose.e2e.yml --env-file .env.e2e \
  --profile e2e run --rm --build playwright

echo
echo "Report: $ROOT/playwright-report/index.html"
