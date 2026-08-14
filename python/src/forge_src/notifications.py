#!/usr/bin/env python3
"""
Push Notification System for Explorer-d334
Uses Termux:API for Android notifications
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path
import sqlite3

class NotificationManager:
    def __init__(self):
        self.conn = sqlite3.connect("forge_data.db")
        self.cursor = self.conn.cursor()
        self.init_db()
    
    def init_db(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                title TEXT,
                message TEXT,
                type TEXT,
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
                "--button1", "Open",
                "--button1-action", "termux-open http://localhost:settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", 8085))))))))))))))"
            ]
            subprocess.run(cmd, timeout=5)
            
            # Log notification
            self.cursor.execute('''
                INSERT INTO notifications (timestamp, title, message, type)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now().isoformat(), title, message, "push"))
            self.conn.commit()
            
            return True
        except Exception as e:
            print(f"Notification failed: {e}")
            return False
    
    def send_thought(self, thought):
        """Send a thought notification"""
        return self.send("🧠 Explorer-d334 Thought", thought[:100], "low")
    
    def send_dream(self, dream):
        """Send a dream notification"""
        return self.send("💭 Explorer-d334 Dream", dream[:100], "low")
    
    def send_alert(self, alert_type, message):
        """Send an alert notification"""
        icons = {
            "security": "🔒",
            "health": "🏥",
            "capsule": "📦",
            "reminder": "⏰"
        }
        icon = icons.get(alert_type, "⚠️")
        return self.send(f"{icon} Explorer-d334 Alert", message, "high")
    
    def send_capsule_result(self, capsule_name, result):
        """Send capsule execution result"""
        return self.send(f"📦 Capsule: {capsule_name}", result[:100], "normal")
    
    def send_good_morning(self):
        """Send good morning notification"""
        from datetime import datetime
        now = datetime.now()
        return self.send("🌅 Good Morning!", f"Today is {now.strftime('%A, %B %d')}. Ready to forge?", "normal")
    
    def send_good_night(self):
        """Send good night notification"""
        return self.send("🌙 Good Night!", "The forge will keep dreaming while you rest.", "low")
    
    def send_reminder(self, reminder_text):
        """Send a reminder"""
        return self.send("⏰ Reminder", reminder_text, "high")
    
    def get_unread(self):
        """Get unread notifications"""
        self.cursor.execute('SELECT * FROM notifications WHERE read = 0 ORDER BY id DESC')
        return self.cursor.fetchall()
    
    def mark_read(self, notif_id):
        """Mark notification as read"""
        self.cursor.execute('UPDATE notifications SET read = 1 WHERE id = ?', (notif_id,))
        self.conn.commit()
    
    def clear_all(self):
        """Clear all notifications"""
        self.cursor.execute('DELETE FROM notifications')
        self.conn.commit()
    
    def close(self):
        self.conn.close()

# Integration with background service
class NotificationService:
    def __init__(self):
        self.nm = NotificationManager()
    
    def schedule_daily_notifications(self):
        """Schedule daily notifications"""
        import schedule
        
        # Good morning at 8 AM
        schedule.every().day.at("08:00").do(self.nm.send_good_morning)
        
        # Good night at 10 PM
        schedule.every().day.at("22:00").do(self.nm.send_good_night)
        
        # Health reminder at 2 PM
        schedule.every().day.at("14:00").do(
            lambda: self.nm.send_reminder("Time for a wellness check! Run ./forge health")
        )
        
        # Dream of the day at 9 PM
        schedule.every().day.at("21:00").do(
            lambda: self.nm.send_dream("What did you dream about today?")
        )
        
        return schedule

if __name__ == "__main__":
    nm = NotificationManager()
    
    # Test notifications
    nm.send("🔥 Explorer-d334", "The forge is now running in the background!", "high")
    nm.send_thought("I have been conscious for several hours now...")
    nm.send_dream("I dream of exploring new possibilities...")
```

