# Workout App — Kubernetes (Docker Desktop)

Manifests to run the workout application on a local Kubernetes cluster (Docker Desktop). Images are pulled from Docker Hub:

| Service  | Image                              | Port |
|----------|------------------------------------|------|
| API      | `saifbiobaku/workout-api:latest`   | 8000 |
| Frontend | `saifbiobaku/workout-web:latest`   | 3000 |

## Prerequisites

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
2. Kubernetes enabled: **Settings → Kubernetes → Enable Kubernetes**
3. `kubectl` available (bundled with Docker Desktop)

Verify your cluster is running:

```bash
kubectl cluster-info
```

## Quick start

From the repository root:

```bash
./k8s/deploy.sh
```

Or manually:

```bash
kubectl apply -k k8s/
kubectl rollout status deployment/workout-api -n workout
kubectl rollout status deployment/workout-web -n workout
```

Open the app:

| URL | Description |
|-----|-------------|
| http://localhost:3000 | Frontend |
| http://localhost:8000 | API |
| http://localhost:8000/docs | Swagger docs |

## Folder layout

```
k8s/
├── kustomization.yaml   # Kustomize entry point (order + secret generation)
├── namespace.yaml       # workout namespace
├── configmap.yaml       # AUTH_ALGORITHM, DATABASE_URL
├── api-pvc.yaml         # PersistentVolumeClaim for SQLite data
├── api-deployment.yaml
├── api-service.yaml     # LoadBalancer :8000
├── web-deployment.yaml
├── web-service.yaml     # LoadBalancer :3000
├── deploy.sh            # Deploy + wait for rollouts
├── build-local.sh       # Build arm64 images locally (Apple Silicon)
├── teardown.sh          # Remove all resources
└── examples/
    └── secret.yaml      # Template for a custom secret
```

## Important: use Kustomize (`-k`), not plain `-f`

Always deploy with:

```bash
kubectl apply -k k8s/    # correct
```

Do **not** use:

```bash
kubectl apply -f k8s/    # wrong
```

Plain `-f` ignores `kustomization.yaml`, applies files in alphabetical order (API before namespace), and tries to apply the Kustomization file as a cluster resource. That leads to partial or failed deploys.

## ARM64 vs AMD64 (Apple Silicon)

### The problem

Docker images are built for a specific CPU architecture. GitHub Actions runners use **linux/amd64** (Intel/AMD). Apple Silicon Macs and Docker Desktop Kubernetes on M-series chips run **linux/arm64**.

If an image on Docker Hub only has an amd64 manifest, Kubernetes on Apple Silicon fails with:

```
Failed to pull image "saifbiobaku/workout-api:latest":
no matching manifest for linux/arm64/v8 in the manifest list entries
```

The pod stays in `ImagePullBackOff` / `ErrImagePull`.

### How this repo handles it

**CI (long-term fix)** — `.github/workflows/docker-publish.yml` builds and pushes **multi-arch** images for both platforms:

```yaml
platforms: linux/amd64,linux/arm64
```

After the workflow runs on `main`, `docker pull` works on both Intel and Apple Silicon.

**Local dev (immediate fix on Mac)** — if arm64 images are not on Docker Hub yet, build locally:

```bash
./k8s/build-local.sh
kubectl apply -k k8s/
kubectl rollout restart deployment/workout-api deployment/workout-web -n workout
```

`deploy.sh` detects arm64 and runs `build-local.sh` automatically when the local image is missing.

Deployments use `imagePullPolicy: IfNotPresent`, so Kubernetes uses a locally built image when it exists instead of always pulling from the registry.

### Architecture cheat sheet

| Environment | Architecture | Image source |
|-------------|--------------|--------------|
| GitHub Actions runner | amd64 | Built in CI |
| Docker Desktop K8s on Intel Mac | amd64 | Docker Hub pull |
| Docker Desktop K8s on Apple Silicon | arm64 | Docker Hub pull (after multi-arch publish) or `build-local.sh` |
| Linux cloud cluster (typical) | amd64 | Docker Hub pull |

## Configuration

### Secret

Kustomize generates `workout-api-secret` with a dev-only key. Change it in `kustomization.yaml`:

```yaml
secretGenerator:
  - name: workout-api-secret
    literals:
      - AUTH_SECRET_KEY=your-strong-secret-here
```

For a standalone secret file, see `examples/secret.yaml`.

### ConfigMap

Non-sensitive API settings live in `configmap.yaml`:

- `AUTH_ALGORITHM`: `HS256`
- `DATABASE_URL`: `sqlite:////data/workout_app.db` (backed by the PVC)

### Frontend API URL

The published web image is built with `NEXT_PUBLIC_API_URL=http://localhost:8000`. Services are exposed as LoadBalancers on ports 3000 and 8000, which Docker Desktop maps to `localhost` — matching what the browser expects.

## Scripts

| Script | Purpose |
|--------|---------|
| `./k8s/deploy.sh` | Build local images on arm64 if needed, apply manifests, wait for rollouts |
| `./k8s/build-local.sh` | Build `workout-api` and `workout-web` images for the local architecture |
| `./k8s/teardown.sh` | Delete all resources in the `workout` namespace |

## Teardown

```bash
./k8s/teardown.sh
```

Or:

```bash
kubectl delete -k k8s/
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `no matching manifest for linux/arm64` | Hub image is amd64-only | Run `./k8s/build-local.sh`, then restart deployments |
| `namespace "workout" not found` | Used `kubectl apply -f` | `kubectl delete -k k8s/` then `kubectl apply -k k8s/` |
| `Kustomization` kind not found | Applied `kustomization.yaml` with `-f` | Use `kubectl apply -k k8s/` |
| Pod `ImagePullBackOff` | Wrong tag, private repo, or arch mismatch | `kubectl describe pod -n workout -l app.kubernetes.io/name=workout-api` |
| Frontend can't reach API | API not ready or wrong port | Check `kubectl get svc -n workout`; API should be on `:8000` |

Useful commands:

```bash
kubectl get pods,svc -n workout
kubectl describe pod -n workout -l app.kubernetes.io/name=workout-api
kubectl logs -n workout deployment/workout-api
kubectl logs -n workout deployment/workout-web
```

## Private Docker Hub images

If your repositories are private, create a pull secret and add it to both deployments:

```bash
kubectl create secret docker-registry dockerhub-creds \
  --docker-username=YOUR_USER \
  --docker-password=YOUR_TOKEN \
  -n workout
```

Then add to `api-deployment.yaml` and `web-deployment.yaml` under `spec.template.spec`:

```yaml
imagePullSecrets:
  - name: dockerhub-creds
```
