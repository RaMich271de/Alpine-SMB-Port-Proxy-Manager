#!/usr/bin/env python3
# proxy-list-devices.py - liest docker-compose.yml und docker ps
import subprocess, re

COMPOSE = "/var/lib/proxy/docker-compose.yml"

txt = open(COMPOSE).read()

# Laufende Container
try:
    ps = subprocess.check_output(
        ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
        stderr=subprocess.DEVNULL
    ).decode()
    running = {}
    for line in ps.strip().split("\n"):
        if "\t" in line:
            name, status = line.split("\t", 1)
            running[name] = status
except:
    running = {}

# Jeden Service-Block einzeln parsen
# Ein Block beginnt mit "  svcname:" (2 Leerzeichen) und endet beim naechsten
blocks = re.split(r'\n(?=  \S)', txt)

services = []
for block in blocks:
    # Nur Bloecke mit proxy-agent Image
    if "image: proxy-agent" not in block:
        continue
    def g(key):
        m = re.search(r'\b' + key + r':\s*["\']?([^\s"\'#\n]+)', block)
        return m.group(1).strip("\"'") if m else ""
    cname    = g("container_name")
    dev_ip   = g("DEVICE_IP")
    dev_port = g("DEVICE_PORT")
    pname    = g("PROXY_NAME")
    proxy_ip = g("ipv4_address")
    if cname and proxy_ip:
        services.append((cname, dev_ip, dev_port, pname, proxy_ip))

for cname, dev_ip, dev_port, pname, proxy_ip in services:
    if cname in running:
        status = "<span class='status-active'>&#10003; Aktiv</span>"
    else:
        status = "<span class='status-inactive'>&#10007; Inaktiv</span>"
    print(
        f"<tr>"
        f"<td>{proxy_ip}</td>"
        f"<td>{dev_ip}</td>"
        f"<td>{dev_port}</td>"
        f"<td>{pname}</td>"
        f"<td>{cname}</td>"
        f"<td>{status}</td>"
        f"<td><button class='delete-btn' "
        f"onclick='deleteDevice(\"{proxy_ip}\")'>L&ouml;schen</button></td>"
        f"</tr>"
    )

if not services:
    print("<tr><td colspan='7'>Keine Weiterleitungen konfiguriert</td></tr>")
