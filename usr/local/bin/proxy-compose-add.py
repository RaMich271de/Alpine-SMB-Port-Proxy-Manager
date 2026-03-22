#!/usr/bin/env python3
# proxy-compose-add.py SVC DEVICE_IP DEVICE_PORT VM_IP PROXY_NAME UUID
import sys

svc, dev_ip, dev_port, vm_ip, proxy_name, uuid = sys.argv[1:7]
compose_file = "/var/lib/proxy/docker-compose.yml"

txt = open(compose_file).read()

if f"  proxy-{svc}:" in txt:
    print(f"FEHLER: proxy-{svc} bereits konfiguriert!", flush=True)
    sys.exit(1)

block = f"""
  proxy-{svc}:
    image: proxy-agent
    container_name: proxy-{svc}
    hostname: {proxy_name}
    restart: always
    environment:
      DEVICE_IP: {dev_ip}
      DEVICE_PORT: "{dev_port}"
      PROXY_NAME: {proxy_name}
      UUID: {uuid}
    networks:
      lan:
        ipv4_address: {vm_ip}
"""

txt = txt.replace("\nnetworks:", block + "\nnetworks:", 1)
open(compose_file, "w").write(txt)
print(f"docker-compose.yml: proxy-{svc} hinzugefuegt", flush=True)
