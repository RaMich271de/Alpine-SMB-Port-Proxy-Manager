Android SMB Port-Proxy Appliance
A lightweight, Alpine-Linux based Virtual Machine appliance designed to solve a very specific but frustrating problem: Mounting non-rooted Android SMB shares in Windows.

🚨 The Problem
If you want to share files from an Android device via SMB over Wi-Fi, you'll hit a wall:
Android (without root) cannot open ports below 1024. Therefore, Android SMB server apps usually run on high ports like 1445 or 4450.
Windows File Explorer (net use / \\IP) is strictly hardcoded to use port 445 for SMB. It completely ignores custom ports.
The result: You cannot natively mount an Android phone as a Windows network drive without root or paid third-party software.

💡 The Solution
This project is a micro-appliance (a lightweight Alpine Linux VM) that acts as a transparent Man-in-the-Middle Proxy-Cluster.
For every Android device in your network, the VM spawns a tiny Docker container with its own physical MAC/IP address (via macvlan). This container listens on standard port 445 and passes the TCP traffic directly to your Android's high port (e.g., 1445).
To Windows, your Android phone looks like a standard enterprise Windows Server.

✨ Key Features & Architecture
Native Web-GUI: A blazing fast, zero-dependency CGI web interface (HTML/JS/ash) to scan your network and manage proxies.
Docker Macvlan: Every forwarded device gets its own real IP address on your network. No port conflicts, no IP-Aliasing bugs.
Zero TCP-Overhead: Uses raw socat for Layer-4 forwarding. No Samba re-sharing, no file-lock issues, perfect performance for streaming (e.g., mp3/video).
Built-in LLMNR Responder: Windows automatically sees the proxies by their hostname (e.g., Tablet-Proxy) in the "Network" tab of the File Explorer without relying on heavy WSDD broadcasting.
Hyper-V Ready: Easily runs as a tiny Hyper-V guest on your Windows machine.

🛠️ Prerequisites
A Hypervisor (Hyper-V, VirtualBox, Proxmox) attached to your LAN.
Crucial: Your Hypervisor virtual switch must have MAC Address Spoofing / Promiscuous Mode enabled, otherwise the Docker Macvlan containers won't be able to communicate with your router!

📸 Screenshots

<img width="542" height="827" alt="Webinterface" src="https://github.com/user-attachments/assets/771ea6f3-5070-4c74-8349-84e1d9e21642" />

<img width="802" height="195" alt="Explorer" src="https://github.com/user-attachments/assets/991ae271-a8bf-4be3-848a-f9542a89482b" />

🚀 How it works under the hood
The Web-GUI is powered by the built-in httpd of BusyBox. When you add a new device, a python script dynamically injects a new service into a central docker-compose.yml. Docker brings up a minimal Alpine container running socat. The VM's custom LLMNR-Responder immediately announces the new IP to Windows.
