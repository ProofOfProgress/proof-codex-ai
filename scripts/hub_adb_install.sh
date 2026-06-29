#!/usr/bin/env bash
# Install Android platform-tools (adb) on the owner hub laptop (WSL Ubuntu).
set -euo pipefail

echo "==> Installing adb (Android platform-tools)..."
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y adb

echo "==> adb version:"
adb version | head -1

echo ""
echo "Next (when phones arrive):"
echo "  1. Enable USB debugging on each phone"
echo "  2. Windows: usbipd attach (see docs/FOR_OWNER_PHONE_HUB.md)"
echo "  3. WSL: adb devices"
echo "  4. Fill serials in data/phone_hub/devices.json"
