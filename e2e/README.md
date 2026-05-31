# Playwright E2E Tests

End-to-end tests for the workout app (Next.js frontend + FastAPI backend) using [Playwright](https://playwright.dev/) and JavaScript.

Tests run in a real browser against the full stack started via Docker Compose.

## Two ways to run

| Mode | Command | Best for |
|------|---------|----------|
| **Docker** (recommended for CI) | `./run-docker.sh` | No local Node/Playwright install; reproducible |
| **Host** | `npm test` | UI mode, debug, headed browser |

### Why two modes?

The browser must reach the API at a URL it can resolve:

- **Host mode** — browser on your machine uses `http://localhost:8000` (via `docker-compose.e2e.host.yml` override)
- **Docker mode** — browser inside the Playwright container uses `http://api:8000` (Docker network)

Test files are the same for both; only `baseURL` and the frontend build arg differ.

## Docker mode (fully containerized)

Requires Docker Desktop only:

```bash
cd e2e
./run-docker.sh
```

Or from the repo root:

```bash
docker compose -f docker-compose.e2e.yml --env-file .env.e2e \
  --profile e2e run --rm --build playwright
```

Reports are written to `e2e/playwright-report/` on your host via volume mounts.

## Host mode (interactive learning)

### Prerequisites

- Docker Desktop running
- Node.js 20+

### Install

```bash
cd e2e
npm ci
npx playwright install chromium
```

### Quick run

Playwright starts Docker Compose and waits for http://localhost:3000:

```bash
npm test
```

### UI mode (best for learning)

```bash
npm run test:ui
```

Pick a test, watch it step-by-step, inspect locators, and time-travel through actions.

### Headed mode (see the browser)

```bash
npm run test:headed
```

### Debug a failing test

```bash
npm run test:debug -- tests/auth.spec.js
```

### App already running

If Docker Compose is already up on ports 3000/8000, Playwright reuses it locally:

```bash
docker compose -f docker-compose.e2e.yml -f docker-compose.e2e.host.yml \
  --env-file .env.e2e up -d   # from repo root
cd e2e && npm test
```

### View HTML report

```bash
npm run report
```

## Test files

| File | Covers |
|------|--------|
| `tests/auth.spec.js` | Register, login, logout |
| `tests/workout.spec.js` | Create workout and routine |
| `fixtures/auth.js` | Shared register/login helpers |

## Clean up Docker

```bash
docker compose -f docker-compose.e2e.yml down -v
```

Use `-v` to remove the E2E SQLite volume for a fresh database.

## vs Jest unit tests

Jest tests in `nextjs/src/__tests__/` mock axios and render components in jsdom. Playwright E2E tests hit the real UI and API — closer to what a user experiences.

## Configuration

| File | Purpose |
|------|---------|
| `playwright.config.js` | base URL, host webServer, reporters |
| `Dockerfile` | Playwright runner image (Chromium preinstalled) |
| `../docker-compose.e2e.yml` | API, frontend, playwright services |
| `../docker-compose.e2e.host.yml` | Host-mode override (`localhost` API URL) |
| `../.env.e2e` | API auth env vars for E2E |
