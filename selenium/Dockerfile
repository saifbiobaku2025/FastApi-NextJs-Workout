FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY conftest.py pytest.ini ./
COPY helpers/ ./helpers/
COPY tests/ ./tests/

ENV BASE_URL=http://frontend:3000
ENV SELENIUM_REMOTE_URL=http://selenium:4444/wd/hub

CMD ["pytest"]
