#!/bin/sh
# detect-host.cgi - Findet die IP des Hyper-V Hosts

echo "Content-Type: application/json"
echo ""

# Funktion: Kontext für eine IP ermitteln
get_ip_context() {
    local ip=$1
    
    # Loopback
    if [ "$ip" = "127.0.0.1" ]; then
        echo "die Maschine selbst - intern"
        return
    fi
    
    # Primäre IP
    primary_ip=$(ip addr show eth0 | grep "inet " | awk '{print $2}' | cut -d/ -f1 | head -1)
    if [ "$ip" = "$primary_ip" ]; then
        echo "die Maschine selbst - über Netzwerk"
        return
    fi
    
    # Weiterleitungen prüfen (aus proxy-forward Service)
    if [ -f /etc/init.d/proxy-forward ]; then
        # Suche nach socat-Zeilen mit dieser bind-IP
        forward_line=$(grep "bind=$ip" /etc/init.d/proxy-forward | head -1)
        if [ -n "$forward_line" ]; then
            # Extrahiere Ziel-IP:Port
            target=$(echo "$forward_line" | grep -oE 'TCP:[0-9.]+:[0-9]+' | sed 's/TCP://')
            target_ip=$(echo "$target" | cut -d: -f1)
            
            # DNS Reverse-Lookup (nur erste Zeile)
            hostname=$(nslookup "$target_ip" 2>/dev/null | grep "name =" | head -1 | awk '{print $NF}' | sed 's/\.$//')
            [ -z "$hostname" ] && hostname="unbekannt"
            
            echo "Weiterleitung von $target | $hostname"
            return
        fi
    fi
    
    # Sekundäre IPs
    if ip addr show | grep -q "$ip"; then
        echo "sekundäre IP dieser Maschine"
        return
    fi
    
    echo "unbekannt"
}

# Eigene IPs sammeln (als Array für JSON)
OWN_IPS_RAW=$(ip addr show | grep "inet " | awk '{print $2}' | cut -d/ -f1)

# Baue excluded_ips Array mit Kontext
excluded_ips_json="["
first=1
for ip in $OWN_IPS_RAW; do
    context=$(get_ip_context "$ip")
    # JSON-Escape für Anführungszeichen
    context_escaped=$(echo "$context" | sed 's/"/\\"/g')
    
    [ $first -eq 0 ] && excluded_ips_json="${excluded_ips_json},"
    excluded_ips_json="${excluded_ips_json}{\"ip\":\"$ip\",\"context\":\"$context_escaped\"}"
    first=0
done
excluded_ips_json="${excluded_ips_json}]"

# Komma-separierte Liste für Vergleich
OWN_IPS=$(echo "$OWN_IPS_RAW" | tr '\n' ',' | sed 's/,$//')

# Kandidaten aus ARP-Tabelle
CANDIDATES=$(arp -a | awk '{print $2}' | sed 's/[()]//g' | grep -E '^192\.168\.178\.[0-9]+$' | sort -u)

best_ip=""
best_time=999999
best_time_str=""
checked_count=0

for ip in $CANDIDATES; do
    # Skip eigene IPs
    echo "$OWN_IPS" | grep -q "$ip" && continue
    
    # Skip Broadcast
    [ "$ip" = "192.168.178.255" ] && continue
    
    checked_count=$((checked_count + 1))
    
    # Ping testen - avg-Wert extrahieren
    avg_time=$(ping -c 2 -W 1 $ip 2>/dev/null | tail -1 | grep "round-trip" | sed 's/.*= //' | cut -d'/' -f2)
    
    if [ -n "$avg_time" ]; then
        # Zu Integer konvertieren für Vergleich
        time_int=$(echo "$avg_time * 1000" | awk '{printf "%d", $1}')
        
        if [ $time_int -lt $best_time ]; then
            best_time=$time_int
            best_ip=$ip
            best_time_str="$avg_time"
        fi
    fi
done

# Host muss < 3ms haben
if [ -n "$best_ip" ] && [ $best_time -lt 3000 ]; then
    # MAC-Adresse
    mac=$(arp -a | grep "$best_ip" | awk '{print $4}')
    
    # Vendor von arp-scan
    vendor=""
    if command -v arp-scan >/dev/null 2>&1; then
        vendor=$(arp-scan -l 2>/dev/null | grep "$best_ip" | cut -f3)
    fi
    vendor_json=$(echo "$vendor" | sed 's/"/\\"/g')
    
    echo "{\"status\":\"ok\",\"host_ip\":\"$best_ip\",\"latency_ms\":\"$best_time_str\",\"mac\":\"$mac\",\"vendor\":\"$vendor_json\",\"excluded_ips\":$excluded_ips_json,\"checked_count\":$checked_count}"
else
    if [ $checked_count -eq 0 ]; then
        echo "{\"status\":\"error\",\"message\":\"Keine Kandidaten in ARP-Tabelle\",\"excluded_ips\":$excluded_ips_json}"
    else
        echo "{\"status\":\"error\",\"message\":\"Kein Host < 3ms (bester: $best_ip mit ${best_time_str}ms)\",\"excluded_ips\":$excluded_ips_json,\"checked_count\":$checked_count,\"best_candidate\":\"$best_ip\",\"best_latency\":\"$best_time_str\"}"
    fi
fi
