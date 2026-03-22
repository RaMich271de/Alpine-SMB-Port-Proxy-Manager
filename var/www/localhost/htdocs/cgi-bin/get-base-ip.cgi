#!/bin/sh
echo "Content-Type: text/plain"
echo ""

# Erste IP von eth0 ist die Basis-IP
ip addr show eth0 | grep 'inet ' | head -1 | awk '{print $2}' | cut -d'/' -f1
