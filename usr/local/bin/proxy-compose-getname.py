#!/usr/bin/env python3
# proxy-compose-getname.py SVC
import sys, re

svc = sys.argv[1]
compose_file = "/var/lib/proxy/docker-compose.yml"

txt = open(compose_file).read()

# Block fuer diesen Service finden
m = re.search(
    r'  proxy-' + re.escape(svc) + r':\n((?:(?:    |\t)[^\n]*\n)*)',
    txt
)
if not m:
    print("", flush=True)
    sys.exit(0)

block = m.group(1)
n = re.search(r'PROXY_NAME:\s*["\']?([^\s"\'#\n]+)', block)
print(n.group(1).strip("\"'") if n else "", flush=True)
