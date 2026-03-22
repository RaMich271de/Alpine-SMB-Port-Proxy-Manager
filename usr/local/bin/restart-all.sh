#!/bin/sh
# restart-all.sh - alle Proxy-Dienste neu starten

echo "=== Starte Dienste neu ==="

rc-service avahi-daemon restart
rc-service smbd restart 2>/dev/null || rc-service samba restart 2>/dev/null
rc-service llmnr-responder restart

# Container neu starten
cd /var/lib/proxy && docker compose restart
if [ $? -eq 0 ]; then
    COUNT=$(docker ps --filter "name=proxy-" --format "{{.Names}}" | wc -l)
    echo "ERFOLG: $COUNT Container laufen"
else
    echo "FEHLER: docker compose restart fehlgeschlagen"
    exit 1
fi
