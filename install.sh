#!/usr/bin/env bash

echo "[+] Installing Python 3..."
apt install python3 python3-pip

echo "[+] Installing required Python packages..."
pip3 install beautifulsoup4 requests

echo "[+] Installing jauth..."
cp jauth.py /usr/bin/jauth
chmod a+x /usr/bin/jauth
