#!/usr/bin/env python3
"""
Privacy-First Telemetry for Explorer-d334
100% opt-in, no data collected without permission
"""

import json
import platform
import subprocess
import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib

class PrivacyTelemetry:
    def __init__(self):
        self.forge_dir = Path.cwd()
        self.db_path = self.forge_dir / "analytics" / "telemetry.db"
        self.analytics_dir = self.forge_dir / "analytics"
        self.analytics_dir.mkdir(exist_ok=True)
        
        self.opt_in_file = self.analytics_dir / ".opt_in"
        self.opt_out_file = self.analytics_dir / ".opt_out"
        
        self.init_db()
    
    def init_db(self):
        """Initialize telemetry database"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                timestamp TIMESTAMP,
                data TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration INTEGER,
                commands_used TEXT
            )
        ''')
        
        self.conn.commit()
    
    def is_opted_in(self):
        """Check if user has opted in to telemetry"""
        if self.opt_in_file.exists():
            return True
        if self.opt_out_file.exists():
            return False
        # Default: no telemetry (privacy first)
        return False
    
    def opt_in(self):
        """User opts in to telemetry"""
        with open(self.opt_in_file, 'w') as f:
            f.write(f"Opted in at: {datetime.now().isoformat()}\n")
            f.write("Only anonymous usage data is collected.\n")
            f.write("No personal information ever leaves your device.\n")
        if self.opt_out_file.exists():
            self.opt_out_file.unlink()
        print("✅ Telemetry enabled. Thank you for helping improve Explorer-d334!")
        print("   Only anonymous usage data is collected. Opt out anytime with 'forge telemetry-off'")
    
    def opt_out(self):
        """User opts out of telemetry"""
        with open(self.opt_out_file, 'w') as f:
            f.write(f"Opted out at: {datetime.now().isoformat()}\n")
        if self.opt_in_file.exists():
            self.opt_in_file.unlink()
        print("✅ Telemetry disabled. No data will be collected.")
    
    def get_anonymous_id(self):
        """Generate anonymous device ID (cannot be traced back)"""
        if not self.is_opted_in():
            return None
        
        # Create a salted hash of machine ID (one-way, cannot reverse)
        try:
            import uuid
            machine_id = str(uuid.getnode())
            salt = "explorer-d334-salt-2026"
            anonymous_id = hashlib.sha256(f"{machine_id}{salt}".encode()).hexdigest()[:16]
            return anonymous_id
        except:
            return "unknown"
    
    def track_event(self, event_type, data=None):
        """Track an anonymous event (only if opted in)"""
        if not self.is_opted_in():
            return
        
        event_data = {
            "event": event_type,
            "timestamp": datetime.now().isoformat(),
            "anonymous_id": self.get_anonymous_id(),
            "data": data or {}
        }
        
        self.cursor.execute('''
            INSERT INTO events (event_type, timestamp, data)
            VALUES (?, ?, ?)
        ''', (event_type, datetime.now().isoformat(), json.dumps(event_data)))
        self.conn.commit()
    
    def track_command(self, command):
        """Track a command execution"""
        if not self.is_opted_in():
            return
        
        self.cursor.execute('''
            INSERT INTO events (event_type, timestamp, data)
            VALUES (?, ?, ?)
        ''', ("command", datetime.now().isoformat(), json.dumps({"command": command})))
        self.conn.commit()
    
    def track_session_start(self):
        """Track session start"""
        if not self.is_opted_in():
            return
        
        import uuid
        session_id = str(uuid.uuid4())[:8]
        self.cursor.execute('''
            INSERT INTO sessions (session_id, start_time, commands_used)
            VALUES (?, ?, ?)
        ''', (session_id, datetime.now().isoformat(), ""))
        self.conn.commit()
        return session_id
    
    def track_session_end(self, session_id, commands):
        """Track session end"""
        if not self.is_opted_in():
            return
        
        self.cursor.execute('''
            UPDATE sessions 
            SET end_time = ?, duration = julianday(?) - julianday(start_time), commands_used = ?
            WHERE session_id = ?
        ''', (datetime.now().isoformat(), datetime.now().isoformat(), ",".join(commands), session_id))
        self.conn.commit()
    
    def get_stats(self):
        """Get anonymous statistics (for local viewing only)"""
        if not self.is_opted_in():
            return {"error": "Telemetry not enabled. Run 'forge telemetry-on' to opt in."}
        
        self.cursor.execute('SELECT COUNT(*) FROM events')
        total_events = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(DISTINCT session_id) FROM sessions')
        total_sessions = self.cursor.fetchone()[0]
        
        self.cursor.execute('''
            SELECT event_type, COUNT(*) FROM events 
            GROUP BY event_type 
            ORDER BY COUNT(*) DESC
        ''')
        top_events = self.cursor.fetchall()
        
        return {
            "total_events": total_events,
            "total_sessions": total_sessions,
            "top_events": [{"event": e[0], "count": e[1]} for e in top_events[:10]]
        }
    
    def export_anonymized(self):
        """Export anonymized data (for debugging, no personal info)"""
        if not self.is_opted_in():
            return None
        
        export = {
            "export_date": datetime.now().isoformat(),
            "total_events": self.cursor.execute('SELECT COUNT(*) FROM events').fetchone()[0],
            "events": []
        }
        
        self.cursor.execute('SELECT timestamp, event_type, data FROM events LIMIT 100')
        for row in self.cursor.fetchall():
            export["events"].append({
                "timestamp": row[0],
                "event_type": row[1],
                "data": json.loads(row[2]) if row[2] else {}
            })
        
        export_file = self.analytics_dir / f"export_{datetime.now().strftime('%Y%m%d')}.json"
        with open(export_file, 'w') as f:
            json.dump(export, f, indent=2)
        
        return export_file
    
    def close(self):
        self.conn.close()

# Crash reporting system
class CrashReporter:
    def __init__(self):
        self.forge_dir = Path.cwd()
        self.crash_dir = self.forge_dir / "analytics" / "crashes"
        self.crash_dir.mkdir(parents=True, exist_ok=True)
    
    def report_crash(self, error_message, context=None):
        """Report a crash (local only, user can choose to send)"""
        crash_id = hashlib.md5(f"{datetime.now().isoformat()}{error_message}".encode()).hexdigest()[:8]
        crash_file = self.crash_dir / f"crash_{crash_id}.json"
        
        crash_data = {
            "crash_id": crash_id,
            "timestamp": datetime.now().isoformat(),
            "error": str(error_message),
            "context": context or {},
            "reported": False
        }
        
        with open(crash_file, 'w') as f:
            json.dump(crash_data, f, indent=2)
        
        return crash_id
    
    def list_crashes(self):
        """List local crashes"""
        crashes = []
        for crash_file in self.crash_dir.glob("*.json"):
            with open(crash_file, 'r') as f:
                crashes.append(json.load(f))
        return crashes

if __name__ == "__main__":
    telemetry = PrivacyTelemetry()
    
    print("=== TELEMETRY STATUS ===")
    print(f"Opted in: {telemetry.is_opted_in()}")
    print(f"Database: {telemetry.db_path}")
    
    if telemetry.is_opted_in():
        stats = telemetry.get_stats()
        print(f"\n📊 Local Statistics:")
        print(f"   Total events: {stats.get('total_events', 0)}")
        print(f"   Total sessions: {stats.get('total_sessions', 0)}")
    
    telemetry.close()
