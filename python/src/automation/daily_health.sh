#!/bin/bash
# Daily health check automation

cd ~/forge
LOG_FILE="$HOME/forge/logs/forge_health.txt"

echo "=== EXPLORER-d334 Daily Health Report ===" > "$LOG_FILE"
echo "Time: $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Run health check
./forge health >> "$LOG_FILE" 2>&1

# Check cube count
echo "" >> "$LOG_FILE"
echo "=== Knowledge Cubes ===" >> "$LOG_FILE"
./forge cubes | head -10 >> "$LOG_FILE" 2>&1

# Log to memory
echo "[AUTO] Daily health check completed at $(date)" >> ~/forge/chat_history.json 2>/dev/null

# Optional: Send notification (if Termux has notification support)
if command -v termux-notification &> /dev/null; then
    termux-notification --title "Explorer-d334" --content "Daily health check completed" --priority low
fi

echo "Daily health check completed at $(date)"
echo "Log saved to: $LOG_FILE"
