#!/usr/bin/env python3
"""
Agent 74 Memory System — Thread-Safe Version
"""

import json
import sqlite3
import time
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional

class AgentMemory:
    """Thread-safe memory system for Agent 74"""
    
    def __init__(self, db_path: str = "agent_74_memory.db"):
        self.db_path = Path(db_path)
        self._lock = threading.RLock()
        self._local = threading.local()
        self._init_db()
    
    def _get_conn(self):
        """Get thread-local database connection"""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._local.cursor = self._local.conn.cursor()
        return self._local.conn, self._local.cursor
    
    def _init_db(self):
        """Initialize database schema"""
        conn, cursor = self._get_conn()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                type TEXT,
                content TEXT,
                importance REAL,
                tags TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                question TEXT,
                context TEXT,
                status TEXT,
                answer TEXT,
                answered_at INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                insight TEXT,
                confidence REAL,
                source TEXT,
                applied INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        print(f"🧠 Memory initialized: {self.db_path}")
    
    def store_experience(self, exp_type: str, content: str, importance: float = 0.5, tags: List[str] = None):
        """Store an experience (thread-safe)"""
        with self._lock:
            conn, cursor = self._get_conn()
            cursor.execute('''
                INSERT INTO experiences (timestamp, type, content, importance, tags)
                VALUES (?, ?, ?, ?, ?)
            ''', (int(time.time()), exp_type, content[:500], importance, json.dumps(tags or [])))
            conn.commit()
    
    def store_question(self, question: str, context: str = ""):
        """Store a question (thread-safe)"""
        with self._lock:
            conn, cursor = self._get_conn()
            cursor.execute('''
                INSERT INTO questions (timestamp, question, context, status)
                VALUES (?, ?, ?, ?)
            ''', (int(time.time()), question[:200], context[:200], "pending"))
            conn.commit()
            return cursor.lastrowid
    
    def answer_question(self, question_id: int, answer: str):
        """Record an answer to a question (thread-safe)"""
        with self._lock:
            conn, cursor = self._get_conn()
            cursor.execute('''
                UPDATE questions SET answer = ?, answered_at = ?, status = ?
                WHERE id = ?
            ''', (answer[:200], int(time.time()), "answered", question_id))
            conn.commit()
    
    def store_learning(self, insight: str, confidence: float = 0.5, source: str = ""):
        """Store a learning (thread-safe)"""
        with self._lock:
            conn, cursor = self._get_conn()
            cursor.execute('''
                INSERT INTO learnings (timestamp, insight, confidence, source)
                VALUES (?, ?, ?, ?)
            ''', (int(time.time()), insight[:200], confidence, source[:50]))
            conn.commit()
    
    def get_recent_experiences(self, limit: int = 10) -> List[Dict]:
        """Get recent experiences (thread-safe)"""
        with self._lock:
            conn, cursor = self._get_conn()
            cursor.execute('''
                SELECT * FROM experiences ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_unanswered_questions(self) -> List[Dict]:
        """Get unanswered questions (thread-safe)"""
        with self._lock:
            conn, cursor = self._get_conn()
            cursor.execute('''
                SELECT * FROM questions WHERE status = "pending"
                ORDER BY timestamp DESC
            ''')
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_learnings(self, min_confidence: float = 0.0) -> List[Dict]:
        """Get stored learnings (thread-safe)"""
        with self._lock:
            conn, cursor = self._get_conn()
            cursor.execute('''
                SELECT * FROM learnings WHERE confidence >= ?
                ORDER BY confidence DESC
            ''', (min_confidence,))
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def close(self):
        """Close all connections"""
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
