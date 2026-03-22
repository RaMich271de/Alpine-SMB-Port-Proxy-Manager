#!/bin/sh
set -e

if [ -z "$DEVICE_IP" ] || [ -z "$DEVICE_PORT" ] || [ -z "$PROXY_NAME" ]; then
    echo "FEHLER: DEVICE_IP, DEVICE_PORT und PROXY_NAME muessen gesetzt sein"
    exit 1
fi

if [ -z "$UUID" ]; then
    UUID=$(cat /proc/sys/kernel/random/uuid)
fi

MY_IP=$(ip -4 addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1)

echo "=== Proxy-Agent ==="
echo "  Name:      $PROXY_NAME"
echo "  Ziel:      $DEVICE_IP:$DEVICE_PORT"
echo "  Proxy-IP:  $MY_IP"
echo "  UUID:      $UUID"

# Stale PID-Files bereinigen (wichtig nach Container-Neustart)
rm -f /run/dbus/dbus.pid /run/avahi-daemon/pid /run/avahi-daemon/socket

# dbus
mkdir -p /run/dbus
dbus-daemon --system --nofork &
sleep 1

# avahi config
mkdir -p /run/avahi-daemon /etc/avahi/services
cat > /etc/avahi/avahi-daemon.conf << 'AVAHICONF'
[server]
host-name-from-machine-id=no
use-ipv4=yes
use-ipv6=no
allow-interfaces=eth0
disallow-other-stacks=yes
enable-dbus=yes

[wide-area]
enable-wide-area=no

[publish]
disable-publishing=no
publish-addresses=yes
publish-hinfo=no
publish-workstation=no
publish-domain=yes

[reflector]
enable-reflector=no
AVAHICONF

# Avahi SMB Service-Datei
python3 -c "
import os
hn = os.environ.get('PROXY_NAME', 'proxy')
LT = chr(0x3c)
GT = chr(0x3e)
SL = '/'
xml  = LT + '?xml version=\"1.0\" standalone=\'no\'?' + GT + '\n'
xml += LT + '!DOCTYPE service-group SYSTEM \"avahi-service.dtd\"' + GT + '\n'
xml += LT + 'service-group' + GT + '\n'
xml += '  ' + LT + 'name replace-wildcards=\"yes\"' + GT + hn + LT + SL + 'name' + GT + '\n'
xml += '  ' + LT + 'service' + GT + '\n'
xml += '    ' + LT + 'type' + GT + '_smb._tcp' + LT + SL + 'type' + GT + '\n'
xml += '    ' + LT + 'port' + GT + '445' + LT + SL + 'port' + GT + '\n'
xml += '  ' + LT + SL + 'service' + GT + '\n'
xml += LT + SL + 'service-group' + GT + '\n'
open('/etc/avahi/services/smb.service', 'w').write(xml)
print('Avahi service: ' + hn)
"

avahi-daemon --no-drop-root --daemonize
echo "  avahi gestartet"

# socat
socat TCP-LISTEN:445,fork,reuseaddr "TCP:${DEVICE_IP}:${DEVICE_PORT}" &
echo "  socat gestartet (-> $DEVICE_IP:$DEVICE_PORT)"

echo "  wsdd startet..."
exec wsdd -i eth0 -n "$PROXY_NAME" -w WORKGROUP --uuid "$UUID" -4 --shortlog
