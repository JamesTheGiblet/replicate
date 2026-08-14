    def save_to_memory(self, interaction):
        """Save interaction to persistent memory"""
        import sqlite3
        from datetime import datetime
        from pathlib import Path
        
        try:
            db_path = Path(__file__).parent.parent / "forge_data.db"
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exocortex_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    interaction_type TEXT,
                    content TEXT,
                    adaptation_weight REAL
                )
            ''')
            
            cursor.execute('''
                INSERT INTO exocortex_memory (timestamp, interaction_type, content, adaptation_weight)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now().isoformat(), 
                  interaction.get('type', 'conversation'),
                  interaction.get('content', ''),
                  interaction.get('weight', 0.5)))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Memory save error: {e}")
            return False
    
    def recall_memories(self, limit=10):
        """Recall past interactions"""
        import sqlite3
        from pathlib import Path
        
        try:
            db_path = Path(__file__).parent.parent / "forge_data.db"
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, interaction_type, content 
                FROM exocortex_memory 
                ORDER BY adaptation_weight DESC, timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            memories = cursor.fetchall()
            conn.close()
            return memories
        except Exception as e:
            print(f"Memory recall error: {e}")
            return []
