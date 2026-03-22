#!/bin/sh
# apply-network-config.sh MODE IP PREFIX GATEWAY
MODE="$1"
NEW_IP="$2"
PREFIX="$3"
GATEWAY="$4"

IFACE_FILE="/etc/network/interfaces"

# Backup
cp "$IFACE_FILE" "${IFACE_FILE}.bak"

if [ "$MODE" = "dhcp" ]; then
    cat > "$IFACE_FILE" << 'EOF'
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet dhcp
EOF
    echo "Konfiguration: DHCP"
else
    cat > "$IFACE_FILE" << EOF
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
address ${NEW_IP}/${PREFIX}
gateway ${GATEWAY}
EOF
    echo "Konfiguration: statisch $NEW_IP/$PREFIX gw $GATEWAY"
fi

# Webinterface.url und LLMNR sofort aktualisieren
# (mit neuer IP, auch wenn Netzwerk noch nicht umgeschaltet)
if [ "$MODE" = "static" ]; then
    printf '[InternetShortcut]\nURL=http://%s/\n' "$NEW_IP" \
        > /var/lib/proxy/weblink/Webinterface.url
    # llmnr-static.conf aktualisieren
    python3 -c "
import re
f = '/var/lib/proxy/llmnr-static.conf'
txt = open(f).read()
txt = re.sub(r'^port-proxyvm:.*$', 'port-proxyvm:$NEW_IP', txt, flags=re.MULTILINE)
txt = re.sub(r'^Port-ProxyVM:.*$', 'Port-ProxyVM:$NEW_IP', txt, flags=re.MULTILINE)
open(f,'w').write(txt)
print('llmnr-static.conf aktualisiert')
"
fi

# Netzwerk neu starten
ifdown eth0 2>/dev/null
ifup eth0 2>/dev/null

# Services die von der IP abhaengen neu starten
rc-service llmnr-responder restart 2>/dev/null
rc-service smbd restart 2>/dev/null
sh /usr/local/bin/start-wsdd-eth0.sh 2>/dev/null

echo "ERFOLG: Netzwerk neu konfiguriert. Bitte Browser neu laden."
echo "NEUE_IP: $NEW_IP"
