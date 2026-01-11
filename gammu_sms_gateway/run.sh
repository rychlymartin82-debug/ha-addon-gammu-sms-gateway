#!/usr/bin/env bash
set -e

echo "[GAMMU SMS GATEWAY] Starting..."

# Načtení konfigurace z HA options
OPTIONS_FILE=/data/options.json

DEVICE=$(jq -r '.device' $OPTIONS_FILE)
PRIMARY_NUMBER=$(jq -r '.primary_number' $OPTIONS_FILE)
RESTART_COMMAND=$(jq -r '.restart_command' $OPTIONS_FILE)
REBOOT_COMMAND=$(jq -r '.reboot_command' $OPTIONS_FILE)
WATCHDOG_INTERVAL=$(jq -r '.watchdog_interval' $OPTIONS_FILE)
PING_HOST=$(jq -r '.ping_host' $OPTIONS_FILE)

echo "[GAMMU SMS GATEWAY] Using device: $DEVICE"

# Instalace gammu a sqlite (jen jednou – na base image Alpine)
echo "[GAMMU SMS GATEWAY] Installing gammu..."
apk add --no-cache gammu gammu-smsd sqlite jq iputils python3 py3-pip || true
pip3 install --no-cache-dir requests

# Vytvoření /data pokud neexistuje
mkdir -p /data

# Vygenerování smsd.conf
sed "s|__DEVICE__|$DEVICE|g" /gammu_sms_gateway/smsd_template.conf > /data/smsd.conf

echo "[GAMMU SMS GATEWAY] Generated /data/smsd.conf:"
cat /data/smsd.conf

# Zkopírování parseru a watchdogu do /data (aby runonreceive fungoval)
cp /gammu_sms_gateway/parser.py /data/parser.py
cp /gammu_sms_gateway/watchdog.py /data/watchdog.py

# Spuštění watchdogu na pozadí
echo "[GAMMU SMS GATEWAY] Starting watchdog..."
python3 /data/watchdog.py "$WATCHDOG_INTERVAL" "$PING_HOST" "$PRIMARY_NUMBER" &

# Spuštění gammu-smsd (foreground)
echo "[GAMMU SMS GATEWAY] Starting gammu-smsd..."
exec gammu-smsd -c /data/smsd.conf -n sms-gateway -f
