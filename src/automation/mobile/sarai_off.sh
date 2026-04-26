#!/data/data/com.termux/files/usr/bin/bash
# OMEGA PROTOCOL: SARAI OFF (Home Screen Toggle)
pkill -f sarai_core
termux-wake-unlock
termux-toast "✦ SARAI MANIFOLD: OFFLINE"
