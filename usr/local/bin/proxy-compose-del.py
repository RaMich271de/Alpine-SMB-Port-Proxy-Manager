#!/usr/bin/env python3
# proxy-compose-del.py SVC  (SVC = letztes Oktet der Proxy-IP, z.B. 124)
import sys, re

svc = sys.argv[1]
compose_file = "/var/lib/proxy/docker-compose.yml"

txt = open(compose_file).read()

# Service-Block entfernen: "  proxy-SVC:\n" + alle Zeilen mit groesserer Einrueckung
pattern = r'\n  proxy-' + re.escape(svc) + r':\n(?:(?:    |\t)[^\n]*\n)*'
new_txt = re.sub(pattern, '\n', txt)

if new_txt == txt:
    print(f"FEHLER: proxy-{svc} nicht gefunden", flush=True)
    sys.exit(1)

open(compose_file, "w").write(new_txt)
print(f"proxy-{svc} entfernt", flush=True)
