# System Architecture – Alpine SMB Port Proxy

Dieses Dokument beschreibt die interne Funktionsweise des Systems vollständig.

---

## 🧠 Grundidee

Das System ist kein einzelnes Programm, sondern eine **Kette von Schichten**, die zusammenarbeiten.

Ziel:

→ Windows denkt, es spricht mit einem echten SMB-Server
→ tatsächlich wird nur TCP weitergeleitet

---

## 🔄 Gesamtablauf

```
Browser (User klickt)
    ↓
index.html (Web GUI)
    ↓
CGI Script (z.B. add-device.cgi)
    ↓
Shell Script (add-proxy.sh)
    ↓
Python Script (proxy-compose-add.py)
    ↓
docker-compose.yml wird verändert
    ↓
docker compose up startet Container
    ↓
Container (proxy-agent)
    ↓
socat leitet TCP weiter
    ↓
Android Gerät
```

---

## 🧩 Komponenten im Detail

---

### 1. Webinterface (Frontend)

Ort:

```
/var/www/localhost/htdocs/
```

Bestandteile:

* `index.html` → UI
* `cgi-bin/*` → Backend-Endpunkte

Funktion:

* Benutzer interagiert mit HTML
* Aktionen werden per CGI an das System weitergegeben

---

### 2. CGI-Schicht

Technik:

* BusyBox `httpd`
* klassische CGI (kein Framework)

Beispiel:

```
add-device.cgi
```

macht:

```
POST lesen → Parameter extrahieren → Shell-Skript aufrufen
```

---

### 3. Engine (Shell + Python)

Ort:

```
/usr/local/bin/
```

Aufgaben:

* Container erzeugen
* docker-compose manipulieren
* Netzwerk scannen
* Status liefern

Wichtige Dateien:

* `add-proxy.sh`
* `del-proxy.sh`
* `proxy-compose-add.py`

---

## 🔑 Zentrales Element

```
/var/lib/proxy/docker-compose.yml
```

Das ist die **Single Source of Truth**.

Alles basiert darauf.

---

## 🐳 Docker-Schicht

Für jedes Gerät:

* eigener Container
* eigene IP (macvlan)
* eigener Name

Beispiel:

```
proxy-124 → 192.168.178.124
```

---

## 📡 Netzwerk (macvlan)

Warum wichtig:

* Container erscheinen wie echte Geräte im LAN
* eigene MAC-Adresse
* eigene IP

Ohne das:

→ Port-Konflikte
→ kein echtes Windows-Verhalten

---

## ⚙️ Container (proxy-agent)

Minimaler Aufbau:

* Alpine Linux
* socat
* wsdd
* avahi
* dbus

---

## 🔁 Laufzeit im Container

### entrypoint.sh macht:

1. Parameter prüfen
2. UUID generieren
3. eigene IP ermitteln
4. dbus starten
5. avahi konfigurieren
6. SMB-Service announcen
7. socat starten
8. wsdd starten (blockiert → hält Container aktiv)

---

## 🔌 Datenfluss

```
Windows Explorer
    ↓ (Port 445)
Container IP
    ↓ (socat)
Android Gerät:1445
```

---

## 📣 Sichtbarkeit im Netzwerk

Damit Windows den Proxy sieht:

* LLMNR → eigener Python-Daemon
* WSDD → im Container
* Avahi → mDNS

---

## 🧨 Warum kein Samba

Absichtlich NICHT:

* kein Re-Sharing
* keine Locks
* kein zusätzlicher Overhead

→ nur TCP Forward

---

## ⚠️ Kritische Punkte

### 1. Hypervisor

MUSS können:

* MAC Spoofing
* Promiscuous Mode

---

### 2. Netzwerk

macvlan funktioniert nicht:

* in NAT
* ohne direkten LAN-Zugriff

---

### 3. Port 445

Nur EIN Prozess pro IP möglich

→ deshalb eigene IP pro Container

---

## 🎯 Fazit

Das System ist:

* kein klassischer Server
* kein Proxy im üblichen Sinne

sondern:

→ ein **verteilter Netzwerk-Adapter auf Containerbasis**
