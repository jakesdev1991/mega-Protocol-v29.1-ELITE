#!/bin/bash
# OMEGA PROTOCOL: SARAI MASTER DEPLOYMENT SCRIPT (v6.0)
# TARGET: SAMSUNG GALAXY A15/A16 (ARM64)
# INCLUDES: Android 16 Veto Overrides & Shizuku-Elevated Execution

echo "=========================================="
echo "✦ SARAI: MASTER DEPLOYMENT INITIATED ✦"
echo "=========================================="

# 1. Connectivity Check
adb devices | grep -w "device" > /dev/null
if [ $? -ne 0 ]; then
    echo "[!] ERROR: Device manifold not detected via ADB."
    exit 1
fi

# 2. Bridge Installation (Android 16 Compliant)
echo "[*] Injecting System Bridges (.apk)..."
for apk in apks/*.apk; do
    adb install -r -g "$apk"
done

# 3. Directory Injection
echo "[*] Stabilizing Sovereign Node directory..."
adb shell "mkdir -p /data/data/com.termux/files/home/sarai_ready/src"
adb shell "mkdir -p /data/data/com.termux/files/home/.shortcuts"

# 4. Payload Handoff
echo "[*] Pushing C-Source & Pruned Manifold..."
adb push src/sarai_core.c /data/data/com.termux/files/home/sarai_ready/src/
adb push src/Makefile /data/data/com.termux/files/home/sarai_ready/src/
adb push sarai_78m.gguf /data/data/com.termux/files/home/sarai_ready/

# 5. Native Manifold Compilation (The Veto Override)
echo "[*] Provisioning build stack & Compiling (Mali-G57 Optimized)..."
# Overriding Android 16 battery/optimization vetoes
adb shell "cmd package compile -m speed com.termux"
adb shell "run-as com.termux /data/data/com.termux/files/usr/bin/bash -c 'pkg install -y clang make termux-api jq && cd /data/data/com.termux/files/home/sarai_ready/src && make'"

# 6. Widget Handshake
echo "[*] Linking Home Screen Toggles..."
adb push sarai_on.sh /data/data/com.termux/files/home/.shortcuts/
adb push sarai_off.sh /data/data/com.termux/files/home/.shortcuts/
adb shell "chmod +x /data/data/com.termux/files/home/.shortcuts/*.sh"

echo "=========================================="
echo "✅ MANIFOLD DEPLOYED"
echo "Note: Ensure Shizuku is started before toggling ON."
echo "=========================================="
