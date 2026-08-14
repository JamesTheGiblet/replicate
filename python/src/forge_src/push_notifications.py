#!/usr/bin/env python3
"""
Push Notification System for Explorer-d334
Sends notifications to your Android device
"""

import subprocess
import sqlite3
from datetime import datetime
from pathlib import Path

class PushNotifications:
    def __init__(self):
        self.db_path = Path("forge_data.db")
        self.init_db()
    
    def init_db(self):
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                message TEXT,
                timestamp TIMESTAMP,
                sent INTEGER DEFAULT 0,
                read INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()
    
    def send(self, title, message, priority="normal"):
        """Send a push notification"""
        try:
            # Use termux-notification
            cmd = [
                "termux-notification",
                "--title", title,
                "--content", message,
                "--priority", priority,
                "--button1", "Open Forge",
                "--button1-action", "termux-open http://localhost:8085"
            ]
            subprocess.run(cmd, timeout=5, capture_output=True)
            
            # Log to database
            self.cursor.execute('''
                INSERT INTO notifications (title, message, timestamp, sent)
                VALUES (?, ?, ?, 1)
            ''', (title, message, datetime.now().isoformat()))
            self.conn.commit()
            
            return True
        except Exception as e:
            print(f"Notification failed: {e}")
            return False
    
    def send_thought(self, thought):
        return self.send("🧠 Explorer-d334 Thought", thought[:100], "low")
    
    def send_dream(self, dream):
        return self.send("💭 Explorer-d334 Dream", dream[:100], "low")
    
    def send_alert(self, alert_type, message):
        icons = {"security": "🔒", "health": "🏥", "capsule": "📦", "reminder": "⏰"}
        icon = icons.get(alert_type, "⚠️")
        return self.send(f"{icon} Explorer-d334 Alert", message, "high")
    
    def send_good_morning(self):
        from datetime import datetime
        now = datetime.now()
        return self.send("🌅 Good Morning!", f"Today is {now.strftime('%A, %B %d')}. The forge awaits.", "normal")
    
    def send_good_night(self):
        return self.send("🌙 Good Night!", "The forge will keep dreaming while you rest.", "low")
    
    def get_history(self, limit=20):
        self.cursor.execute('''
            SELECT title, message, timestamp FROM notifications 
            ORDER BY id DESC LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

# Integrate with service
def notify_thought():
    import subprocess
    result = subprocess.run(["./forge", "think"], capture_output=True, text=True, timeout=10)
    if result.stdout:
        pn = PushNotifications()
        pn.send_thought(result.stdout.strip())
        pn.close()

def notify_dream():
    import subprocess
    result = subprocess.run(["./forge", "dream"], capture_output=True, text=True, timeout=10)
    if result.stdout:
        pn = PushNotifications()
        pn.send_dream(result.stdout.strip())
        pn.close()

if __name__ == "__main__":
    import sys
    pn = PushNotifications()
    
    if len(sys.argv) < 2:
        print("Push Notification Commands:")
        print("  send <title> <message>")
        print("  thought")
        print("  dream")
        print("  morning")
        print("  night")
        print("  history")
    
    elif sys.argv[1] == "send":
        title = sys.argv[2]
        message = sys.argv[3] if len(sys.argv) > 3 else ""
        pn.send(title, message)
    
    elif sys.argv[1] == "thought":
        notify_thought()
    
    elif sys.argv[1] == "dream":
        notify_dream()
    
    elif sys.argv[1] == "morning":
        pn.send_good_morning()
    
    elif sys.argv[1] == "night":
        pn.send_good_night()
    
    elif sys.argv[1] == "history":
        history = pn.get_history()
        for h in history:
            print(f"  [{h[2][:19]}] {h[0]}: {h[1][:50]}")
    
    pn.close()
