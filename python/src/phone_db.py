"""
Phone Database - SQLite + Replicant Ledger
Stores phone sensor data and integrates with Replicant's audit trail
"""

import sqlite3
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class PhoneDatabase:
    """SQLite database for phone sensor data"""
    
    def __init__(self, db_path: str = "phone_data.db"):
        self.db_path = Path(db_path)
        self.conn = None
        self.cursor = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time INTEGER,
                end_time INTEGER,
                agent_id TEXT,
                total_ticks INTEGER,
                total_entries INTEGER
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                tick INTEGER,
                timestamp REAL,
                x REAL,
                y REAL,
                altitude REAL,
                accuracy REAL,
                heading REAL,
                energy REAL,
                light REAL,
                pressure REAL,
                steps INTEGER,
                accel_x REAL,
                accel_y REAL,
                accel_z REAL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS world_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                tick INTEGER,
                event_type TEXT,
                claim_id TEXT,
                agent_id TEXT,
                lens TEXT,
                data TEXT,
                timestamp REAL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        ''')
        
        self.conn.commit()
        print(f"✅ Database initialized: {self.db_path}")
    
    def start_session(self, session_id: str, agent_id: str = "phone-001"):
        """Start a new session"""
        self.cursor.execute(
            "INSERT OR REPLACE INTO sessions (session_id, start_time, agent_id, total_ticks, total_entries) VALUES (?, ?, ?, 0, 0)",
            (session_id, int(time.time()), agent_id)
        )
        self.conn.commit()
        print(f"📊 Session started: {session_id}")
    
    def end_session(self, session_id: str, total_ticks: int, total_entries: int):
        """End a session"""
        self.cursor.execute(
            "UPDATE sessions SET end_time = ?, total_ticks = ?, total_entries = ? WHERE session_id = ?",
            (int(time.time()), total_ticks, total_entries, session_id)
        )
        self.conn.commit()
        print(f"📊 Session ended: {session_id} ({total_entries} entries)")
    
    def insert_reading(self, session_id: str, tick: int, data: Dict[str, Any]):
        """Insert a sensor reading"""
        self.cursor.execute('''
            INSERT INTO sensor_readings (
                session_id, tick, timestamp, x, y, altitude, accuracy,
                heading, energy, light, pressure, steps,
                accel_x, accel_y, accel_z
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            tick,
            data.get("timestamp", time.time()),
            data.get("x", 0),
            data.get("y", 0),
            data.get("altitude", 0),
            data.get("accuracy", 0),
            data.get("heading", 0),
            data.get("energy", 100),
            data.get("light", 0),
            data.get("pressure", 0),
            data.get("steps", 0),
            data.get("acceleration", [0,0,0])[0],
            data.get("acceleration", [0,0,0])[1],
            data.get("acceleration", [0,0,0])[2]
        ))
        self.conn.commit()
    
    def insert_world_event(self, session_id: str, tick: int, event: Dict[str, Any]):
        """Insert a world event (claim, attestation, etc.)"""
        self.cursor.execute('''
            INSERT INTO world_events (
                session_id, tick, event_type, claim_id, agent_id, lens, data, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            tick,
            event.get("type", "unknown"),
            event.get("claim_id", ""),
            event.get("agent_id", ""),
            event.get("lens", ""),
            json.dumps(event),
            time.time()
        ))
        self.conn.commit()
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        self.cursor.execute(
            "SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM sensor_readings WHERE session_id = ?",
            (session_id,)
        )
        count, start, end = self.cursor.fetchone()
        
        self.cursor.execute(
            "SELECT COUNT(*) FROM world_events WHERE session_id = ?",
            (session_id,)
        )
        events = self.cursor.fetchone()[0]
        
        return {
            "session_id": session_id,
            "readings": count or 0,
            "events": events or 0,
            "start": start,
            "end": end,
        }
    
    def export_to_json(self, session_id: str, output_file: str):
        """Export session data to JSON"""
        data = {
            "session_id": session_id,
            "readings": [],
            "events": []
        }
        
        self.cursor.execute("SELECT * FROM sensor_readings WHERE session_id = ?", (session_id,))
        columns = [description[0] for description in self.cursor.description]
        for row in self.cursor.fetchall():
            data["readings"].append(dict(zip(columns, row)))
        
        self.cursor.execute("SELECT * FROM world_events WHERE session_id = ?", (session_id,))
        columns = [description[0] for description in self.cursor.description]
        for row in self.cursor.fetchall():
            data["events"].append(dict(zip(columns, row)))
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"📊 Exported to: {output_file}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
