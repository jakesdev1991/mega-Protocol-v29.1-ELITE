#!/data/data/com.termux/files/usr/bin/bash
# OMEGA PROTOCOL: SARAI ON (Home Screen Toggle)
termux-wake-lock
cd /data/data/com.termux/files/home/sarai_ready/src
nohup ./sarai_core > sarai.log 2>&1 &
termux-toast "✦ SARAI MANIFOLD: ACTIVE"
