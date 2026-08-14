#!/usr/bin/env python3
"""
Smart Web Validator with Confidence-Based Prioritization
Validates low-confidence facts first, high-confidence less often
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import random

class SmartValidator:
    def __init__(self):
        self.init_db()
        self.weight_config = {
            "validate_threshold": 80,      # Only validate if confidence below this
            "revalidate_days": 7,           # Revalidate every 7 days
            "priority_freshness": 3,        # Check fresh facts more often
            "low_confidence_range": (0, 50),    # Validate immediately
            "medium_confidence_range": (51, 70), # Validate soon
            "high_confidence_range": (71, 100)   # Validate rarely
        }
    
    def init_db(self):
        self.conn = sqlite3.connect("forge_data.db")
        self.cursor = self.conn.cursor()
        
        # Validation queue table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS validation_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_id TEXT,
                fact_content TEXT,
                current_confidence REAL,
                priority_score REAL,
                last_validated TIMESTAMP,
                validation_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Validation results
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS validation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_id TEXT,
                validated_at TIMESTAMP,
                confidence_before REAL,
                confidence_after REAL,
                sources_found INTEGER,
                success INTEGER
            )
        ''')
        self.conn.commit()
    
    def calculate_priority(self, confidence, last_validated_days):
        """Calculate priority score - lower confidence = higher priority"""
        if confidence < 50:
            priority = 100 - confidence  # Very high priority (50-100)
        elif confidence < 70:
            priority = 60 - confidence   # Medium priority (0-10)
        else:
            priority = 30 - confidence   # Low priority (negative, rarely check)
        
        # Age factor - older facts get priority boost
        age_boost = min(last_validated_days * 2, 20)
        
        return max(0, priority + age_boost)
    
    def add_to_queue(self, fact_id, fact_content, current_confidence):
        """Add a fact to validation queue with priority score"""
        last_validated = datetime.now().isoformat()
        
        # Calculate priority
        priority = self.calculate_priority(current_confidence, 0)
        
        self.cursor.execute('''
            INSERT OR REPLACE INTO validation_queue 
            (fact_id, fact_content, current_confidence, priority_score, last_validated, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (fact_id, fact_content, current_confidence, priority, last_validated, 'pending'))
        self.conn.commit()
        
        return priority
    
    def get_next_to_validate(self, limit=5):
        """Get highest priority facts to validate"""
        self.cursor.execute('''
            SELECT id, fact_id, fact_content, current_confidence, priority_score, last_validated
            FROM validation_queue 
            WHERE status = 'pending'
            ORDER BY priority_score DESC, current_confidence ASC
            LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
    
    def should_validate(self, confidence, last_validated_days):
        """Determine if a fact should be validated"""
        # Low confidence (<50): always validate
        if confidence < 50:
            return True, "low_confidence"
        
        # Medium confidence (50-70): validate if older than 3 days
        if confidence < 70 and last_validated_days > 3:
            return True, "medium_confidence_stale"
        
        # High confidence (>70): validate if older than 7 days
        if confidence >= 70 and last_validated_days > 7:
            return True, "high_confidence_stale"
        
        # Random chance for very old facts
        if last_validated_days > 14 and random.random() < 0.3:
            return True, "random_refresh"
        
        return False, None
    
    def update_validation_result(self, fact_id, success, new_confidence, sources_found):
        """Update validation results"""
        self.cursor.execute('''
            INSERT INTO validation_results 
            (fact_id, validated_at, confidence_before, confidence_after, sources_found, success)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (fact_id, datetime.now().isoformat(), 
              self.get_current_confidence(fact_id), new_confidence, sources_found, 1 if success else 0))
        self.conn.commit()
        
        # Update queue
        self.cursor.execute('''
            UPDATE validation_queue 
            SET current_confidence = ?, 
                last_validated = ?,
                validation_count = validation_count + 1,
                priority_score = ?,
                status = 'pending'
            WHERE fact_id = ?
        ''', (new_confidence, datetime.now().isoformat(), 
              self.calculate_priority(new_confidence, 0), fact_id))
        self.conn.commit()
    
    def get_current_confidence(self, fact_id):
        """Get current confidence for a fact"""
        self.cursor.execute('SELECT current_confidence FROM validation_queue WHERE fact_id = ?', (fact_id,))
        row = self.cursor.fetchone()
        return row[0] if row else 0
    
    def get_statistics(self):
        """Get validation statistics"""
        self.cursor.execute('SELECT COUNT(*) FROM validation_queue')
        total = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT AVG(current_confidence) FROM validation_queue')
        avg_confidence = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute('''
            SELECT 
                SUM(CASE WHEN current_confidence < 50 THEN 1 ELSE 0 END) as low,
                SUM(CASE WHEN current_confidence BETWEEN 50 AND 70 THEN 1 ELSE 0 END) as medium,
                SUM(CASE WHEN current_confidence > 70 THEN 1 ELSE 0 END) as high
            FROM validation_queue
        ''')
        counts = self.cursor.fetchone()
        
        return {
            "total_facts": total,
            "avg_confidence": avg_confidence,
            "low_confidence": counts[0] or 0,
            "medium_confidence": counts[1] or 0,
            "high_confidence": counts[2] or 0
        }
    
    def close(self):
        self.conn.close()

# Integration with Data Cube
class DataCubeValidator:
    def __init__(self):
        self.validator = SmartValidator()
    
    def scan_datacube(self):
        """Scan Data Cube for facts to validate"""
        cube_file = Path("datacube.jsonl")
        if not cube_file.exists():
            return
        
        with open(cube_file, 'r') as f:
            for line in f:
                data = json.loads(line)
                fact_id = data.get('hash', '')[:16]
                fact_content = json.dumps(data.get('data', {}))
                
                # Check if already in queue
                self.validator.cursor.execute(
                    'SELECT id FROM validation_queue WHERE fact_id = ?', (fact_id,)
                )
                if not self.validator.cursor.fetchone():
                    # Add with default confidence (assume high initially)
                    self.validator.add_to_queue(fact_id, fact_content, 85)
        
        print("✅ Data Cube facts added to validation queue")

if __name__ == "__main__":
    import sys
    
    smart = SmartValidator()
    
    if len(sys.argv) < 2:
        print("Smart Validator Commands:")
        print("  add <fact_id> <content> <confidence> - Add fact")
        print("  next                                 - Get next to validate")
        print("  stats                                - Show statistics")
        print("  scan                                 - Scan Data Cube")
    
    elif sys.argv[1] == "add":
        fact_id = sys.argv[2]
        content = sys.argv[3]
        confidence = float(sys.argv[4]) if len(sys.argv) > 4 else 50
        priority = smart.add_to_queue(fact_id, content, confidence)
        print(f"✅ Added fact {fact_id} with priority {priority:.2f}")
    
    elif sys.argv[1] == "next":
        next_facts = smart.get_next_to_validate()
        print(f"\n📋 Next to validate ({len(next_facts)}):")
        for fact in next_facts:
            print(f"   [{fact[3]:.0f}% confidence] {fact[2][:60]}...")
            print(f"   Priority: {fact[4]:.2f}")
            print()
    
    elif sys.argv[1] == "stats":
        stats = smart.get_statistics()
        print(f"\n📊 Validation Statistics:")
        print(f"   Total facts: {stats['total_facts']}")
        print(f"   Avg confidence: {stats['avg_confidence']:.1f}%")
        print(f"   Low confidence (<50%): {stats['low_confidence']}")
        print(f"   Medium confidence (50-70%): {stats['medium_confidence']}")
        print(f"   High confidence (>70%): {stats['high_confidence']}")
    
    elif sys.argv[1] == "scan":
        scanner = DataCubeValidator()
        scanner.scan_datacube()
    
    smart.close()
