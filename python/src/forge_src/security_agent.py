#!/usr/bin/env python3
"""
Security & Quality Agent for Explorer-d334
"""

import os
import re
import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path

class SecurityAgent:
    def __init__(self):
        self.forge_dir = Path.cwd()
        self.src_dir = self.forge_dir / "src"
        self.quarantine_dir = self.forge_dir / ".quarantine"
        self.quarantine_dir.mkdir(exist_ok=True)
        
        self.db_path = self.forge_dir / "forge_data.db"
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        self.init_tables()
        self.issues = []
    
    def init_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                issue_type TEXT,
                severity TEXT,
                line_number INTEGER,
                description TEXT,
                found_at TIMESTAMP,
                status TEXT DEFAULT 'open',
                hash TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS quarantine_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                reason TEXT,
                quarantined_at TIMESTAMP,
                original_hash TEXT,
                restored INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()
    
    def scan_for_malicious_patterns(self):
        patterns = [
            (r'os\.system\(', "System command execution", "high"),
            (r'eval\(', "Eval execution", "critical"),
            (r'exec\(', "Exec execution", "critical"),
            (r'rm\s+-rf', "Destructive file operation", "critical"),
        ]
        
        for py_file in self.src_dir.glob("*.py"):
            with open(py_file, 'r') as f:
                lines = f.readlines()
            
            for pattern, desc, severity in patterns:
                for i, line in enumerate(lines):
                    if re.search(pattern, line, re.IGNORECASE):
                        self.add_issue(str(py_file), "malicious", severity, i+1, f"{desc}: {line.strip()[:100]}")
    
    def scan_for_bugs(self):
        patterns = [
            (r'except:', "Bare exception handler", "medium"),
            (r'=\s*=\s*=', "Assignment in condition", "high"),
        ]
        
        for py_file in self.src_dir.glob("*.py"):
            with open(py_file, 'r') as f:
                lines = f.readlines()
            
            for pattern, desc, severity in patterns:
                for i, line in enumerate(lines):
                    if re.search(pattern, line):
                        self.add_issue(str(py_file), "bug", severity, i+1, f"{desc}: {line.strip()[:100]}")
    
    def scan_documentation_quality(self):
        doc_files = ["README.md", "FORGE_COMPLETE.md", "FORGE_COMPLETE_GUIDE.md"]
        
        for doc_file in doc_files:
            file_path = self.forge_dir / doc_file
            if not file_path.exists():
                self.add_issue(doc_file, "documentation", "medium", 0, f"Missing documentation file: {doc_file}")
                continue
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            required_sections = ["Quick Start", "Commands", "Architecture"]
            for section in required_sections:
                if section.lower() not in content.lower():
                    self.add_issue(doc_file, "documentation", "medium", 0, f"Missing section: '{section}'")
    
    def add_issue(self, file_path, issue_type, severity, line_number, description):
        issue_hash = hashlib.md5(f"{file_path}{description}".encode()).hexdigest()[:16]
        
        self.cursor.execute('''
            SELECT id FROM security_issues 
            WHERE file_path = ? AND description = ? AND status = 'open'
        ''', (file_path, description))
        
        if not self.cursor.fetchone():
            self.cursor.execute('''
                INSERT INTO security_issues (file_path, issue_type, severity, line_number, description, found_at, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (file_path, issue_type, severity, line_number, description, datetime.now().isoformat(), issue_hash))
            self.conn.commit()
            self.issues.append({"file": file_path, "type": issue_type, "severity": severity, "desc": description})
    
    def full_scan(self):
        print("\n" + "="*60)
        print("🔒 SECURITY & QUALITY AGENT SCAN")
        print("="*60)
        
        print("\n🔍 Scanning for malicious patterns...")
        self.scan_for_malicious_patterns()
        
        print("🐛 Scanning for bugs...")
        self.scan_for_bugs()
        
        print("📚 Scanning documentation quality...")
        self.scan_documentation_quality()
        
        print("\n" + "="*60)
        print("📊 SCAN RESULTS")
        print("="*60)
        
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for issue in self.issues:
            severity = issue.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        print(f"\n⚠️ Critical: {severity_counts.get('critical', 0)}")
        print(f"🔴 High: {severity_counts.get('high', 0)}")
        print(f"🟡 Medium: {severity_counts.get('medium', 0)}")
        print(f"🔵 Low: {severity_counts.get('low', 0)}")
        
        if self.issues:
            print("\n📋 ISSUES FOUND:")
            for issue in self.issues[:10]:
                print(f"   • {issue['file']} - {issue['type']}: {issue['desc'][:80]}")
        else:
            print("\n✅ No issues found! Codebase is clean.")
        
        print("\n" + "="*60)
        self.generate_report()
        return self.issues
    
    def generate_report(self):
        report_path = self.forge_dir / "security_report.txt"
        with open(report_path, 'w') as f:
            f.write("="*60 + "\n")
            f.write("SECURITY & QUALITY REPORT\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("="*60 + "\n\n")
            
            for issue in self.issues:
                f.write(f"[{issue['severity'].upper()}] {issue['file']}\n")
                f.write(f"   Type: {issue['type']}\n")
                f.write(f"   Issue: {issue['desc']}\n")
                f.write("-"*40 + "\n")
        
        print(f"\n📄 Full report saved to: {report_path}")
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    agent = SecurityAgent()
    agent.full_scan()
    agent.close()
