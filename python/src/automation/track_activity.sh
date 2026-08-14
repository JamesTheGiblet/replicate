#!/bin/bash
# Track user activity for smarter dreaming

ACTIVITY_FILE="$HOME/forge/logs/user_activity.log"
mkdir -p "$HOME/forge/logs"

# Log current activity
echo "$(date +%s):forge_command" >> "$ACTIVITY_FILE"
tail -n 1000 "$ACTIVITY_FILE" > "$ACTIVITY_FILE.tmp"
mv "$ACTIVITY_FILE.tmp" "$ACTIVITY_FILE"

# Also track web interface activity
if [ -f "$HOME/forge/atomicforge.html" ]; then
    touch "$HOME/forge/.web_activity"
fi
