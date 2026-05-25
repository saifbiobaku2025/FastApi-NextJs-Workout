# FastApi-NextJs-Workout

FastAPI backend for the workout application.

## Local development

```bash
cd fastapi
fastapi run api/main.py --host localhost

cd nextjs
npm run dev


cd nextjs
npm test          # run once
npm run test:watch  # watch mode

```

## Run tests locally (90% pass threshold)

```bash
pip install -r requirements.txt
cd fastapi && pytest --junitxml=pytest-report.xml -v
cd .. && python .github/scripts/check_test_pass_rate.py fastapi/pytest-report.xml 0.90
```

## Docker Compose (local)

```bash
cp .env.example .env   # set AUTH_SECRET_KEY
docker compose up -d
curl http://localhost:8000/
```

## CI/CD: GitHub Actions → Docker Hub

Pushes to `main` build and publish `saifbiobaku/workout-api:latest` to Docker Hub,
replacing the previous `latest` tag on each successful run.

Pull requests to `main` run **Flake8** and **Pytest** (90% pass rate required) before merge.

### 1. Create a Docker Hub repository

1. Sign in at [Docker Hub](https://hub.docker.com/).
2. Go to **Repositories** → **Create Repository**.
3. Name: `workout-api`
4. Visibility: Public or Private.
5. Full image name: `saifbiobaku/workout-api`

> If the repository does not exist, Docker Hub creates it automatically on the first push.

### 2. Create a Docker Hub access token

1. Open [Docker Hub Security settings](https://hub.docker.com/settings/security).
2. Click **New Access Token**.
3. Description: `github-actions-workout-api`
4. Permissions: **Read & Write** (required to push images).
5. Copy the token immediately — it is shown only once.

Do **not** use your Docker Hub account password in GitHub Actions. Use an access token.

### 3. Add GitHub repository secrets

1. Open your GitHub repo → **Settings** → **Secrets and variables** → **Actions**.
2. Click **New repository secret** and add:

| Secret name | Value |
|-------------|-------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username (e.g. `saifbiobaku`) |
| `DOCKERHUB_TOKEN` | The access token from step 2 |

These secrets are used by `.github/workflows/docker-publish.yml`:

```yaml
- uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

### 4. Protect `main` (recommended)

In **Settings** → **Branches** → **Branch protection rules** for `main`:

- Require pull request reviews before merging
- Require status checks: **Flake8 / flake8**, **Pytest / pytest**
- Require branches to be up to date before merging

This ensures only code that passes lint and tests can merge and trigger a Docker publish.

### 5. How the publish workflow runs

| Event | Workflow | Result |
|-------|----------|--------|
| Pull request → `main` | Flake8, Pytest | Must pass to merge |
| Push to `main` (after merge) | Docker Publish | Builds and pushes `saifbiobaku/workout-api:latest` |

Monitor runs under **Actions** → **Docker Publish**.

### 6. Pull and run the published image

```bash
docker pull saifbiobaku/workout-api:latest

docker run -d \
  --name workout-api \
  -p 8000:8000 \
  -e AUTH_SECRET_KEY=your-secret \
  -e AUTH_ALGORITHM=HS256 \
  -e DATABASE_URL=sqlite:////data/workout_app.db \
  -v workout_data:/data \
  saifbiobaku/workout-api:latest
```

Or with Docker Compose (uses the published image):

```bash
docker compose pull
docker compose up -d
```

API docs: http://localhost:8000/docs

### Troubleshooting

| Issue | Fix |
|-------|-----|
| `denied: requested access to the resource is denied` | Check `DOCKERHUB_USERNAME` and that the token has **Read & Write** permission |
| `authentication required` | Verify `DOCKERHUB_TOKEN` is set and not expired |
| Workflow does not run | Confirm the push landed on `main`, not a feature branch |
| Image not updating locally | Run `docker pull saifbiobaku/workout-api:latest` to fetch the new `latest` |
