#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Removing workout app from Kubernetes..."
kubectl delete -k "$ROOT" --ignore-not-found
