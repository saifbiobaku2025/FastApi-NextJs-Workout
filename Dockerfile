FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/fastapi

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN opentelemetry-bootstrap -a install

COPY fastapi/ ./fastapi/

WORKDIR /app/fastapi

EXPOSE 8000

CMD ["opentelemetry-instrument", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
