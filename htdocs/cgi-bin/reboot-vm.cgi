#!/bin/sh
echo "Content-Type: text/plain"
echo ""

# Warnung ausgeben
echo "⚠️ System wird neu gestartet..."
echo "Alpine VM fährt herunter und startet neu."
echo "Das Web-Interface ist ca. 30 Sekunden nicht erreichbar."
echo ""

# Reboot ausführen
sudo /usr/local/bin/reboot-vm.sh

echo "✓ Neustart-Befehl gesendet"
