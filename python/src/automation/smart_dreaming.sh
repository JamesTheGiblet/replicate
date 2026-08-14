#!/bin/bash
# Smart dreaming based on user activity and time of day

cd ~/forge
LOG_FILE="$HOME/forge/logs/dream_log.txt"
ACTIVITY_FILE="$HOME/forge/logs/user_activity.log"
DREAM_DIR="$HOME/forge/memories/dreams"

mkdir -p "$DREAM_DIR"
mkdir -p "$HOME/forge/logs"

# Function to save dream to JSON and history
save_dream() {
    local dream_type="$1"
    local dream_content="$2"
    local timestamp=$(date -Iseconds)
    
    # Save to dream_history.txt
    echo "[$timestamp]" >> "$DREAM_DIR/dream_history.txt"
    echo "$dream_content" >> "$DREAM_DIR/dream_history.txt"
    echo "" >> "$DREAM_DIR/dream_history.txt"
    
    # Save as JSON
    dream_data='{"timestamp":"'"$timestamp"'","content":"'"$dream_content"'","type":"'"$dream_type"'"}'
    dream_filename="$DREAM_DIR/DREAM-$(date +%Y%m%d-%H%M%S).json"
    echo "$dream_data" | python3 -m json.tool > "$dream_filename" 2>/dev/null || echo "$dream_data" > "$dream_filename"
    
    echo "[DREAM] $dream_type dream saved to memory" >> "$LOG_FILE"
}

# Generate and save a dream
generate_and_save_dream() {
    local dream_type="$1"
    local DREAM=$(./forge dream 2>/dev/null | cat)
    
    # Clean up the dream content (remove the emoji prefix if present)
    DREAM=$(echo "$DREAM" | sed 's/^[^a-zA-Z]*//')
    
    if [ -n "$DREAM" ]; then
        save_dream "$dream_type" "$DREAM"
        echo "💭 Generated $dream_type dream" >> "$LOG_FILE"
    fi
}

# Check if user is active
check_activity() {
    # Check for recent forge commands
    local recent_activity=$(find "$HOME/forge" -name "chat_history.json" -o -name "*.log" 2>/dev/null | xargs ls -t 2>/dev/null | head -1)
    if [ -n "$recent_activity" ]; then
        local cmd_time=$(stat -c %Y "$recent_activity" 2>/dev/null || echo 0)
        local now=$(date +%s)
        echo $((now - cmd_time))
    else
        echo 3600
    fi
}

# Main dreaming logic
main() {
    local hour=$(date +%H)
    local inactive_seconds=$(check_activity)
    local inactive_minutes=$((inactive_seconds / 60))
    
    # Night dreaming: 11 PM to 6 AM (sleep hours)
    if [ $hour -ge 23 ] || [ $hour -lt 6 ]; then
        # Generate night dream every 2 hours during sleep
        if [ ! -f "$HOME/forge/logs/.night_dream_$hour" ]; then
            generate_and_save_dream "NIGHT"
            touch "$HOME/forge/logs/.night_dream_$hour"
            # Clean up old hour markers
            find "$HOME/forge/logs" -name ".night_dream_*" -mmin +120 -delete 2>/dev/null
        fi
    else
        # Daytime - generate daydream after 30+ minutes of inactivity
        if [ $inactive_minutes -gt 30 ]; then
            if [ ! -f "$HOME/forge/logs/.daydream_recent" ]; then
                generate_and_save_dream "DAYDREAM"
                touch "$HOME/forge/logs/.daydream_recent"
                # Reset after 2 hours
                (sleep 7200; rm -f "$HOME/forge/logs/.daydream_recent") &
            fi
        else
            # Remove daydream flag if user becomes active
            rm -f "$HOME/forge/logs/.daydream_recent" 2>/dev/null
        fi
    fi
}

main
