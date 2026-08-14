#!/bin/bash
# Generate and save daily thought

cd ~/forge
THOUGHT=$(./forge think 2>/dev/null | head -1)

# Save to thoughts directory
mkdir -p memories/thoughts
echo "[$(date)] $THOUGHT" >> memories/thoughts/daily_thoughts.txt

echo "[AUTO] Daily thought generated at $(date)" >> ~/forge/chat_history.json 2>/dev/null

# Log to file
mkdir -p logs
echo "[$(date)] Thought: $THOUGHT" >> logs/daily_thoughts.log

echo "Daily thought: $THOUGHT"
