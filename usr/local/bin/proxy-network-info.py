#!/usr/bin/env python3
# proxy-network-info.py - liefert TAB-getrennte Proxy-Infos aus docker-compose.yml
# Ausgabe: PROXY_IP\tTARGET_IP\tTARGET_PORT\tPROXY_NAME
import re

COMPOSE = "/var/lib/proxy/docker-compose.yml"
try:
    txt = open(COMPOSE).read()
except:
    exit(0)

blocks = re.split(r'\n(?=  \S)', txt)
for block in blocks:
    if "image: proxy-agent" not in block:
        continue
    def g(key):
        m = re.search(r'\b' + key + r':\s*["\']?([^\s"\'#\n]+)', block)
        return m.group(1).strip("\"'") if m else ""
    proxy_ip  = g("ipv4_address")
    target_ip = g("DEVICE_IP")
    target_port = g("DEVICE_PORT")
    proxy_name  = g("PROXY_NAME")
    if proxy_ip:
        print(f"{proxy_ip}\t{target_ip}\t{target_port}\t{proxy_name}")
