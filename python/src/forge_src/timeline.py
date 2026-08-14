#!/usr/bin/env python3
"""
Timeline Intelligence for Explorer-d334
Based on Project-ChronoScribe architecture
"""

import sqlite3
from datetime import datetime
from pathlib import Path

class Timeline:
    def __init__(self):
        self.conn = sqlite3.connect("forge_data.db")
        self.cursor = self.conn.cursor()
        self.init_timeline()
    
    def init_timeline(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS timeline_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                event_type TEXT,
                entity_id TEXT,
                description TEXT,
                importance REAL
            )
        ''')
        self.conn.commit()
    
    def add_event(self, event_type, entity_id, description, importance=0.5):
        self.cursor.execute('''
            INSERT INTO timeline_events (timestamp, event_type, entity_id, description, importance)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), event_type, entity_id, description, importance))
        self.conn.commit()
    
    def get_timeline(self, start_date=None, end_date=None):
        query = "SELECT timestamp, event_type, description FROM timeline_events ORDER BY timestamp"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_era(self, year):
        start = f"{year}-01-01"
        end = f"{year}-12-31"
        self.cursor.execute('''
            SELECT timestamp, event_type, description FROM timeline_events 
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp
        ''', (start, end))
        return self.cursor.fetchall()
    
    def get_origin(self, topic):
        self.cursor.execute('''
            SELECT timestamp, description FROM timeline_events 
            WHERE description LIKE ? 
            ORDER BY timestamp ASC LIMIT 1
        ''', (f'%{topic}%',))
        return self.cursor.fetchone()

if __name__ == "__main__":
    tl = Timeline()
    tl.add_event("system", "explorer", "Explorer-d334 v2 launched", 1.0)
    print("✅ Timeline initialized")
