#!/bin/sh
# Startet wsdd fuer die VM selbst (.20 / Port-ProxyVM)
pkill -f "wsdd.*192.168.178.20" 2>/dev/null
rm -f /run/wsdd-eth0.pid
sleep 1
nohup /usr/bin/wsdd -i 192.168.178.20 -n Port-ProxyVM \
    -w WORKGROUP --uuid a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
    -4 --shortlog \
    < /dev/null > /var/log/wsdd-eth0.log 2>&1 &
echo $! > /run/wsdd-eth0.pid
sleep 2
if kill -0 $(cat /run/wsdd-eth0.pid) 2>/dev/null; then
    echo "wsdd-eth0 gestartet (PID $(cat /run/wsdd-eth0.pid))"
else
    echo "FEHLER: wsdd-eth0 konnte nicht gestartet werden"
fi
