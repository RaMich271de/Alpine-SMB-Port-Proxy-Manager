#!/bin/sh
echo "Content-Type: text/event-stream"
echo "Cache-Control: no-cache"
echo "X-Accel-Buffering: no"
echo ""

send() {
    printf "data: %s\n\n" "$1"
}

sudo /usr/local/bin/system-update.sh 2>&1 | while IFS= read -r line; do
    send "$line"
done

send ""
send "=== FERTIG ==="
