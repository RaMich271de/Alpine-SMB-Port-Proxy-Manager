#!/bin/sh
echo "Content-Type: text/plain"
echo ""
read POST_DATA
VM_IP=$(echo "$POST_DATA" | sed -n 's/.*vm_ip=\([^&]*\).*/\1/p' | sed 's/%2E/./g')
if [ -z "$VM_IP" ]; then
    echo "FEHLER: Keine VM_IP angegeben!"
    exit 1
fi
sudo /usr/local/bin/del-proxy.sh "$VM_IP"
