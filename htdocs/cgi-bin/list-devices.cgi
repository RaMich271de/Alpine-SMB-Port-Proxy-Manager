#!/bin/sh
echo "Content-Type: text/html"
echo ""

COMPOSE="/var/lib/proxy/docker-compose.yml"

cat << 'EOH'
<html><head><style>
table { border-collapse: collapse; width: 100%; }
th, td { padding: 8px; text-align: left; border: 1px solid #ddd; }
th { background: #0066cc; color: white; }
tr:hover { background: #f5f5f5; }
.status-active { color: green; font-weight: bold; }
.status-inactive { color: red; font-weight: bold; }
.delete-btn { background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; }
</style></head><body>
<table>
<tr><th>Proxy-IP</th><th>Ziel-Geraet</th><th>Port</th><th>Name</th><th>Container</th><th>Status</th><th>Aktion</th></tr>
EOH

if [ ! -f "$COMPOSE" ]; then
    echo "<tr><td colspan='7'>Keine Weiterleitungen konfiguriert</td></tr>"
else
    python3 /usr/local/bin/proxy-list-devices.py
fi

echo "</table>"
echo "<p style='margin-top: 20px; color: #666; font-size: 12px;'>Letzte Aktualisierung: $(date '+%Y-%m-%d %H:%M:%S')</p>"

cat << 'JS'
<script>
function deleteDevice(vmIp) {
    if (!confirm('Weiterleitung für ' + vmIp + ' wirklich entfernen?')) return;
    fetch('/cgi-bin/delete-device.cgi', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'vm_ip=' + encodeURIComponent(vmIp)
    }).then(r => r.text()).then(data => {
        if (data.includes('ERFOLG')) {
            location.reload();
        } else {
            alert('Fehler: ' + data);
        }
    }).catch(err => alert('Fehler: ' + err));
}
</script>
JS

echo "</body></html>"
