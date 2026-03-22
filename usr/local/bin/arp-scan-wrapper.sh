#!/bin/sh
# Nur IP-Zeilen ausgeben - keine Header/Footer von arp-scan
/usr/bin/arp-scan --interface=eth0 --localnet --quiet 2>/dev/null | \
    grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+'
