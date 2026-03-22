# Android SMB Port-Proxy Appliance

A minimal Alpine Linux based appliance that transparently exposes Android SMB shares to Windows by solving the **port 445 limitation**.

---

## 🚨 Problem

Android SMB Apps (ohne Root):

* können **keine Ports <1024 öffnen**
* laufen daher auf Ports wie `1445`, `4450`

Windows:

* nutzt **IMMER Port 445**
* ignoriert andere Ports vollständig

➡️ Ergebnis:
**Android SMB Shares sind in Windows nicht mountbar.**

---

## 💡 Lösung

Dieses Projekt erstellt eine Proxy-Schicht:

* Für jedes Gerät wird ein **Docker-Container** erzeugt
* Jeder Container bekommt:

  * **eigene IP (macvlan)**
  * **Port 445**
* Weiterleitung erfolgt per `socat` auf z. B. `192.168.x.x:1445`

➡️ Für Windows sieht jedes Gerät wie ein echter SMB-Server aus.

---

## 🧠 Architektur

```
Browser (Web-GUI)
        │
        ▼
CGI (BusyBox httpd)
        │
        ▼
Shell / Python Engine
        │
        ▼
docker-compose.yml  ← zentrale "Datenbank"
        │
        ▼
Docker Container (proxy-agent)
        │
        ▼
socat → Android Gerät
```

---

## 📂 Projektstruktur

```
/
├── etc/
│   └── init.d/
│       └── llmnr-responder             [Autostart: Windows Namensauflösung]
│
├── usr/
│   └── local/
│       └── bin/                        [ENGINE]
│           ├── add-proxy.sh
│           ├── del-proxy.sh
│           ├── proxy-compose-add.py
│           ├── proxy-compose-del.py
│           ├── proxy-list-devices.py
│           ├── proxy-network-info.py
│           ├── llmnr-responder.py
│           ├── arp-scan-wrapper.sh
│           ├── restart-all.sh
│           ├── system-update.sh
│           └── ...
│
├── var/
│   ├── lib/
│   │   └── proxy/                      [STATE]
│   │       ├── docker-compose.yml
│   │       ├── llmnr-static.conf
│   │       └── weblink/
│   │           └── Webinterface.url
│   │
│   └── www/
│       └── localhost/
│           └── htdocs/                 [WEB-GUI]
│               ├── index.html
│               ├── cgi-bin/
│               │   ├── add-device.cgi
│               │   ├── delete-device.cgi
│               │   ├── list-devices.cgi
│               │   ├── status.cgi
│               │   └── ...
│               └── system-diagnose/
│                   └── index.html
```

---

## 🐳 Docker: proxy-agent

### Dockerfile

Der Container basiert auf Alpine und enthält nur:

* `socat` → TCP Proxy
* `wsdd` → Windows Discovery
* `avahi` → mDNS
* `dbus` → notwendig für Avahi

### entrypoint.sh

Beim Start passiert:

1. Validierung der Parameter
2. UUID erzeugen
3. Avahi konfigurieren (SMB Service)
4. dbus + avahi starten
5. `socat` startet TCP-Forward
6. `wsdd` hält Container aktiv

➡️ Der Container ist ein **reiner Netzwerk-Adapter + Proxy**

---

## ⚙️ Voraussetzungen

* Hypervisor (Hyper-V, Proxmox, VirtualBox)
* **WICHTIG:**

  * MAC Spoofing / Promiscuous Mode aktivieren
  * sonst funktioniert macvlan nicht

---

## 🚀 Funktionsweise

1. Gerät im Webinterface hinzufügen
2. Script schreibt Eintrag in:

```
/var/lib/proxy/docker-compose.yml
```

3. Docker startet Container:

```
proxy-XYZ → eigene IP → Port 445
```

4. Windows erkennt Gerät automatisch via:

* LLMNR
* WSDD
* Avahi

---

## 🧩 Warum das funktioniert

* Windows glaubt:
  → echter SMB Server auf Port 445

* tatsächlich:
  → Weiterleitung auf Android-Port

---

## ⚠️ Wichtige Hinweise

* Kein Samba → kein Re-Sharing → keine Locks
* Reiner TCP-Forward → maximale Performance
* Jeder Proxy ist isoliert (eigene IP)

---

## 🔧 Ziel dieses Projekts

Kein Framework.
Keine Abhängigkeiten.
Kein Overengineering.

➡️ Nur ein präzises Werkzeug für genau ein Problem.

## 📚 Weiterführende Details

Für ein vollständiges Verständnis der internen Funktionsweise siehe:

👉 SYSTEM.md

