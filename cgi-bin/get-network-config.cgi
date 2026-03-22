#!/bin/sh
echo "Content-Type: application/json"
echo ""

# Aktuellen Modus ermitteln
MODE=$(grep "iface eth0 inet" /etc/network/interfaces | awk '{print $4}')
if [ "$MODE" = "dhcp" ]; then
    echo "{\"mode\":\"dhcp\",\"ip\":\"\",\"prefix\":\"\",\"gateway\":\"\"}"
else
    IP=$(grep "address" /etc/network/interfaces | awk '{print $2}' | cut -d/ -f1)
    PREFIX=$(grep "address" /etc/network/interfaces | awk '{print $2}' | cut -d/ -f2)
    GW=$(grep "gateway" /etc/network/interfaces | awk '{print $2}')
    echo "{\"mode\":\"static\",\"ip\":\"$IP\",\"prefix\":\"$PREFIX\",\"gateway\":\"$GW\"}"
fi
