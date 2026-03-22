#!/bin/sh
echo "Content-Type: text/plain"
echo ""

read POST_DATA

MODE=$(echo "$POST_DATA"     | sed -n 's/.*mode=\([^&]*\).*/\1/p')
NEW_IP=$(echo "$POST_DATA"   | sed -n 's/.*ip=\([^&]*\).*/\1/p'      | sed 's/%2E/./g')
PREFIX=$(echo "$POST_DATA"   | sed -n 's/.*prefix=\([^&]*\).*/\1/p')
GATEWAY=$(echo "$POST_DATA"  | sed -n 's/.*gateway=\([^&]*\).*/\1/p' | sed 's/%2E/./g')

if [ -z "$MODE" ]; then
    echo "FEHLER: Parameter fehlen"
    exit 1
fi

if [ "$MODE" = "static" ]; then
    if [ -z "$NEW_IP" ] || [ -z "$PREFIX" ] || [ -z "$GATEWAY" ]; then
        echo "FEHLER: IP, Prefix und Gateway erforderlich"
        exit 1
    fi
    # Einfache IP-Validierung
    echo "$NEW_IP" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' || { echo "FEHLER: Ungueltige IP"; exit 1; }
    echo "$GATEWAY" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' || { echo "FEHLER: Ungueltige Gateway-IP"; exit 1; }
fi

sudo /usr/local/bin/apply-network-config.sh "$MODE" "$NEW_IP" "$PREFIX" "$GATEWAY"
