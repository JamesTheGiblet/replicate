#!/bin/bash
# Weekly backup automation

cd ~/forge
BACKUP_DIR="$HOME/forge/forge_backups"
mkdir -p "$BACKUP_DIR"

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="forge_backup_$DATE"

echo "=== Weekly Backup ==="
echo "Starting backup at $(date)"

# Create backup
./backup.sh

# Compress old backups (keep last 4 weeks)
cd "$BACKUP_DIR"
ls -t forge_backup_* 2>/dev/null | tail -n +5 | xargs rm -rf 2>/dev/null

echo "Backup completed at $(date)"
echo "[AUTO] Weekly backup completed: $BACKUP_NAME" >> ~/forge/chat_history.json 2>/dev/null

# Notification
if command -v termux-notification &> /dev/null; then
    termux-notification --title "Explorer-d334 Backup" --content "Weekly backup completed" --priority low
fi
