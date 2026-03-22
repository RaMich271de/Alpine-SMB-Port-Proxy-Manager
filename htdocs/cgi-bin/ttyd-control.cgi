#!/bin/sh
# ttyd-control.cgi - Startet/Stoppt ttyd auf allen Interfaces (ttyd 1.7.7)

echo "Content-Type: application/json"
echo ""

# Aktuelle VM-IP ermitteln (immer eth0, auch bei DHCP)
VM_IP=$(ip -4 addr show eth0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
[ -z "$VM_IP" ] && VM_IP="192.168.178.37"

# Parameter aus QUERY_STRING extrahieren
ACTION=$(echo "$QUERY_STRING" | sed 's/^[^=]*=//' | tr -d '&= ')

# Falls kein Parameter, default auf status
if [ -z "$ACTION" ]; then
    ACTION="status"
fi

case "$ACTION" in
    start)
        # Prüfen ob schon läuft
        if pgrep -f "ttyd.*7681" > /dev/null; then
            PID=$(pgrep -f "ttyd.*7681")
            echo "{\"status\":\"ok\",\"message\":\"ttyd läuft bereits\",\"pid\":$PID,\"vm_ip\":\"$VM_IP\"}"
        else
            # ttyd starten auf ALLEN Interfaces (0.0.0.0) mit Iframe-Unterstützung
            # -O: Deaktiviert Origin-Prüfung (für ttyd 1.7.7: -O bedeutet "Do not allow", aber in der Logik: -O setzt check-origin auf false)
            # --writable: Aktiviert Schreibmodus
            # /bin/sh -l: Startet Login-Shell
            nohup ttyd -p 7681 -i 0.0.0.0 --writable -t disableLeaveAlert=true -t fontSize=14 -w /root /bin/sh -l > /tmp/ttyd.log 2>&1 &
            sleep 2
            PID=$(pgrep -f "ttyd.*7681")
            if [ -n "$PID" ]; then
                echo "{\"status\":\"ok\",\"message\":\"ttyd gestartet\",\"pid\":$PID,\"vm_ip\":\"$VM_IP\"}"
            else
                echo "{\"status\":\"error\",\"message\":\"ttyd konnte nicht gestartet werden\",\"vm_ip\":\"$VM_IP\"}"
            fi
        fi
        ;;
    stop)
        PID=$(pgrep -f "ttyd.*7681")
        if [ -n "$PID" ]; then
            kill $PID 2>/dev/null
            sleep 1
            # Sicherheitshalber kill -9
            kill -9 $PID 2>/dev/null
            echo "{\"status\":\"ok\",\"message\":\"ttyd gestoppt\",\"pid\":$PID,\"vm_ip\":\"$VM_IP\"}"
        else
            echo "{\"status\":\"ok\",\"message\":\"ttyd läuft nicht\",\"vm_ip\":\"$VM_IP\"}"
        fi
        ;;
    status)
        PID=$(pgrep -f "ttyd.*7681")
        # Immer die AKTUELLE eth0 IP zurückgeben
        CURRENT_IP=$(ip -4 addr show eth0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
        [ -z "$CURRENT_IP" ] && CURRENT_IP="$VM_IP"
        
        if [ -n "$PID" ]; then
            echo "{\"status\":\"ok\",\"running\":true,\"pid\":$PID,\"vm_ip\":\"$CURRENT_IP\"}"
        else
            echo "{\"status\":\"ok\",\"running\":false,\"vm_ip\":\"$CURRENT_IP\"}"
        fi
        ;;
    *)
        echo "{\"status\":\"error\",\"message\":\"Ungültige Aktion (start|stop|status)\",\"vm_ip\":\"$VM_IP\"}"
        ;;
esac
