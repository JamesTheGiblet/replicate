#!/usr/bin/env python3
"""
Daily Memory with Six Lens Integration - Fixed Cube Matching
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
import sys
import os
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.six_lens_classifier import SixLensClassifier

class DailyMemoryLens:
    def __init__(self):
        self.classifier = SixLensClassifier()
        self.init_db()
    
    def init_db(self):
        self.conn = sqlite3.connect("forge_data.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lens_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lens TEXT,
                content TEXT,
                confidence REAL,
                timestamp TIMESTAMP,
                source TEXT,
                cube_id TEXT
            )
        ''')
        self.conn.commit()
    
    def find_or_create_cube(self, content, lens):
        """Find existing cube or create new one based on content similarity"""
        # Extract core topic (first meaningful words)
        words = content.lower().split()
        stopwords = {'the', 'a', 'an', 'and', 'of', 'to', 'in', 'for', 'on', 'with', 'by', 'is', 'are', 'was', 'were'}
        core_words = [w for w in words[:10] if w not in stopwords and len(w) > 3]
        
        if not core_words:
            core_words = words[:3]
        
        topic_sig = ' '.join(core_words[:5])
        
        # Check if there's an existing cube with similar topic
        self.cursor.execute('''
            SELECT cube_id, content FROM lens_interactions 
            WHERE cube_id IN (
                SELECT cube_id FROM lens_interactions 
                GROUP BY cube_id 
                ORDER BY COUNT(*) DESC
            )
        ''')
        
        existing_cubes = self.cursor.fetchall()
        
        for cube_id, cube_content in existing_cubes:
            # Check if topic signature appears in cube content
            if topic_sig.lower() in cube_content.lower() or cube_content.lower() in topic_sig.lower():
                return cube_id
        
        # Create new cube
        new_cube_id = hashlib.md5(topic_sig.encode()).hexdigest()[:8]
        return new_cube_id
    
    def record(self, content, source="user"):
        lens, confidence = self.classifier.classify(content)
        cube_id = self.find_or_create_cube(content, lens)
        
        self.cursor.execute('''
            INSERT INTO lens_interactions (lens, content, confidence, timestamp, source, cube_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (lens, content, confidence, datetime.now().isoformat(), source, cube_id))
        self.conn.commit()
        
        icon = self.classifier.get_lens_icon(lens)
        print(f"{icon} [{lens}] added to cube {cube_id}: {content[:60]}... (conf: {confidence})")
        return lens, confidence, cube_id
    
    def get_cube_status(self, cube_id):
        self.cursor.execute('SELECT lens, content, confidence, timestamp FROM lens_interactions WHERE cube_id = ?', (cube_id,))
        entries = [{"lens": row[0], "content": row[1], "confidence": row[2], "timestamp": row[3]} for row in self.cursor.fetchall()]
        
        # Count unique lenses
        unique_lenses = set(e['lens'] for e in entries)
        filled = len(unique_lenses)
        completeness = (filled / 6) * 100
        avg_confidence = sum(e['confidence'] for e in entries) / max(len(entries), 1)
        integrity = (completeness * 0.4) + (avg_confidence * 0.6)
        
        if integrity >= 90: grade = "CRYSTALLINE"
        elif integrity >= 65: grade = "COHERENT"
        elif integrity >= 35: grade = "FORMING"
        else: grade = "SPARSE"
        
        # Group by lens to show each once
        lens_map = {}
        for e in entries:
            if e['lens'] not in lens_map:
                lens_map[e['lens']] = e['content']
        
        return {
            "cube_id": cube_id,
            "filled_faces": filled,
            "missing_faces": 6 - filled,
            "integrity": integrity,
            "grade": grade,
            "entries": [{"lens": k, "content": v[:60]} for k, v in lens_map.items()]
        }
    
    def show_all_cubes(self):
        self.cursor.execute('SELECT DISTINCT cube_id FROM lens_interactions')
        cubes = self.cursor.fetchall()
        
        print("\n" + "="*60)
        print("📦 DATA CUBES (Six Lenses)")
        print("="*60)
        
        for cube in cubes:
            status = self.get_cube_status(cube[0])
            
            # Determine icon based on completeness
            if status['filled_faces'] == 6:
                icon = "💎"
            elif status['filled_faces'] >= 4:
                icon = "🔷"
            elif status['filled_faces'] >= 2:
                icon = "🔶"
            else:
                icon = "🔸"
            
            print(f"\n{icon} Cube: {status['cube_id']}")
            print(f"   Integrity: {status['integrity']:.1f}% ({status['grade']})")
            print(f"   Filled: {status['filled_faces']}/6 faces")
            
            # Show which lenses are filled
            lenses_filled = [e['lens'] for e in status['entries']]
            print(f"   Lenses: {', '.join(lenses_filled) if lenses_filled else 'none'}")
            
            # Show missing lenses
            all_lenses = {"FACT", "COUNTER", "OPINION", "FICTION", "CONTEXT", "UNKNOWN"}
            missing = all_lenses - set(lenses_filled)
            if missing:
                print(f"   Missing: {', '.join(missing)}")
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    dm = DailyMemoryLens()
    if len(sys.argv) < 2:
        dm.show_all_cubes()
    elif sys.argv[1] == "add":
        content = " ".join(sys.argv[2:])
        dm.record(content)
    elif sys.argv[1] == "cube":
        cube_id = sys.argv[2]
        status = dm.get_cube_status(cube_id)
        print(f"\n📦 Cube: {cube_id}")
        print(f"   Integrity: {status['integrity']:.1f}% ({status['grade']})")
        print(f"   Filled: {status['filled_faces']}/6")
        for e in status['entries']:
            icon = dm.classifier.get_lens_icon(e['lens'])
            print(f"   {icon} {e['lens']}: {e['content'][:60]}...")
    dm.close()
