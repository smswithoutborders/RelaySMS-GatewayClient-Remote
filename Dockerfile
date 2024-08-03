FROM python:3.12

RUN apt-get update && \ 
    apt-get install -y \
    build-essential \
    apache2 \
    apache2-dev \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /

COPY . .

RUN pip install -U pip && \
    pip install --no-cache-dir wheel && \
    pip install --no-cache-dir -r requirements.txt 

CMD mod_wsgi-express start-server wsgi.py \
    --user www-data \
    --group www-data \
    --port '${PORT}' \
    --https-port '${HTTPS_PORT}' \
    --server-name '${SERVER_NAME}'\
    --ssl-certificate-file '${SSL_CERTIFICATE_FILE}' \
    --ssl-certificate-key-file '${SSL_CERTIFICATE_KEY_FILE}' \
    --ssl-certificate-chain-file '${SSL_CERTIFICATE_CHAIN_FILE}' \
    --https-only \
    --log-to-terminal
