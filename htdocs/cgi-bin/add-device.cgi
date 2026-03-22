#!/bin/sh
echo "Content-Type: text/plain"
echo ""

read POST_DATA

DEVICE_IP=$(echo "$POST_DATA" | sed -n 's/.*device_ip=\([^&]*\).*/\1/p' | sed 's/%2E/./g')
DEVICE_PORT=$(echo "$POST_DATA" | sed -n 's/.*device_port=\([^&]*\).*/\1/p')
VM_IP=$(echo "$POST_DATA" | sed -n 's/.*vm_ip=\([^&]*\).*/\1/p' | sed 's/%2E/./g')

if [ -z "$DEVICE_IP" ] || [ -z "$DEVICE_PORT" ] || [ -z "$VM_IP" ]; then
    echo "FEHLER: Parameter fehlen!"
    exit 1
fi

sudo /usr/local/bin/add-proxy.sh "$DEVICE_IP" "$DEVICE_PORT" "$VM_IP"
