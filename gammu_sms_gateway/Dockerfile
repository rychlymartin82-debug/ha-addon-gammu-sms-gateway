FROM alpine:3.19

# Instalace gammu, pythonu a nástrojů
RUN apk add --no-cache \
    gammu \
    gammu-smsd \
    python3 \
    py3-pip \
    jq \
    sqlite \
    iputils \
    bash

# Instalace Python knihoven
RUN pip3 install --no-cache-dir requests

# Vytvoření pracovního adresáře
WORKDIR /app

# Zkopírování skriptů addonu
COPY run.sh /app/run.sh
COPY parser.py /app/parser.py
COPY watchdog.py /app/watchdog.py
COPY smsd_template.conf /app/smsd_template.conf

# Oprávnění
RUN chmod +x /app/run.sh

# Start addonu
CMD ["/app/run.sh"]
