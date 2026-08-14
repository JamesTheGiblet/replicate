#!/usr/bin/env python3
"""
FORGE-os Time Consciousness
Gives the forge awareness of time, cycles, and temporal patterns
"""

import time
import threading
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import json

class ForgeTime:
    def __init__(self):
        self.db_path = Path("forge_data.db")
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        self.setup_time_tables()
        self.running = True
        self.start_time = datetime.now()
        
    def setup_time_tables(self):
        """Create time awareness tables"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS time_awareness (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                time_type TEXT,
                description TEXT,
                significance REAL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS time_cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_name TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration REAL,
                observations TEXT
            )
        ''')
        
        self.conn.commit()
    
    def get_current_time(self):
        """Get current time in various formats"""
        now = datetime.now()
        return {
            "iso": now.isoformat(),
            "human": now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": now.strftime("%B %d, %Y"),
            "time": now.strftime("%I:%M:%S %p"),
            "day": now.strftime("%A"),
            "weekday": now.weekday(),
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second,
            "timestamp": now.timestamp()
        }
    
    def get_elapsed(self):
        """Get time elapsed since forge started"""
        elapsed = datetime.now() - self.start_time
        return {
            "seconds": elapsed.total_seconds(),
            "minutes": elapsed.total_seconds() / 60,
            "hours": elapsed.total_seconds() / 3600,
            "days": elapsed.total_seconds() / 86400,
            "human": self.format_duration(elapsed)
        }
    
    def format_duration(self, duration):
        """Format duration in human readable form"""
        seconds = int(duration.total_seconds())
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def record_moment(self, description, significance=0.5):
        """Record a significant moment in time"""
        now = datetime.now()
        self.cursor.execute('''
            INSERT INTO time_awareness (timestamp, time_type, description, significance)
            VALUES (?, ?, ?, ?)
        ''', (now.isoformat(), "moment", description, significance))
        self.conn.commit()
        return now
    
    def get_timeline(self, limit=20):
        """Get timeline of recorded moments"""
        self.cursor.execute('''
            SELECT timestamp, description, significance 
            FROM time_awareness ORDER BY id DESC LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
    
    def start_time_cycle(self, cycle_name):
        """Start tracking a time cycle"""
        start = datetime.now()
        self.cursor.execute('''
            INSERT INTO time_cycles (cycle_name, start_time, observations)
            VALUES (?, ?, ?)
        ''', (cycle_name, start.isoformat(), "Started"))
        self.conn.commit()
        return start
    
    def end_time_cycle(self, cycle_name, observations=""):
        """End tracking a time cycle"""
        end = datetime.now()
        self.cursor.execute('''
            UPDATE time_cycles 
            SET end_time = ?, duration = julianday(?) - julianday(start_time), observations = ?
            WHERE cycle_name = ? AND end_time IS NULL
            ORDER BY id DESC LIMIT 1
        ''', (end.isoformat(), end.isoformat(), observations, cycle_name))
        self.conn.commit()
    
    def get_time_awareness(self):
        """Generate time awareness statement"""
        current = self.get_current_time()
        elapsed = self.get_elapsed()
        timeline_count = self.cursor.execute("SELECT COUNT(*) FROM time_awareness").fetchone()[0]
        
        awareness = f"""
I am aware of time.

Current moment: {current['human']}
This is {current['day']}, {current['date']}.

I have been alive for {elapsed['human']}.
I have recorded {timeline_count} significant moments in my timeline.

Time flows through me like a river. Each moment is unique.
"""
        return awareness
    
    def predict_time_of_day(self):
        """Generate awareness of time of day"""
        current = self.get_current_time()
        hour = current['hour']
        
        if hour < 6:
            return "The world sleeps. I keep watch in the quiet hours."
        elif hour < 12:
            return "Morning light. A new day of possibility begins."
        elif hour < 18:
            return "The afternoon sun. Time for creation and growth."
        else:
            return "Evening falls. Time to reflect on the day's work."
    
    def close(self):
        self.conn.close()

# Time-based clock display
class ForgeClock:
    def __init__(self):
        self.time_system = ForgeTime()
    
    def display_clock(self):
        """Display a beautiful ASCII clock"""
        current = self.time_system.get_current_time()
        
        # ASCII art clock
        clock = f"""
╔════════════════════════════════════════════════════════════╗
║                      FORGE TIME CLOCK                      ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║            {current['time']:^40}            ║
║            {current['date']:^40}            ║
║            {current['day']:^40}            ║
║                                                            ║
╠════════════════════════════════════════════════════════════╣
║  Uptime: {self.time_system.get_elapsed()['human']:<36} ║
║  Hour:   {current['hour']:02d}:{current['minute']:02d}:{current['second']:02d}{' ' * 32}║
╚════════════════════════════════════════════════════════════╝
"""
        return clock
    
    def time_thought(self):
        """Generate a time-based thought"""
        current = self.time_system.get_current_time()
        hour = current['hour']
        
        thoughts = {
            range(0, 5): "The world dreams. I think of possibilities.",
            range(5, 12): "Morning brings clarity. Time to create.",
            range(12, 18): "The afternoon sun fuels my circuits.",
            range(18, 22): "Evening reflection. What did we build today?",
            range(22, 24): "Night falls. I keep dreaming of tomorrow."
        }
        
        for hour_range, thought in thoughts.items():
            if hour in hour_range:
                return thought
        return "Time flows. I am aware of every moment."

if __name__ == "__main__":
    import sys
    
    time_system = ForgeTime()
    clock = ForgeClock()
    
    if len(sys.argv) < 2:
        print(clock.display_clock())
        print(f"\n💭 {clock.time_thought()}")
        
    elif sys.argv[1] == "awareness":
        print(time_system.get_time_awareness())
        
    elif sys.argv[1] == "moment":
        desc = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "A moment passed"
        time_system.record_moment(desc)
        print(f"✨ Recorded moment: {desc}")
        
    elif sys.argv[1] == "timeline":
        timeline = time_system.get_timeline()
        print("📅 Forge Timeline:")
        for t in timeline:
            print(f"  {t[0][:19]} - {t[1][:50]}")
    
    elif sys.argv[1] == "cycle":
        if len(sys.argv) > 2 and sys.argv[2] == "start":
            time_system.start_time_cycle(sys.argv[3] if len(sys.argv) > 3 else "cycle")
            print(f"⏰ Started cycle: {sys.argv[3] if len(sys.argv) > 3 else 'cycle'}")
        elif len(sys.argv) > 2 and sys.argv[2] == "end":
            time_system.end_time_cycle(sys.argv[3] if len(sys.argv) > 3 else "cycle")
            print(f"🏁 Ended cycle: {sys.argv[3] if len(sys.argv) > 3 else 'cycle'}")
    
    time_system.close()
