#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$ROOT/.." && pwd)"

if [[ "$(uname -m)" == "arm64" ]]; then
  if ! docker image inspect saifbiobaku/workout-api:latest >/dev/null 2>&1; then
    echo "No local arm64 image found; building from source..."
    "$ROOT/build-local.sh"
  fi
fi

echo "Deploying workout app to Kubernetes (namespace: workout)..."
kubectl apply -k "$ROOT"

echo
echo "Waiting for deployments..."
kubectl rollout status deployment/workout-api -n workout --timeout=120s
kubectl rollout status deployment/workout-web -n workout --timeout=120s

echo
kubectl get pods,svc -n workout
echo
echo "Frontend: http://localhost:3000"
echo "API:      http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
