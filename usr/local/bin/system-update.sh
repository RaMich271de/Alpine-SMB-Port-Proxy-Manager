#!/bin/sh
echo "=== System-Update gestartet: $(date) ==="
echo ""
echo "--- apk update ---"
apk update
echo ""
echo "--- apk upgrade ---"
apk upgrade
echo ""
echo "--- apk fix ---"
apk fix
echo ""
echo "--- apk cache clean ---"
apk cache clean
echo ""
echo "=== Update abgeschlossen: $(date) ==="
