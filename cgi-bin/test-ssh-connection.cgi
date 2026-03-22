#!/bin/sh
# Test SSH-Verbindung und VM-ID-Abgleich

echo "Content-Type: application/json"
echo ""

# Funktion: JSON-sichere Escape-Sequenzen für BusyBox
json_escape() {
    echo "$1" | tr -d '[:cntrl:]' | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e 's/\//\\\//g'
}

# Funktion: Einfache URL-Decodierung (für Werte ohne '+')
decode_url() {
    echo "$1" | sed -e 's/%20/ /g' -e 's/%21/!/g' -e 's/%22/"/g' -e 's/%23/#/g' -e 's/%24/$/g' \
                     -e 's/%25/%/g' -e 's/%26/&/g' -e "s/%27/'/g" -e 's/%28/(/g' -e 's/%29/)/g' \
                     -e 's/%2A/*/g' -e 's/%2B/+/g' -e 's/%2C/,/g' -e 's/%2D/-/g' -e 's/%2E/./g' \
                     -e 's/%2F/\//g' -e 's/%3A/:/g' -e 's/%3B/;/g' -e 's/%3D/=/g' -e 's/%3F/?/g' \
                     -e 's/%40/@/g' -e 's/%5B/[/g' -e 's/%5D/]/g' -e 's/%5C/\\/g'
}

# POST-Daten lesen (wenn CONTENT_LENGTH gesetzt ist)
if [ -n "$CONTENT_LENGTH" ]; then
    read -r POST_DATA
elif [ -n "$QUERY_STRING" ]; then
    POST_DATA="$QUERY_STRING"
else
    POST_DATA=""
fi

# Parameter extrahieren und dekodieren
HOST_IP=""
HOST_USER=""
HOST_PASS=""

IFS='&'
for pair in $POST_DATA; do
    key=$(echo "$pair" | cut -d'=' -f1)
    val=$(echo "$pair" | cut -d'=' -f2-)
    case "$key" in
        host_ip)   HOST_IP=$(decode_url "$val")   ;;
        host_user) HOST_USER=$(decode_url "$val") ;;
        host_pass) HOST_PASS=$(decode_url "$val") ;;
    esac
done
unset IFS

# Validierung der Parameter
if [ -z "$HOST_IP" ] || [ -z "$HOST_USER" ] || [ -z "$HOST_PASS" ]; then
    echo '{"status":"error","message":"Host-IP, Benutzer und Passwort erforderlich"}'
    exit 1
fi

# 1. Meine eigene VM-ID aus dem KVP-Pool lesen
if [ ! -r "/var/lib/hyperv/.kvp_pool_3" ]; then
    echo '{"status":"error","message":"KVP-System nicht verfügbar"}'
    exit 1
fi

MY_VMID=$(strings "/var/lib/hyperv/.kvp_pool_3" 2>/dev/null | awk '/^VirtualMachineId$/{getline; print $1; exit}')
MY_VMID_CLEAN=$(echo "$MY_VMID" | tr '[:upper:]' '[:lower:]' | tr -d '\r\n -')

if [ -z "$MY_VMID_CLEAN" ]; then
    echo '{"status":"error","message":"VM-ID konnte nicht aus KVP gelesen werden"}'
    exit 1
fi

# 2. SSH-Verbindung zum Host - Sichere Passwortübergabe mit File-Deskriptor
SSH_OUTPUT=""
SSH_ERROR=""
EXIT_CODE=1

# Temporäre Datei für das Passwort (sicherer als Here-Doc)
PASSFILE=$(mktemp)
chmod 600 "$PASSFILE"
printf '%s' "$HOST_PASS" > "$PASSFILE"

# SSH-Kommando mit sshpass - WICHTIG: known_hosts Problem umgehen
SSH_CMD="sshpass -f \"$PASSFILE\" ssh -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/dev/null \
          -o ConnectTimeout=10 \
          -o PasswordAuthentication=yes \
          -o PubkeyAuthentication=no \
          \"$HOST_USER@$HOST_IP\" \
          \"powershell.exe -Command \\\"(Get-VM -Name 'ProxyVM').Id.ToString()\\\"\""

SSH_OUTPUT=$(eval "$SSH_CMD" 2>&1)
EXIT_CODE=$?

# Aufräumen
rm -f "$PASSFILE"

# 3. SSH-Fehlerbehandlung
if [ $EXIT_CODE -ne 0 ]; then
    ERROR_MSG=$(echo "$SSH_OUTPUT" | head -1)
    ERROR_MSG_ESCAPED=$(json_escape "$ERROR_MSG")
    echo "{\"status\":\"error\",\"message\":\"SSH-Fehler: $ERROR_MSG_ESCAPED\"}"
    exit 1
fi

# 4. VM-ID aus der Host-Antwort extrahieren
HOST_VMID=$(echo "$SSH_OUTPUT" | grep -Eio '[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}' | head -1)
HOST_VMID_CLEAN=$(echo "$HOST_VMID" | tr '[:upper:]' '[:lower:]' | tr -d '\r\n -')

if [ -z "$HOST_VMID_CLEAN" ]; then
    RAW_OUTPUT_ESCAPED=$(json_escape "$SSH_OUTPUT")
    echo "{\"status\":\"error\",\"message\":\"VM-ID aus Host-Antwort nicht gefunden\",\"raw\":\"$RAW_OUTPUT_ESCAPED\"}"
    exit 1
fi

# 5. Vergleich der VM-IDs
if [ "$MY_VMID_CLEAN" = "$HOST_VMID_CLEAN" ]; then
    echo "{\"status\":\"ok\",\"message\":\"Host erfolgreich verifiziert\",\"vm_id\":\"$MY_VMID_CLEAN\",\"host_confirmed\":true}"
else
    echo "{\"status\":\"error\",\"message\":\"VM-ID-Missmatch\",\"local\":\"$MY_VMID_CLEAN\",\"remote\":\"$HOST_VMID_CLEAN\"}"
    exit 1
fi
