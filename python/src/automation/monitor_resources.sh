#!/bin/bash
# Monitor system resources every 5 minutes

cd ~/forge
MONITOR_FILE="$HOME/forge/logs/forge_monitor.log"
mkdir -p "$HOME/forge/logs"

# Check disk space
DISK=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK" -gt 90 ]; then
    echo "[WARNING] Low disk space: ${DISK}% at $(date)" >> "$MONITOR_FILE"
    if command -v termux-notification &> /dev/null; then
        termux-notification --title "Explorer-d334 Warning" --content "Low disk space: ${DISK}%" --priority high
    fi
fi

# Check memory
MEM=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
if [ "$MEM" -gt 90 ]; then
    echo "[WARNING] High memory usage: ${MEM}% at $(date)" >> "$MONITOR_FILE"
fi

# Log to history (summary only)
echo "[MONITOR] Disk: ${DISK}%, Memory: ${MEM}% at $(date)" >> ~/forge/chat_history.json 2>/dev/null
