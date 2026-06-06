# Observability (logging, tracing, dashboards)

Local self-hosted observability for the workout API using **OpenTelemetry** and the **Grafana LGTM** stack (`grafana/otel-lgtm`).

| Signal | How it's collected | Where to view it |
|--------|-------------------|------------------|
| **Logs** | Python `logging` + OTLP export | Grafana → Explore → **Loki** |
| **Traces** | OpenTelemetry auto-instrumentation (FastAPI) | Grafana → Explore → **Tempo** |
| **Metrics** | OTel HTTP metrics (auto) | Grafana → Explore → **Prometheus** |

Logs and traces are correlated via `trace_id` — click a log line in Loki to jump to the matching trace in Tempo.

## Architecture

```
workout-api  ──OTLP (gRPC :4317)──►  grafana/otel-lgtm
                                         ├── OpenTelemetry Collector
                                         ├── Tempo   (traces)
                                         ├── Loki    (logs)
                                         └── Grafana (UI :3010)
```

## Quick start

From the repo root:

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Frontend | http://localhost:3000 |
| **Grafana** | http://localhost:3010 (login: `admin` / `admin`) |

Generate traffic:

```bash
curl http://localhost:8000/
```

Wait ~30s after first start for LGTM to finish booting, then open Grafana.

## Viewing traces

1. Open http://localhost:3010
2. **Explore** (left sidebar) → datasource **Tempo**
3. Query type: **Search**
4. Filter: `service.name = workout-api`
5. Run query → click a trace to see spans per HTTP request

## Viewing logs

1. **Explore** → datasource **Loki**
2. Set query type to **Label browser** (or enter a query directly)
3. Pick label `service_name` → value `workout-api` (labels appear after the API has logged at least once)
4. Example query:

   ```logql
   {service_name="workout-api"}
   ```

   If the label browser is empty, generate traffic first (`curl http://localhost:8000/`), wait a few seconds, then refresh labels.

5. Click a log line → **View trace** (if `trace_id` is present) to correlate with Tempo

## Viewing access logs

The API logs one line per request (`api.access` logger) with method, path, status, and duration. These appear in both:

- `docker compose logs api` (stdout)
- Grafana Loki (via OTLP)

## Environment variables

Set on the `api` service in [`docker-compose.yml`](../docker-compose.yml):

| Variable | Default (Compose) | Purpose |
|----------|-------------------|---------|
| `OTEL_SERVICE_NAME` | `workout-api` | Service name in traces/logs |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://otel-lgtm:4317` | OTLP collector address |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `grpc` | OTLP transport |
| `OTEL_TRACES_EXPORTER` | `otlp` | Export traces to collector |
| `OTEL_LOGS_EXPORTER` | `otlp` | Export logs to Loki via collector |
| `OTEL_METRICS_EXPORTER` | `otlp` | Export HTTP metrics |
| `OTEL_PYTHON_LOG_CORRELATION` | `true` | Inject `trace_id` into log records |
| `OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED` | `true` | Bridge stdlib `logging` to OTLP → Loki |
| `LOG_LEVEL` | `INFO` | Python log level |

### Disable OpenTelemetry (local dev without LGTM)

Run the API without exporting telemetry:

```bash
OTEL_SDK_DISABLED=true fastapi run api/main.py --host localhost
```

Or in Compose, set `OTEL_SDK_DISABLED=true` on the `api` service. Logs still go to stdout.

## Local development (API only, no Docker)

```bash
pip install -r requirements.txt
opentelemetry-bootstrap -a install

# Terminal 1 — start LGTM
docker run --rm -p 3010:3000 -p 4317:4317 -p 4318:4318 grafana/otel-lgtm

# Terminal 2 — run instrumented API
cd fastapi
export OTEL_SERVICE_NAME=workout-api
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_TRACES_EXPORTER=otlp
export OTEL_LOGS_EXPORTER=otlp
export OTEL_PYTHON_LOG_CORRELATION=true
opentelemetry-instrument fastapi run api/main.py --host localhost
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Grafana empty after start | Wait 30–60s for `otel-lgtm` to finish booting |
| No traces in Tempo | Confirm `api` has `depends_on: otel-lgtm` and OTEL env vars; check `docker compose logs api` for OTLP errors |
| Port 3010 in use | Change `"3010:3000"` in `docker-compose.yml` |
| Frontend port conflict | LGTM Grafana is on **3010**, not 3000 (frontend keeps 3000) |
| Logs in stdout but not Loki | Verify `OTEL_LOGS_EXPORTER=otlp`, `OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true`, and that `logging_config.py` uses `LoggingInstrumentor` (not `basicConfig(force=True)`, which strips the OTLP handler) |
| Loki label browser empty | Generate API traffic, wait ~5s, refresh; labels only appear after first log export |

## What is not covered (v1)

- Next.js browser/server tracing (API only)
- Kubernetes log shipping (use same OTEL env vars in K8s manifests as a follow-up)
- Production alerting or retention policies (`otel-lgtm` is for dev/demo)

## References

- [Grafana otel-lgtm docs](https://grafana.com/docs/opentelemetry/docker-lgtm/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)
