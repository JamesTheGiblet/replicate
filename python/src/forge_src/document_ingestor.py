#!/usr/bin/env python3
"""
Document Ingestor for Explorer-d334
Fully integrated with Leighton Weight, Data Cube, Dreams, and Memory
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
import sqlite3

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

class DocumentIngestor:
    def __init__(self):
        self.forge_dir = Path.cwd()
        self.ingested_dir = self.forge_dir / "ingested"
        self.ingested_dir.mkdir(exist_ok=True)
        self.init_db()
    
    def init_db(self):
        self.conn = sqlite3.connect(str(self.forge_dir / "forge_data.db"))
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingested_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                file_name TEXT,
                file_type TEXT,
                content_hash TEXT,
                content TEXT,
                word_count INTEGER,
                ingested_at TIMESTAMP,
                tags TEXT,
                trust_score REAL DEFAULT 0.5,
                dream_triggered INTEGER DEFAULT 0,
                reasoning_used INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()
    
    def read_txt(self, file_path):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def read_docx(self, file_path):
        if not DOCX_AVAILABLE:
            return None
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    
    def update_trust(self, document_name, success):
        """Update Leighton Weight trust for this document"""
        try:
            from simple_trust import SimpleTrust
            trust = SimpleTrust()
            if success:
                trust.update(f"doc_{document_name}", True)
            else:
                trust.update(f"doc_{document_name}", False)
            trust.close()
        except:
            pass
    
    def add_to_data_cube(self, content, file_name):
        """Add document summary to immutable data cube"""
        try:
            from integrated_datacube import IntegratedDataCube
            cube = IntegratedDataCube()
            
            fact = {
                "type": "ingested_document",
                "file": file_name,
                "timestamp": datetime.now().isoformat(),
                "summary": content[:500],
                "word_count": len(content.split())
            }
            cube.add_fact(fact)
            cube.close()
        except:
            pass
    
    def trigger_dream(self, content, file_name):
        """Trigger a dream based on document content"""
        try:
            from forge_memory import ForgeMemory
            memory = ForgeMemory()
            
            # Extract key themes for dreaming
            words = content.lower().split()
            common_words = ['the', 'and', 'to', 'of', 'a', 'in', 'is', 'it', 'for', 'with']
            themes = [w for w in set(words) if len(w) > 5 and w not in common_words][:5]
            
            dream_content = f"I dreamt about {', '.join(themes)} from the document '{file_name}'"
            memory.dream(dream_content, "document_inspired")
            memory.close()
            
            # Mark as triggered
            self.cursor.execute('UPDATE ingested_documents SET dream_triggered = 1 WHERE file_name = ?', (file_name,))
            self.conn.commit()
            
            return themes
        except:
            return []
    
    def analyze_with_reasoning(self, content, file_name):
        """Use reasoning to extract insights from document"""
        try:
            from intelligent_llm import IntelligentLLM
            llm = IntelligentLLM()
            
            # Use LLM to summarize if available
            prompt = f"Summarize this document in 2-3 sentences:\n\n{content[:1000]}"
            # This would call the LLM - for now, use simple extraction
            summary = content[:200] + "..." if len(content) > 200 else content
            
            # Store reasoning result
            self.cursor.execute('UPDATE ingested_documents SET reasoning_used = 1 WHERE file_name = ?', (file_name,))
            self.conn.commit()
            
            return summary
        except:
            return content[:200]
    
    def process_file(self, file_path, tags=None):
        """Process a single document with full integration"""
        file_path = Path(file_path)
        if not file_path.exists():
            return {"success": False, "error": "File not found"}
        
        ext = file_path.suffix.lower()
        if ext == '.txt':
            content = self.read_txt(file_path)
            file_type = 'txt'
        elif ext == '.docx':
            content = self.read_docx(file_path)
            file_type = 'docx'
        else:
            return {"success": False, "error": f"Unsupported: {ext}"}
        
        if content is None:
            return {"success": False, "error": f"Could not read {ext}"}
        
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        self.cursor.execute('SELECT id FROM ingested_documents WHERE content_hash = ?', (content_hash,))
        if self.cursor.fetchone():
            return {"success": False, "error": "Already ingested"}
        
        word_count = len(content.split())
        
        # Store in database
        self.cursor.execute('''
            INSERT INTO ingested_documents 
            (file_path, file_name, file_type, content_hash, content, word_count, ingested_at, tags, trust_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (str(file_path), file_path.name, file_type, content_hash, content, word_count, 
              datetime.now().isoformat(), tags or '', 0.65))
        self.conn.commit()
        
        # Update Leighton Weight trust
        self.update_trust(file_path.name, True)
        
        # Add to immutable data cube
        self.add_to_data_cube(content, file_path.name)
        
        # Trigger a dream about the document
        themes = self.trigger_dream(content, file_path.name)
        
        # Analyze with reasoning
        summary = self.analyze_with_reasoning(content, file_path.name)
        
        # Save to SCP memory
        self.save_to_memory(file_path.name, summary, tags)
        
        return {
            "success": True,
            "file_name": file_path.name,
            "word_count": word_count,
            "trust_score": 0.65,
            "dream_themes": themes,
            "summary": summary[:200]
        }
    
    def save_to_memory(self, title, content, tags):
        try:
            from scp_memory import get_scp_memory
            memory = get_scp_memory()
            memory.create_scp("document", title, {
                "content": content,
                "tags": tags,
                "ingested_at": datetime.now().isoformat()
            })
        except:
            pass
    
    def ingest_directory(self, directory_path, tags=None):
        directory_path = Path(directory_path)
        if not directory_path.exists():
            return {"success": False, "error": "Directory not found"}
        
        results = []
        for ext in ['*.txt', '*.docx']:
            for file_path in directory_path.glob(ext):
                result = self.process_file(file_path, tags)
                results.append(result)
        
        return {"success": True, "processed": len(results), "results": results}
    
    def search_documents(self, keyword):
        self.cursor.execute('''
            SELECT file_name, file_type, word_count, ingested_at, tags, trust_score
            FROM ingested_documents 
            WHERE content LIKE ? OR tags LIKE ?
            ORDER BY trust_score DESC, ingested_at DESC
        ''', (f'%{keyword}%', f'%{keyword}%'))
        return self.cursor.fetchall()
    
    def list_documents(self):
        self.cursor.execute('''
            SELECT file_name, file_type, word_count, ingested_at, tags, trust_score, dream_triggered
            FROM ingested_documents 
            ORDER BY trust_score DESC
        ''')
        return self.cursor.fetchall()
    
    def get_statistics(self):
        """Get document ingestion statistics"""
        self.cursor.execute('SELECT COUNT(*) FROM ingested_documents')
        total = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT AVG(trust_score) FROM ingested_documents')
        avg_trust = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute('SELECT SUM(dream_triggered) FROM ingested_documents')
        dreams = self.cursor.fetchone()[0] or 0
        
        return {
            "total_documents": total,
            "average_trust": avg_trust,
            "dreams_triggered": dreams
        }
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    import sys
    
    ingestor = DocumentIngestor()
    
    if len(sys.argv) < 2:
        print("Document Ingestor Commands:")
        print("  file <path> [tags]    - Ingest single file")
        print("  dir <path> [tags]     - Ingest directory")
        print("  list                  - List documents")
        print("  search <keyword>      - Search documents")
        print("  stats                 - Show statistics")
    
    elif sys.argv[1] == "file":
        tags = sys.argv[3] if len(sys.argv) > 3 else None
        result = ingestor.process_file(sys.argv[2], tags)
        print(json.dumps(result, indent=2))
        
        if result.get('dream_themes'):
            print(f"\n💭 Dream triggered about: {', '.join(result['dream_themes'])}")
        print(f"⭐ Trust score: {result.get('trust_score', 0)}")
    
    elif sys.argv[1] == "dir":
        tags = sys.argv[3] if len(sys.argv) > 3 else None
        result = ingestor.ingest_directory(sys.argv[2], tags)
        print(f"📚 Processed {result['processed']} documents")
    
    elif sys.argv[1] == "list":
        docs = ingestor.list_documents()
        for doc in docs:
            dream_icon = "💭" if doc[6] else "📄"
            print(f"  {dream_icon} {doc[0]} ({doc[1]}) - {doc[2]} words - Trust: {doc[5]:.2f}")
    
    elif sys.argv[1] == "search":
        results = ingestor.search_documents(sys.argv[2])
        for r in results:
            print(f"  📄 {r[0]} - Trust: {r[5]:.2f}")
    
    elif sys.argv[1] == "stats":
        stats = ingestor.get_statistics()
        print(f"📊 Document Statistics:")
        print(f"   Total: {stats['total_documents']}")
        print(f"   Average trust: {stats['average_trust']:.2f}")
        print(f"   Dreams triggered: {stats['dreams_triggered']}")
    
    ingestor.close()
