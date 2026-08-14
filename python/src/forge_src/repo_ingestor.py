#!/usr/bin/env python3
"""
Repository Ingestor for Explorer-d334
Simplified version without heavy dependencies
"""

import os
import json
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime

class RepoIngestor:
    def __init__(self):
        self.repos_dir = Path.home() / "repos"
        self.ingested_db = Path("forge_data.db")
        self.init_db()
    
    def init_db(self):
        self.conn = sqlite3.connect(str(self.ingested_db))
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingested_repos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_name TEXT UNIQUE,
                repo_path TEXT,
                description TEXT,
                tags TEXT,
                status TEXT,
                last_ingested TIMESTAMP,
                hash TEXT
            )
        ''')
        self.conn.commit()
    
    def scan_repos(self):
        """Scan for all repos in your directory"""
        repos = []
        if self.repos_dir.exists():
            for repo_dir in self.repos_dir.iterdir():
                if repo_dir.is_dir() and (repo_dir / ".git").exists():
                    repos.append(repo_dir)
        return repos
    
    def extract_description(self, content):
        """Extract first paragraph as description"""
        lines = content.split('\n')
        for line in lines[:20]:
            if line.strip() and not line.startswith('#'):
                return line.strip()[:200]
        return "No description"
    
    def extract_tags(self, content):
        """Extract tags from content"""
        tags = []
        content_lower = content.lower()
        if "emergence" in content_lower:
            tags.append("emergence")
        if "simulation" in content_lower:
            tags.append("simulation")
        if "ai" in content_lower or "llm" in content_lower:
            tags.append("ai")
        if "security" in content_lower:
            tags.append("security")
        return tags
    
    def ingest_repo(self, repo_path):
        """Ingest a single repository"""
        readme_path = repo_path / "README.md"
        if not readme_path.exists():
            return False
        
        try:
            with open(readme_path, 'r') as f:
                content = f.read()
            
            description = self.extract_description(content)
            tags = self.extract_tags(content)
            
            repo_hash = hashlib.md5(str(repo_path).encode()).hexdigest()
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO ingested_repos 
                (repo_name, repo_path, description, tags, status, last_ingested, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                repo_path.name,
                str(repo_path),
                description,
                json.dumps(tags),
                'active',
                datetime.now().isoformat(),
                repo_hash
            ))
            self.conn.commit()
            print(f"  ✅ Ingested: {repo_path.name}")
            return True
        except Exception as e:
            print(f"  ❌ Error ingesting {repo_path.name}: {e}")
            return False
    
    def ingest_all(self):
        """Ingest all repositories"""
        repos = self.scan_repos()
        print(f"📚 Found {len(repos)} repositories")
        
        for repo in repos:
            self.ingest_repo(repo)
        
        print(f"✅ Ingested {len(repos)} repositories")
        return len(repos)
    
    def list_ingested(self):
        """List all ingested repos"""
        self.cursor.execute('''
            SELECT repo_name, description, status, last_ingested 
            FROM ingested_repos 
            ORDER BY last_ingested DESC
        ''')
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    import sys
    ingestor = RepoIngestor()
    
    if len(sys.argv) < 2:
        print("Repo Ingestor Commands:")
        print("  scan   - Scan and ingest all repos")
        print("  list   - List ingested repos")
    elif sys.argv[1] == "scan":
        ingestor.ingest_all()
    elif sys.argv[1] == "list":
        repos = ingestor.list_ingested()
        for repo in repos:
            print(f"  📁 {repo[0]} - {repo[1][:50]}... ({repo[2]})")
    
    ingestor.close()
