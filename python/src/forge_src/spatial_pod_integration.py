#!/usr/bin/env python3
"""
SpatialPod Integration for Explorer-d334
"""

import json
import hashlib
import math
import sqlite3
from datetime import datetime
from pathlib import Path

class SpatialPodIntegration:
    def __init__(self):
        self.conn = sqlite3.connect("forge_data.db")
        self.cursor = self.conn.cursor()
        self.ensure_spatial_tables()
    
    def ensure_spatial_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS spatial_pods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pod_id TEXT UNIQUE,
                cube_id TEXT,
                center_x REAL,
                center_y REAL,
                radius REAL,
                energy REAL DEFAULT 100,
                created_at TIMESTAMP,
                boundary_points TEXT
            )
        ''')
        self.conn.commit()
    
    def cube_to_pod(self, cube_id):
        """Convert a cube to a spatial pod"""
        self.cursor.execute('SELECT COUNT(*) FROM lens_interactions WHERE cube_id = ?', (cube_id,))
        count = self.cursor.fetchone()[0]
        
        # Simple pod creation
        hash_val = sum(ord(c) for c in cube_id) % 1000
        center_x = 200 + (hash_val % 600)
        center_y = 200 + ((hash_val * 7) % 400)
        radius = 50 + (count * 10)
        energy = 50 + (count * 5)
        
        self.cursor.execute('''
            INSERT OR REPLACE INTO spatial_pods 
            (pod_id, cube_id, center_x, center_y, radius, energy, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (cube_id, cube_id, center_x, center_y, radius, energy, datetime.now().isoformat()))
        self.conn.commit()
        
        return {
            "pod_id": cube_id,
            "cube_id": cube_id,
            "center_x": center_x,
            "center_y": center_y,
            "radius": radius,
            "energy": energy
        }
    
    def update_all_pods(self):
        """Update all pods from cubes"""
        self.cursor.execute('SELECT DISTINCT cube_id FROM lens_interactions')
        cubes = self.cursor.fetchall()
        pods = []
        for cube in cubes:
            pod = self.cube_to_pod(cube[0])
            pods.append(pod)
        return pods
    
    def log_pod_to_datacube(self, pod_data):
        """Log pod creation to data cube"""
        try:
            cube_file = Path("datacube.jsonl")
            fact = {
                "type": "spatial_pod",
                "pod_id": pod_data.get('pod_id'),
                "cube_id": pod_data.get('cube_id'),
                "energy": pod_data.get('energy'),
                "radius": pod_data.get('radius'),
                "timestamp": datetime.now().isoformat(),
                "hash": hashlib.md5(str(pod_data).encode()).hexdigest()[:16]
            }
            with open(cube_file, 'a') as f:
                f.write(json.dumps(fact) + '\n')
            return True
        except Exception as e:
            print(f"Data cube error: {e}")
            return False
    
    def create_pod_with_logging(self, cube_id):
        pod = self.cube_to_pod(cube_id)
        if pod:
            self.log_pod_to_datacube(pod)
        return pod
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    spi = SpatialPodIntegration()
    print("Testing SpatialPodIntegration...")
    pods = spi.update_all_pods()
    print(f"Created {len(pods)} pods")
    spi.close()
