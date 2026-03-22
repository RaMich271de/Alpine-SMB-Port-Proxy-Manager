#!/bin/sh
echo "Content-Type: application/json"
echo ""

OCCUPIED=$(sudo /usr/local/bin/arp-scan-wrapper.sh)

COUNT=0
FIRST=1
JSON_IPS=""

for IP in $OCCUPIED; do
    COUNT=$((COUNT + 1))
    if [ $FIRST -eq 1 ]; then
        FIRST=0
        JSON_IPS="    \"$IP\""
    else
        JSON_IPS="$JSON_IPS,\n    \"$IP\""
    fi
done

echo "{"
echo "  \"occupied\": ["
if [ $COUNT -gt 0 ]; then
    printf "%b\n" "$JSON_IPS"
fi
echo "  ],"
echo "  \"timestamp\": \"$(date '+%Y-%m-%d %H:%M:%S')\","
echo "  \"count\": $COUNT"
echo "}"
