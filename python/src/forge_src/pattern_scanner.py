#!/usr/bin/env python3
"""
Pattern Scanner for Explorer-d334
Analyzes ingested repos for recurring patterns
"""

import sqlite3
import json
from collections import Counter

class PatternScanner:
    def __init__(self):
        self.conn = sqlite3.connect("forge_data.db")
        self.cursor = self.conn.cursor()
    
    def scan_patterns(self):
        """Scan all ingested repos for patterns"""
        self.cursor.execute('SELECT repo_name, tags FROM ingested_repos')
        repos = self.cursor.fetchall()
        
        all_tags = []
        for repo in repos:
            tags = json.loads(repo[1]) if repo[1] else []
            all_tags.extend(tags)
        
        tag_counts = Counter(all_tags)
        
        print("\n🔍 RECURRING PATTERNS ACROSS YOUR REPOS\n")
        print("=" * 50)
        for tag, count in tag_counts.most_common(10):
            print(f"  {tag}: {count} repos")
        
        return tag_counts
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    scanner = PatternScanner()
    scanner.scan_patterns()
    scanner.close()
