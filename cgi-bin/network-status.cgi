#!/bin/sh
echo "Content-Type: text/html"
echo ""

cat << 'STYLE'
<html><head><style>
body { font-family: Arial, sans-serif; margin: 0; padding: 10px; }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
th, td { padding: 10px 12px; text-align: left; border: 1px solid #ddd; }
th { background: #0066cc; color: white; font-size: 15px; }
tr:hover { background: #f5f5f5; }
.ip-gateway  { background: #fff3cd; font-weight: bold; }
.ip-vm-base  { background: #d4edda; font-weight: bold; }
.ip-vm-proxy { background: #cfe2ff; font-weight: bold; }
.ip-target   { background: #fff9e6; }
.ip-target-offline { background: #f8d7da; }
.ip-addr { font-family: monospace; font-size: 15px; font-weight: bold; }
.mac-addr { font-family: monospace; font-size: 12px; color: #666; }
.role { font-size: 13px; }
.summary { background: #f0f0f0; padding: 10px; margin-bottom: 15px;
           border-left: 4px solid #0066cc; font-size: 14px; }
</style></head><body>
STYLE

GATEWAY=$(ip route | grep default | awk '{print $3}')
VM_BASE=$(ip addr show eth0 | grep 'inet ' | head -1 | awk '{print $2}' | cut -d'/' -f1)

PROXY_INFO=$(python3 /usr/local/bin/proxy-network-info.py 2>/dev/null)
PROXY_IPS=$(echo "$PROXY_INFO" | awk -F'	' '{print $1}')
TARGET_IPS=$(echo "$PROXY_INFO" | awk -F'	' '{print $2}')

SCAN_RESULT=$(sudo /usr/local/bin/arp-scan-wrapper.sh | sort -t. -k4 -n | awk '!seen[$1]++')
TOTAL=$(echo "$SCAN_RESULT" | grep -c '[0-9]')

echo "<div class='summary'>"
echo "&#127760; <strong>Netzwerk-Scan:</strong> $TOTAL Geräte per ARP | Gateway: <strong>$GATEWAY</strong> | VM: <strong>$VM_BASE</strong>"
echo "</div>"

echo "<table>"
echo "<tr><th>IP-Adresse</th><th>MAC-Adresse</th><th>Hersteller</th><th>Rolle</th></tr>"

# Container-IPs aus docker-compose (immer anzeigen)
echo "$PROXY_INFO" | while IFS='	' read PROXY_IP TARGET_IP TARGET_PORT PROXY_NAME; do
    [ -z "$PROXY_IP" ] && continue
    ETH0_MAC=$(ip link show eth0 | grep ether | awk '{print $2}')
    echo "<tr class='ip-vm-proxy'>"
    echo "<td class='ip-addr'>$PROXY_IP</td>"
    echo "<td class='mac-addr'>$ETH0_MAC (Container)</td>"
    echo "<td>Docker macvlan</td>"
    echo "<td class='role'>&#128260; Proxy-Container: $PROXY_NAME &rarr; $TARGET_IP:$TARGET_PORT</td>"
    echo "</tr>"
done

# ARP-Scan Ergebnisse
echo "$SCAN_RESULT" | while IFS= read -r line; do
    IP=$(echo "$line" | awk '{print $1}')
    MAC=$(echo "$line" | awk '{print $2}')
    VENDOR=$(echo "$line" | cut -f3)
    [ -z "$IP" ] && continue

    CSS="" ; ROLE=""
    [ "$IP" = "$GATEWAY" ] && { CSS="ip-gateway"; ROLE="&#127760; Gateway (Router)"; }
    [ "$IP" = "$VM_BASE" ] && { CSS="ip-vm-base"; ROLE="&#128205; Diese VM (Webinterface)"; }

    echo "$PROXY_IPS" | grep -qF "$IP" && continue

    if echo "$TARGET_IPS" | grep -qF "$IP"; then
        CSS="ip-target"
        ROLE="&#128241; Ziel-Geraet (per ARP gefunden)"
    fi

    [ -z "$ROLE" ] && ROLE="&#128187; Netzwerkgeraet"

    echo "<tr class='$CSS'>"
    echo "<td class='ip-addr'>$IP</td>"
    echo "<td class='mac-addr'>$MAC</td>"
    echo "<td>$VENDOR</td>"
    echo "<td class='role'>$ROLE</td>"
    echo "</tr>"
done

# Zielgeraete die NICHT im ARP-Scan waren: per TCP pruefen
echo "$PROXY_INFO" | while IFS='	' read PROXY_IP TARGET_IP TARGET_PORT PROXY_NAME; do
    [ -z "$TARGET_IP" ] && continue
    echo "$SCAN_RESULT" | grep -qF "$TARGET_IP" && continue

    # TCP-Check
    if nc -z -w3 "$TARGET_IP" "$TARGET_PORT" 2>/dev/null; then
        CSS="ip-target"
        ROLE="&#128241; Ziel-Geraet (per TCP erreichbar, kein ARP)"
    else
        CSS="ip-target-offline"
        ROLE="&#128241; Ziel-Geraet (nicht erreichbar)"
    fi

    echo "<tr class='$CSS'>"
    echo "<td class='ip-addr'>$TARGET_IP</td>"
    echo "<td class='mac-addr'>-</td>"
    echo "<td>-</td>"
    echo "<td class='role'>$ROLE &rarr; $PROXY_NAME</td>"
    echo "</tr>"
done

echo "</table>"
echo "<p style='margin-top:15px; color:#888; font-size:12px;'>Letzte Aktualisierung: $(date '+%Y-%m-%d %H:%M:%S')</p>"
echo "</body></html>"
