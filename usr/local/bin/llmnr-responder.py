import socket, struct, signal, sys, time, re

LLMNR_PORT   = 5355
LLMNR_MCAST  = "224.0.0.252"
CONF_STATIC  = "/var/lib/proxy/llmnr-static.conf"
CONF_COMPOSE = "/var/lib/proxy/docker-compose.yml"

def load_names():
    names = {}
    try:
        for line in open(CONF_STATIC):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(":", 1)
            if len(parts) == 2:
                names[parts[0].lower().strip()] = parts[1].strip()
    except Exception as e:
        print(f"Static config error: {e}", flush=True)
    try:
        txt = open(CONF_COMPOSE).read()
        blocks = re.split(r'\n(?=  \S)', txt)
        for block in blocks:
            if "image: proxy-agent" not in block:
                continue
            m_ip   = re.search(r'ipv4_address:\s*(\S+)', block)
            m_name = re.search(r'PROXY_NAME:\s*["\']?([^\s"\'#\n]+)', block)
            if m_ip and m_name:
                ip   = m_ip.group(1).strip()
                name = m_name.group(1).strip("\"'").lower()
                names[name] = ip
    except Exception as e:
        print(f"Compose config error: {e}", flush=True)
    return names

def parse_name(data, offset):
    labels = []
    for _ in range(128):
        if offset >= len(data): break
        length = data[offset]
        if length == 0:
            offset += 1
            break
        offset += 1
        labels.append(data[offset:offset+length].decode("utf-8", errors="ignore"))
        offset += length
    return ".".join(labels), offset

def encode_name(name):
    out = b""
    for label in name.rstrip(".").split("."):
        enc = label.encode("utf-8")
        out += bytes([len(enc)]) + enc
    return out + b"\x00"

def handle(data, addr, sock, names):
    if len(data) < 12: return
    tx_id = data[0:2]
    flags = struct.unpack("!H", data[2:4])[0]
    if flags & 0x8000: return
    qdcount = struct.unpack("!H", data[4:6])[0]
    if qdcount == 0: return
    offset = 12
    name, offset = parse_name(data, offset)
    if offset + 4 > len(data): return
    qtype = struct.unpack("!H", data[offset:offset+2])[0]
    if qtype != 1: return
    key = name.lower().rstrip(".")
    if key not in names: return
    ip = names[key]
    print(f"LLMNR: {name} -> {ip}  (from {addr[0]})", flush=True)
    r  = tx_id
    r += struct.pack("!H", 0x8000)
    r += struct.pack("!HHHH", 1, 1, 0, 0)
    r += encode_name(name)
    r += struct.pack("!HH", 1, 1)
    r += encode_name(name)
    r += struct.pack("!HH", 1, 1)
    r += struct.pack("!I", 30)
    r += struct.pack("!H", 4)
    r += bytes(int(x) for x in ip.split("."))
    sock.sendto(r, addr)

def main():
    names = load_names()
    print(f"LLMNR responder v3, {len(names)} Namen:", flush=True)
    for n, ip in sorted(names.items()):
        print(f"  {n} -> {ip}", flush=True)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try: sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError: pass
    sock.bind(("", LLMNR_PORT))
    mreq = struct.pack("4s4s", socket.inet_aton(LLMNR_MCAST), socket.inet_aton("0.0.0.0"))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.settimeout(30.0)
    last_reload = time.time()
    def stop(sig, frame):
        print("LLMNR: stopping", flush=True)
        sock.close()
        sys.exit(0)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    print(f"Hoere auf {LLMNR_MCAST}:{LLMNR_PORT} ...", flush=True)
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            now = time.time()
            if now - last_reload > 60:
                names = load_names()
                last_reload = now
            handle(data, addr, sock, names)
        except socket.timeout: continue
        except OSError: break
        except Exception as e:
            print(f"LLMNR error: {e}", flush=True)

if __name__ == "__main__":
    main()
