#!/bin/sh
DEVICE_IP="$1"
DEVICE_PORT="$2"
VM_IP="$3"
COMPOSE="/var/lib/proxy/docker-compose.yml"
LLMNR_STATIC="/var/lib/proxy/llmnr-static.conf"

if [ -z "$DEVICE_IP" ] || [ -z "$DEVICE_PORT" ] || [ -z "$VM_IP" ]; then
    echo "FEHLER: DEVICE_IP DEVICE_PORT VM_IP erforderlich"
    exit 1
fi

# Proxy-Name aus nslookup ableiten
HOSTNAME_RAW=$(nslookup "$DEVICE_IP" 2>/dev/null | grep 'name =' | head -1 | awk '{print $4}' | sed 's/\.$//')
if [ -z "$HOSTNAME_RAW" ]; then
    LAST=$(echo "$DEVICE_IP" | cut -d. -f4)
    PROXY_NAME="dev${LAST}-proxy"
else
    SHORT=$(echo "${HOSTNAME_RAW%%.*}" | cut -c1-8)
    PROXY_NAME="${SHORT}-proxy"
fi

# Service-Name = letztes Oktet der Proxy-IP (eindeutig, kurz)
SVC=$(echo "$VM_IP" | cut -d. -f4)
UUID=$(cat /proc/sys/kernel/random/uuid)

echo "Lege an: $PROXY_NAME ($VM_IP -> $DEVICE_IP:$DEVICE_PORT)"

python3 /usr/local/bin/proxy-compose-add.py "$SVC" "$DEVICE_IP" "$DEVICE_PORT" "$VM_IP" "$PROXY_NAME" "$UUID"
if [ $? -ne 0 ]; then exit 1; fi

docker compose -f "$COMPOSE" up -d "proxy-$SVC" 2>&1
if [ $? -ne 0 ]; then
    echo "FEHLER: docker compose up fehlgeschlagen"
    exit 1
fi

NAME_LOWER=$(echo "$PROXY_NAME" | tr '[:upper:]' '[:lower:]')
grep -q "^${NAME_LOWER}:" "$LLMNR_STATIC" 2>/dev/null || \
    echo "${NAME_LOWER}:${VM_IP}" >> "$LLMNR_STATIC"
rc-service llmnr-responder restart >/dev/null 2>&1

echo "ERFOLG: $VM_IP -> $DEVICE_IP:$DEVICE_PORT ($PROXY_NAME)"
