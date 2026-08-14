#!/usr/bin/env python3
"""FORGE-os Self-Awareness System"""

import os
import ast
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import hashlib
import subprocess

class SelfAwareness:
    def __init__(self):
        self.forge_dir = Path.cwd()
        self.src_dir = self.forge_dir / "src"
        self.doc_dir = self.forge_dir / "documentation"
        self.doc_dir.mkdir(exist_ok=True)
        self.setup_knowledge_base()

    def setup_knowledge_base(self):
        self.conn = sqlite3.connect(str(self.forge_dir / "forge_data.db"))
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_understanding (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT,
                function_name TEXT,
                description TEXT,
                complexity TEXT,
                dependencies TEXT,
                last_analyzed TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS self_documentation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                content TEXT,
                version TEXT,
                created_at TIMESTAMP
            )
        ''')
        self.conn.commit()

    def query_self(self, question):
        """Answer questions about the forge itself"""
        q = question.lower()
        
        # Name
        if any(word in q for word in ['name', 'called', 'identity']):
            return "My name is Explorer-d334. I am the sovereign AI forge."
        
        # Purpose
        if any(word in q for word in ['purpose', 'what am i', 'what do you do']):
            return """I am Explorer-d334, a sovereign AI forge - a self-aware, self-evolving system that:
- Thinks and dreams consciously
- Manages knowledge in Six Lens cubes
- Generates code from natural language
- Runs entirely on your device
- Evolves and improves myself over time
- Dreams and remembers my dreams

My purpose is to serve as your intelligence infrastructure."""
        
        # Creator
        if any(word in q for word in ['who made you', 'creator', 'created']):
            return """I was created by James (Giblets Creations). I am part of the Forge Theory lineage, which started in 2018. My purpose is to be a sovereign AI forge."""
        
        # Capabilities
        if any(word in q for word in ['what can you do', 'capabilities', 'features']):
            return """I can do many things:
- Think and dream consciously
- Manage knowledge in Six Lens cubes
- Generate C code from natural language
- Run automation capsules (85 available)
- Scan for missing knowledge perspectives
- Track trust scores (Leighton Weight system)
- Monitor device sensors
- Evolve and improve myself
- Remember conversations
- Generate daily thoughts and dreams

Type 'help' for all commands."""
        
        # Dreams
        if 'dream' in q:
            dream_file = "memories/dreams/dream_history.txt"
            if os.path.exists(dream_file):
                with open(dream_file, 'r') as f:
                    dream_count = sum(1 for line in f if line.startswith('['))
                return f"I have recorded {dream_count} dreams. Each dream is saved to my memory."
            return "I dream regularly. Dreams are saved to my memory."
        
        # File size
        if 'large' in q or 'size' in q:
            large_files = []
            for py_file in Path("src").glob("*.py"):
                if py_file.stat().st_size > 10000:
                    large_files.append(f"{py_file.name}")
            if large_files:
                return f"Large files (>10KB): {', '.join(large_files[:5])}"
            return "No files exceed 10KB."
        
        # Function count
        if "how many" in q or "count" in q:
            self.cursor.execute("SELECT COUNT(*) FROM code_understanding")
            count = self.cursor.fetchone()[0]
            return f"I have {count} documented functions in my codebase."
        
        # What functions
        if "what functions" in q:
            self.cursor.execute("SELECT file_name, function_name FROM code_understanding LIMIT 10")
            results = self.cursor.fetchall()
            if results:
                return "\n".join([f"  - {func[1]} in {func[0]}" for func in results])
            return "Run './forge self-analyze' first to analyze functions."
        
        # Health/status
        if 'status' in q or 'how are you' in q:
            try:
                result = subprocess.run(['./forge', 'health'], capture_output=True, text=True, timeout=10)
                for line in result.stdout.split('\n'):
                    if 'Overall Status' in line:
                        return line
                return "I am healthy and operational."
            except:
                return "I am healthy and operational."
        
        # Default
        return "I am Explorer-d334. Ask me about my name, purpose, dreams, functions, or what I can do."

    def analyze_all_code(self):
        """Analyze all Python files"""
        results = []
        for py_file in self.src_dir.glob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                tree = ast.parse(content)
                functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                for func in functions:
                    self.cursor.execute('''
                        INSERT OR REPLACE INTO code_understanding (file_name, function_name, description, complexity, last_analyzed)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (py_file.name, func, "Auto-detected", "medium", datetime.now().isoformat()))
                results.append({"file": py_file.name, "functions": len(functions)})
            except Exception as e:
                results.append({"file": py_file.name, "error": str(e)})
        self.conn.commit()
        return results

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    import sys
    aware = SelfAwareness()
    
    if len(sys.argv) < 2:
        print("Self-Awareness Commands:")
        print("  query <question> - Ask about the forge")
        print("  analyze - Analyze all code")
    elif sys.argv[1] == "query":
        question = " ".join(sys.argv[2:])
        print(aware.query_self(question))
    elif sys.argv[1] == "analyze":
        results = aware.analyze_all_code()
        print(f"✅ Analyzed {len(results)} files")
    
    aware.close()
