#!/bin/sh
VM_IP=$(ip addr show eth0 | grep 'inet ' | head -1 | awk '{print $2}' | cut -d/ -f1)
printf '[InternetShortcut]\nURL=http://%s/\n' "$VM_IP" > /var/lib/proxy/weblink/Webinterface.url
echo "Webinterface.url: http://$VM_IP/"
