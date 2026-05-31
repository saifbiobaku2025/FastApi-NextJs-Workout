# Workout App — Next.js Frontend

Next.js frontend for the workout application.

## Getting started

Install dependencies and start the dev server:

```bash
npm ci
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

The API must be running separately (see the root [README](../README.md)) — default API URL is `http://localhost:8000`.

## Running Jest tests

Tests live in `src/__tests__/` and use [Jest](https://jestjs.io/) with [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/).

### Run all tests once

```bash
cd nextjs
npm test
```

### Watch mode (re-runs on file changes)

```bash
npm run test:watch
```

### Run a single test file

```bash
npm test -- src/__tests__/login.test.js
```

### Run tests matching a name

```bash
npm test -- -t "renders login form"
```

### Coverage report

```bash
npm test -- --coverage
```

### CI-style run (JUnit report + non-interactive)

This matches what GitHub Actions runs on pull requests:

```bash
JEST_JUNIT_OUTPUT_FILE=jest-report.xml npm test -- --ci --reporters=default --reporters=jest-junit
```

Then enforce the 90% pass-rate gate from the repo root:

```bash
python ../.github/scripts/check_test_pass_rate.py jest-report.xml 0.90
```

## Test suites

| File | Covers |
|------|--------|
| `src/__tests__/login.test.js` | Login page |
| `src/__tests__/AuthContext.test.js` | Auth context provider |
| `src/__tests__/ProtectedRoute.test.js` | Route protection |
| `src/__tests__/page.test.js` | Home page |

Configuration: `jest.config.js`, setup: `jest.setup.js`.

## Other scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server |
| `npm run build` | Production build |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |

## Docker

The frontend image is built from `Dockerfile` and published as `saifbiobaku/workout-web:latest`. See the root [README](../README.md) and [k8s/README](../k8s/README.md) for deployment options.
