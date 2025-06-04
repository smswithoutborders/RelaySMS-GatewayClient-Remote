FROM python:3.13.3-slim

WORKDIR /remote_gateway_client

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    apache2 \
    apache2-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

COPY . .

CMD gunicorn -w 4 -b 0.0.0.0:${HTTPS_PORT} \
    --log-level=info --access-logfile=- \
    --certfile=${SSL_CERTIFICATE_FILE} \
    --keyfile=${SSL_CERTIFICATE_KEY_FILE} \
    --threads 15 --timeout 30 app:app
