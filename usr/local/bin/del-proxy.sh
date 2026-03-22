#!/bin/sh
VM_IP="$1"
COMPOSE="/var/lib/proxy/docker-compose.yml"
LLMNR_STATIC="/var/lib/proxy/llmnr-static.conf"

if [ -z "$VM_IP" ]; then
    echo "FEHLER: VM_IP erforderlich"
    exit 1
fi

SVC=$(echo "$VM_IP" | cut -d. -f4)

if ! grep -q "ipv4_address: $VM_IP" "$COMPOSE" 2>/dev/null; then
    echo "FEHLER: $VM_IP nicht in docker-compose.yml gefunden"
    exit 1
fi

PROXY_NAME=$(python3 /usr/local/bin/proxy-compose-getname.py "$SVC")

echo "Entferne: proxy-$SVC ($VM_IP)"

docker compose -f "$COMPOSE" rm -sf "proxy-$SVC" 2>&1

python3 /usr/local/bin/proxy-compose-del.py "$SVC"
if [ $? -ne 0 ]; then
    echo "FEHLER: Konnte nicht aus docker-compose.yml entfernen"
    exit 1
fi

if [ -n "$PROXY_NAME" ]; then
    NAME_LOWER=$(echo "$PROXY_NAME" | tr '[:upper:]' '[:lower:]')
    sed -i "/^${NAME_LOWER}:/d" "$LLMNR_STATIC"
    rc-service llmnr-responder restart >/dev/null 2>&1
fi

echo "ERFOLG: $VM_IP (proxy-$SVC) entfernt"
