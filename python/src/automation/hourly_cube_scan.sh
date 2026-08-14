#!/bin/bash
# Scan for missing cube perspectives

cd ~/forge
SCAN_LOG="$HOME/forge/logs/forge_cube_scan.log"
mkdir -p "$HOME/forge/logs"

echo "=== Cube Scan at $(date) ===" >> "$SCAN_LOG"
./forge cube-scan >> "$SCAN_LOG" 2>&1

# Check if new proposals were found
if grep -q "proposal" "$SCAN_LOG" 2>/dev/null; then
    echo "[AUTO] New cube proposals found at $(date)" >> ~/forge/chat_history.json
    if command -v termux-notification &> /dev/null; then
        termux-notification --title "Explorer-d334" --content "New cube perspectives found!" --priority normal
    fi
fi

echo "Cube scan completed at $(date)"
