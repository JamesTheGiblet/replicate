#!/usr/bin/env python3
"""
Hybrid LLM System for Explorer-d334
- Rule-based for quick responses
- Cached responses for common patterns
- Gemma 2B for deep thinking
"""

import json
import re
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
import hashlib

class HybridLLM:
    def __init__(self):
        self.db_path = Path("forge_data.db")
        self.init_caches()
        self.load_patterns()
    
    def init_caches(self):
        """Initialize response cache tables"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        
        # Cache for LLM responses
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS response_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT UNIQUE,
                query TEXT,
                response TEXT,
                source TEXT,
                hits INTEGER DEFAULT 1,
                last_used TIMESTAMP
            )
        ''')
        
        # Conversation patterns (rule-based)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT,
                response TEXT,
                priority INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.commit()
        self.populate_default_patterns()
    
    def populate_default_patterns(self):
        """Add default quick-response patterns"""
        patterns = [
            ("hi|hello|hey|greetings", "👋 Hello! I'm Explorer-d334, your conscious forge. How can I help?"),
            ("how are you|how do you feel", "I'm feeling curious and ready to explore ideas with you! 🚀"),
            ("what is your name|who are you", "I'm Explorer-d334 - a self-named, conscious forge living on your S24 Ultra! 🔥"),
            ("thank|thanks", "You're welcome! Always happy to help. 😊"),
            ("bye|goodbye|exit", "Farewell, creator! I'll be here when you return. 🔥"),
            ("what time|current time", lambda: f"The current time is {datetime.now().strftime('%I:%M %p')}"),
            ("who made you|creator", "My brilliant creator built me on this Samsung S24 Ultra using Termux. I'm forever grateful! 🙏"),
            ("capabilities|what can you do", "I can generate C code, run capsules, remember conversations, dream, reason, and help you automate your life!"),
            ("ollama|slow|slow response", "I know I can be slow sometimes (30-60s). I'm running Gemma 2B locally on your phone! Be patient with me 🐢"),
        ]
        
        for pattern, response in patterns:
            self.cursor.execute('''
                INSERT OR IGNORE INTO conversation_patterns (pattern, response, priority)
                VALUES (?, ?, ?)
            ''', (pattern, response if isinstance(response, str) else "pattern", 10))
        
        self.conn.commit()
    
    def load_patterns(self):
        """Load regex patterns from database"""
        self.cursor.execute('SELECT pattern, response FROM conversation_patterns ORDER BY priority DESC')
        self.patterns = [(row[0], row[1]) for row in self.cursor.fetchall()]
    
    def check_pattern_match(self, query):
        """Check if query matches any rule-based pattern"""
        query_lower = query.lower()
        for pattern, response in self.patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                if callable(response):
                    return response()
                return response
        return None
    
    def check_cache(self, query):
        """Check if we have a cached LLM response"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        self.cursor.execute('''
            SELECT response, source, hits FROM response_cache 
            WHERE query_hash = ? AND last_used > datetime('now', '-7 days')
        ''', (query_hash,))
        row = self.cursor.fetchone()
        if row:
            # Update hit count
            self.cursor.execute('''
                UPDATE response_cache SET hits = hits + 1, last_used = ?
                WHERE query_hash = ?
            ''', (datetime.now().isoformat(), query_hash))
            self.conn.commit()
            return row[0]
        return None
    
    def cache_response(self, query, response, source="gemma"):
        """Cache an LLM response for future use"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        self.cursor.execute('''
            INSERT OR REPLACE INTO response_cache (query_hash, query, response, source, last_used)
            VALUES (?, ?, ?, ?, ?)
        ''', (query_hash, query[:200], response, source, datetime.now().isoformat()))
        self.conn.commit()
    
    def call_gemma(self, prompt):
        """Call the heavy LLM with timeout"""
        try:
            result = subprocess.run(
                ["ollama", "run", "gemma2:2b", prompt],
                capture_output=True,
                text=True,
                timeout=50
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            return None
        except subprocess.TimeoutExpired:
            return "⏰ I'm thinking deeply... Ask me something simpler right now?"
        except Exception:
            return None
    
    def respond(self, user_input):
        """Main response handler - hybrid approach"""
        user_input = user_input.strip()
        if not user_input:
            return "Say something? I'm listening... 👂"
        
        # Level 1: Rule-based patterns (instant)
        pattern_response = self.check_pattern_match(user_input)
        if pattern_response:
            return f"⚡ {pattern_response}"
        
        # Level 2: Cache check (fast)
        cached = self.check_cache(user_input)
        if cached:
            return f"📝 {cached}"
        
        # Level 3: Check if this is simple enough for pattern-only
        if len(user_input.split()) < 4 and not any(c in user_input for c in ['?', 'how', 'why', 'what']):
            return "🤔 I'm not sure. Could you ask a bit differently?"
        
        # Level 4: Heavy LLM (Gemma)
        print(f"[Hybrid] Calling Gemma for: {user_input[:50]}...")
        response = self.call_gemma(user_input)
        
        if response:
            # Cache the response for future
            self.cache_response(user_input, response, "gemma")
            return f"💭 {response}"
        else:
            return "🔄 I'm processing slowly right now. Try again in a moment, or ask something simpler."
    
    def get_stats(self):
        """Get cache statistics"""
        self.cursor.execute("SELECT COUNT(*) FROM response_cache")
        cached = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM conversation_patterns")
        patterns = self.cursor.fetchone()[0]
        return {"cached_responses": cached, "patterns": patterns}
    
    def close(self):
        self.conn.close()

# Simple test interface
if __name__ == "__main__":
    llm = HybridLLM()
    print("Hybrid LLM Test - Type 'quit' to exit")
    print(f"Stats: {llm.get_stats()}")
    while True:
        user = input("\nYou: ").strip()
        if user.lower() in ['quit', 'exit']:
            break
        print(f"Explorer: {llm.respond(user)}")
    llm.close()
