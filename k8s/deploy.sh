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
echo "Waiting for observability stack..."
kubectl rollout status deployment/otel-lgtm -n workout --timeout=180s

echo
echo "Restarting API so pods pick up ConfigMap env (OTEL endpoint)..."
kubectl rollout restart deployment/workout-api -n workout

echo
echo "Waiting for app deployments..."
kubectl rollout status deployment/workout-api -n workout --timeout=120s
kubectl rollout status deployment/workout-web -n workout --timeout=120s

echo
echo "Verify OTEL endpoint in the running API pod:"
kubectl exec -n workout deployment/workout-api -- env | grep OTEL_EXPORTER_OTLP_ENDPOINT || true

echo
kubectl get pods,svc -n workout
echo
echo "Frontend: http://localhost:3000"
echo "API:      http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo "Grafana:  http://localhost:3010  (admin / admin)"
echo
echo "Wait ~30s after rollout before querying Grafana (LGTM boot time)."
