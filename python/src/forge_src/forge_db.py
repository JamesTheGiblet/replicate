#!/usr/bin/env python3
"""
FORGE-os Database Storage
Embedded SQLite database for storing SCPs, audit logs, and function results
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class ForgeDB:
    def __init__(self, db_path="forge_data.db"):
        self.db_path = Path(db_path)
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialize all database tables"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        # SCP Prompts table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS scp_prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                scp_type TEXT,
                params TEXT,
                logic TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                version INTEGER DEFAULT 1,
                hash TEXT
            )
        ''')
        
        # Generated Code table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS generated_code (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scp_name TEXT,
                code TEXT,
                compiled_size INTEGER,
                created_at TIMESTAMP,
                hash TEXT,
                FOREIGN KEY (scp_name) REFERENCES scp_prompts(name)
            )
        ''')
        
        # Execution Results table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS execution_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                function_name TEXT,
                input_value TEXT,
                output_value TEXT,
                execution_time REAL,
                timestamp TIMESTAMP,
                success BOOLEAN
            )
        ''')
        
        # Audit Log table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                entity_type TEXT,
                entity_name TEXT,
                details TEXT,
                timestamp TIMESTAMP,
                hash TEXT
            )
        ''')
        
        # Metrics table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                metric_value REAL,
                timestamp TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def save_scp(self, name: str, scp_data: Dict) -> bool:
        """Save or update an SCP prompt"""
        now = datetime.now()
        scp_json = json.dumps(scp_data)
        scp_hash = hashlib.sha256(scp_json.encode()).hexdigest()
        
        # Check if exists
        cursor = self.conn.execute(
            "SELECT id, version FROM scp_prompts WHERE name = ?", (name,)
        )
        existing = cursor.fetchone()
        
        if existing:
            # Update
            self.conn.execute('''
                UPDATE scp_prompts 
                SET scp_type = ?, params = ?, logic = ?, 
                    updated_at = ?, version = version + 1, hash = ?
                WHERE name = ?
            ''', (
                scp_data.get('type', 'function'),
                json.dumps(scp_data.get('params', [])),
                scp_data.get('logic', ''),
                now, scp_hash, name
            ))
        else:
            # Insert
            self.conn.execute('''
                INSERT INTO scp_prompts 
                (name, scp_type, params, logic, created_at, updated_at, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                name,
                scp_data.get('type', 'function'),
                json.dumps(scp_data.get('params', [])),
                scp_data.get('logic', ''),
                now, now, scp_hash
            ))
        
        self.conn.commit()
        self.audit("save", "scp", name, f"Saved version {existing[1]+1 if existing else 1}")
        return True
    
    def get_scp(self, name: str) -> Dict:
        """Retrieve an SCP prompt by name"""
        cursor = self.conn.execute(
            "SELECT * FROM scp_prompts WHERE name = ?", (name,)
        )
        row = cursor.fetchone()
        if row:
            return {
                'name': row['name'],
                'type': row['scp_type'],
                'params': json.loads(row['params']),
                'logic': row['logic'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'version': row['version']
            }
        return None
    
    def list_scps(self, limit=50) -> List[Dict]:
        """List all SCP prompts"""
        cursor = self.conn.execute(
            "SELECT name, scp_type, version, updated_at FROM scp_prompts ORDER BY updated_at DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def log_execution(self, function_name: str, input_val: Any, output_val: Any, 
                      exec_time: float, success: bool):
        """Log function execution results"""
        self.conn.execute('''
            INSERT INTO execution_results 
            (function_name, input_value, output_value, execution_time, timestamp, success)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (function_name, str(input_val), str(output_val), exec_time, 
              datetime.now(), success))
        self.conn.commit()
    
    def get_execution_stats(self, function_name: str = None) -> Dict:
        """Get execution statistics"""
        if function_name:
            cursor = self.conn.execute('''
                SELECT 
                    COUNT(*) as total_calls,
                    AVG(execution_time) as avg_time,
                    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes
                FROM execution_results 
                WHERE function_name = ?
            ''', (function_name,))
        else:
            cursor = self.conn.execute('''
                SELECT 
                    COUNT(*) as total_calls,
                    AVG(execution_time) as avg_time,
                    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successes
                FROM execution_results
            ''')
        
        row = cursor.fetchone()
        return dict(row) if row else {}
    
    def save_metric(self, name: str, value: float):
        """Save a metric value"""
        self.conn.execute(
            "INSERT INTO metrics (metric_name, metric_value, timestamp) VALUES (?, ?, ?)",
            (name, value, datetime.now())
        )
        self.conn.commit()
    
    def get_metrics(self, name: str, hours=24) -> List[Dict]:
        """Get recent metrics"""
        cursor = self.conn.execute('''
            SELECT metric_value, timestamp 
            FROM metrics 
            WHERE metric_name = ? 
            AND timestamp > datetime('now', ?)
            ORDER BY timestamp DESC
        ''', (name, f'-{hours} hours'))
        return [dict(row) for row in cursor.fetchall()]
    
    def audit(self, action: str, entity_type: str, entity_name: str, details: str):
        """Add audit log entry"""
        log_entry = f"{action}:{entity_type}:{entity_name}:{details}"
        log_hash = hashlib.sha256(log_entry.encode()).hexdigest()
        
        self.conn.execute('''
            INSERT INTO audit_log (action, entity_type, entity_name, details, timestamp, hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (action, entity_type, entity_name, details, datetime.now(), log_hash))
        self.conn.commit()
    
    def get_audit_trail(self, limit=100) -> List[Dict]:
        """Get audit trail"""
        cursor = self.conn.execute(
            "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def backup_database(self):
        """Create a backup of the database"""
        backup_path = f"forge_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_conn = sqlite3.connect(backup_path)
        self.conn.backup(backup_conn)
        backup_conn.close()
        print(f"✅ Database backed up to {backup_path}")
        return backup_path
    
    def close(self):
        if self.conn:
            self.conn.close()

# CLI Interface
if __name__ == "__main__":
    import sys
    
    db = ForgeDB()
    
    if len(sys.argv) < 2:
        print("ForgeDB Commands:")
        print("  list                    - List all SCPs")
        print("  get <name>              - Get SCP by name")
        print("  stats [function]        - Get execution stats")
        print("  audit [limit]           - Show audit trail")
        print("  metrics <name>          - Show metrics")
        print("  backup                  - Backup database")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        scps = db.list_scps()
        for scp in scps:
            print(f"  {scp['name']} (v{scp['version']}) - {scp['updated_at']}")
    
    elif cmd == "get" and len(sys.argv) > 2:
        scp = db.get_scp(sys.argv[2])
        if scp:
            print(json.dumps(scp, indent=2, default=str))
        else:
            print(f"SCP '{sys.argv[2]}' not found")
    
    elif cmd == "stats":
        func = sys.argv[2] if len(sys.argv) > 2 else None
        stats = db.get_execution_stats(func)
        print(json.dumps(stats, indent=2))
    
    elif cmd == "audit":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        entries = db.get_audit_trail(limit)
        for entry in entries:
            print(f"[{entry['timestamp']}] {entry['action']} {entry['entity_name']}")
    
    elif cmd == "metrics" and len(sys.argv) > 2:
        metrics = db.get_metrics(sys.argv[2])
        for m in metrics:
            print(f"  {m['timestamp']}: {m['metric_value']}")
    
    elif cmd == "backup":
        db.backup_database()
    
    db.close()
