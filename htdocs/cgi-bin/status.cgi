#!/bin/sh
echo "Content-Type: text/html"
echo ""

echo "<html><head><style>"
echo "body { font-family: Arial, sans-serif; background: #f9f9f9; padding: 10px; margin: 0; }"
echo "h4 { margin: 0 0 15px 0; color: #333; }"
echo "table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 13px; }"
echo "th, td { padding: 8px 12px; text-align: left; border: 1px solid #ddd; }"
echo "th { background: #0066cc; color: white; font-weight: bold; }"
echo "tr:hover { background: #f5f5f5; }"
echo ".mono { font-family: monospace; }"
echo ".highlight { background: #e8f4f8; font-weight: bold; padding: 10px; border-left: 3px solid #0066cc; margin: 10px 0; }"
echo ".row-vm   { background: #d4edda; }"
echo ".row-vpn  { background: #fff3cd; }"
echo ".row-info { background: #f8f9fa; color: #888; font-style: italic; }"
echo "</style></head><body>"

echo "<h4>VM System-Status</h4>"

# --- Netzwerk: nur relevante Interfaces ---
echo "<h4 style='margin-top: 5px;'>🌐 Netzwerk-Konfiguration</h4>"
echo "<table>"
echo "<tr><th>Interface</th><th>Status</th><th>IP</th><th>Bemerkung</th></tr>"

# eth0 – VM-Haupt-IP
VM_IP=$(ip addr show eth0 | grep 'inet ' | head -1 | awk '{print $2}' | cut -d'/' -f1)
ETH_STATE=$(ip link show eth0 | grep -oE "state [A-Z]+" | awk '{print $2}')
echo "<tr class='row-vm'><td class='mono'>eth0</td><td>$ETH_STATE</td><td class='mono'>$VM_IP</td><td>Primaere NIC – Webinterface</td></tr>"

# tailscale0 – falls vorhanden
TS_IP=$(ip addr show tailscale0 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d'/' -f1)
if [ -n "$TS_IP" ]; then
    echo "<tr class='row-vpn'><td class='mono'>tailscale0</td><td>UP</td><td class='mono'>$TS_IP</td><td>VPN-Tunnel (Tailscale)</td></tr>"
fi

echo "</table>"

# --- Docker Container als Proxy-Uebersicht ---
echo "<h4 style='margin-top: 15px;'>🐳 Proxy-Container</h4>"
echo "<table>"
echo "<tr><th>Container</th><th>Status</th><th>Proxy-IP</th><th>Ziel</th><th>Name</th></tr>"
docker ps -a --format "{{.Names}}\t{{.Status}}" 2>/dev/null | grep '^proxy-' | while IFS="	" read CNAME CSTATUS; do
    PROXY_IP=$(docker inspect "$CNAME" --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 2>/dev/null)
    ENV_DEVICE=$(docker inspect "$CNAME" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | grep DEVICE_IP | cut -d= -f2)
    ENV_PORT=$(docker inspect "$CNAME" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | grep DEVICE_PORT | cut -d= -f2 | tr -d '"')
    ENV_NAME=$(docker inspect "$CNAME" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | grep PROXY_NAME | cut -d= -f2)
    if echo "$CSTATUS" | grep -q "^Up"; then
        BADGE="<span style='color:green;font-weight:bold'>&#10003; Aktiv</span>"
    else
        BADGE="<span style='color:red;font-weight:bold'>&#10007; Gestoppt</span>"
    fi
    echo "<tr><td class='mono'>$CNAME</td><td>$BADGE</td><td class='mono'>$PROXY_IP</td><td class='mono'>$ENV_DEVICE:$ENV_PORT</td><td>$ENV_NAME</td></tr>"
done

CONTAINER_COUNT=$(docker ps --filter "name=proxy-" --format "{{.Names}}" 2>/dev/null | wc -l)
echo "</table>"
echo "<div class='highlight'>📱 <strong>Aktive Proxy-Container:</strong> $CONTAINER_COUNT laufen</div>"

# --- System ---
echo "<h4 style='margin-top: 20px;'>ℹ️ System-Informationen</h4>"
echo "<table>"
echo "<tr><th>Eigenschaft</th><th>Wert</th></tr>"
echo "<tr><td>Hostname</td><td class='mono'>$(hostname)</td></tr>"
echo "<tr><td>Uptime</td><td>$(uptime | cut -d',' -f1 | sed 's/^.*up //')</td></tr>"
echo "<tr><td>Load Average</td><td class='mono'>$(uptime | awk -F'load average:' '{print $2}')</td></tr>"
echo "<tr><td>Docker</td><td class='mono'>$(docker version --format '{{.Server.Version}}' 2>/dev/null)</td></tr>"
echo "</table>"

echo "<h4 style='margin-top: 20px;'>💾 Arbeitsspeicher</h4>"
echo "<table>"
echo "<tr><th>Gesamt</th><th>Belegt</th><th>Frei</th><th>Cache</th></tr>"
free -h | grep Mem | awk '{printf "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n", $2, $3, $4, $6}'
echo "</table>"

echo "<h4 style='margin-top: 20px;'>💿 Festplatte</h4>"
echo "<table>"
echo "<tr><th>Partition</th><th>Gesamt</th><th>Belegt</th><th>Frei</th><th>Belegt %</th></tr>"
df -h / | tail -1 | awk '{printf "<tr><td class=\"mono\">%s</td><td>%s</td><td>%s</td><td>%s</td><td><strong>%s</strong></td></tr>\n", $1, $2, $3, $4, $5}'
echo "</table>"

echo "</body></html>"
