#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Building local images for Apple Silicon / arm64..."
docker build -t saifbiobaku/workout-api:latest -f "$REPO_ROOT/Dockerfile" "$REPO_ROOT"
docker build -t saifbiobaku/workout-web:latest \
  -f "$REPO_ROOT/nextjs/Dockerfile" \
  --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 \
  "$REPO_ROOT/nextjs"

echo
echo "Images ready:"
docker images | grep saifbiobaku/workout
