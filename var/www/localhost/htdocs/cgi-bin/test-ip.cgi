#!/bin/sh
echo "Content-Type: application/json"
echo ""
VM_IP=$(ip -4 addr show eth0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
if [ -z "$VM_IP" ]; then
    echo '{"status":"error","message":"Keine IP gefunden"}'
else
    echo "{\"status\":\"ok\",\"vm_ip\":\"$VM_IP\"}"
fi
