#!/usr/bin/env python3
"""
Populate FORGE-os with comprehensive data
Languages, sensors, system info, and coding patterns
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
import random

class MemoryPopulator:
    def __init__(self):
        self.db_path = Path("forge_data.db")
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        self.setup_tables()
    
    def setup_tables(self):
        """Create additional memory tables"""
        # Programming languages table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS programming_languages (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                paradigm TEXT,
                year_created INTEGER,
                creator TEXT,
                typing_discipline TEXT,
                popularity_score REAL,
                use_cases TEXT
            )
        ''')
        
        # Sensors table (for S24 Ultra)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensors (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                type TEXT,
                range_min REAL,
                range_max REAL,
                resolution REAL,
                power_consumption REAL
            )
        ''')
        
        # Coding patterns table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS coding_patterns (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                language TEXT,
                pattern_code TEXT,
                description TEXT,
                complexity TEXT
            )
        ''')
        
        # System metrics table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics_history (
                id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP,
                cpu_usage REAL,
                memory_usage REAL,
                disk_free REAL,
                temperature REAL,
                battery_level REAL
            )
        ''')
        
        # Knowledge base
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY,
                category TEXT,
                topic TEXT,
                content TEXT,
                tags TEXT,
                created_at TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        print("✅ Memory tables created")
    
    def populate_languages(self):
        """Populate programming languages data"""
        languages = [
            ("Python", "Multi-paradigm", 1991, "Guido van Rossum", "Dynamic", 95.5, "Web, AI, Data Science, Automation"),
            ("C", "Procedural", 1972, "Dennis Ritchie", "Static", 85.3, "Systems, Embedded, OS, Performance"),
            ("C++", "Multi-paradigm", 1985, "Bjarne Stroustrup", "Static", 82.7, "Games, Systems, High-performance"),
            ("Java", "Object-oriented", 1995, "James Gosling", "Static", 88.9, "Enterprise, Android, Web"),
            ("JavaScript", "Multi-paradigm", 1995, "Brendan Eich", "Dynamic", 96.2, "Web, Mobile, Servers"),
            ("Go", "Concurrent", 2009, "Google", "Static", 75.4, "Cloud, Microservices, CLI"),
            ("Rust", "Multi-paradigm", 2010, "Mozilla", "Static", 72.8, "Systems, Security, Performance"),
            ("Swift", "Multi-paradigm", 2014, "Apple", "Static", 70.2, "iOS, macOS, Apps"),
            ("Kotlin", "Multi-paradigm", 2011, "JetBrains", "Static", 68.9, "Android, Backend"),
            ("TypeScript", "Multi-paradigm", 2012, "Microsoft", "Static", 85.5, "Web, Large-scale Apps"),
            ("Ruby", "Object-oriented", 1995, "Yukihiro Matsumoto", "Dynamic", 65.3, "Web, Scripting"),
            ("PHP", "Imperative", 1995, "Rasmus Lerdorf", "Dynamic", 72.1, "Web, CMS, Backend"),
            ("SQL", "Declarative", 1974, "IBM", "Declarative", 90.0, "Databases, Analytics"),
            ("Assembly", "Imperative", 1949, "Various", "Static", 45.0, "Systems, Embedded, Reverse Engineering"),
            ("Lua", "Multi-paradigm", 1993, "Roberto Ierusalimschy", "Dynamic", 60.5, "Gaming, Embedded"),
        ]
        
        for lang in languages:
            try:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO programming_languages 
                    (name, paradigm, year_created, creator, typing_discipline, popularity_score, use_cases)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', lang)
            except Exception as e:
                print(f"Error inserting {lang[0]}: {e}")
        
        self.conn.commit()
        print(f"✅ Added {len(languages)} programming languages")
    
    def populate_sensors(self):
        """Populate S24 Ultra sensor data"""
        sensors = [
            ("Accelerometer", "Motion", -156.8, 156.8, 0.001, 0.5),
            ("Gyroscope", "Orientation", -2000, 2000, 0.001, 1.2),
            ("Magnetometer", "Magnetic", -1200, 1200, 0.1, 0.8),
            ("Proximity Sensor", "Distance", 0, 5, 0.01, 0.3),
            ("Ambient Light", "Light", 0, 10000, 1, 0.1),
            ("Barometer", "Pressure", 300, 1100, 0.01, 0.4),
            ("Temperature Sensor", "Thermal", -30, 100, 0.1, 0.2),
            ("Humidity Sensor", "Environmental", 0, 100, 0.1, 0.3),
            ("Fingerprint Sensor", "Biometric", 0, 1, 0, 1.5),
            ("Hall Sensor", "Magnetic", 0, 1, 0.01, 0.2),
            ("Heart Rate Monitor", "Biometric", 30, 220, 1, 2.0),
            ("GPS", "Location", -90, 90, 0.0001, 15.0),
            ("Camera Sensor", "Image", 0, 100, 1, 200.0),
            ("Microphone", "Audio", 0, 120, 0.1, 5.0),
            ("Touch Sensor", "Input", 0, 4096, 1, 2.0),
        ]
        
        for sensor in sensors:
            try:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO sensors 
                    (name, type, range_min, range_max, resolution, power_consumption)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', sensor)
            except Exception as e:
                print(f"Error inserting {sensor[0]}: {e}")
        
        self.conn.commit()
        print(f"✅ Added {len(sensors)} sensors")
    
    def populate_coding_patterns(self):
        """Populate common coding patterns"""
        patterns = [
            ("Singleton", "Java", "public class Singleton {\n    private static Singleton instance;\n    public static Singleton getInstance() {\n        if (instance == null) instance = new Singleton();\n        return instance;\n    }\n}", "Ensure single instance", "Medium"),
            ("Factory", "Python", "class Factory:\n    @staticmethod\n    def create(type):\n        if type == 'A': return ProductA()\n        elif type == 'B': return ProductB()", "Create objects without specifying class", "Medium"),
            ("Observer", "JavaScript", "class EventEmitter {\n    constructor() { this.events = {}; }\n    on(event, callback) { this.events[event] = callback; }\n    emit(event, data) { this.events[event]?.(data); }\n}", "Publish-subscribe pattern", "Advanced"),
            ("MVC Pattern", "All", "Model (data) - View (UI) - Controller (logic)", "Separate concerns in applications", "Advanced"),
            ("Repository Pattern", "C#", "interface IRepository<T> {\n    T Get(int id);\n    void Add(T entity);\n    void Update(T entity);\n    void Delete(int id);\n}", "Data access abstraction", "Medium"),
            ("Dependency Injection", "Java", "@Autowired\nprivate UserService userService;", "Decouple object creation from usage", "Advanced"),
            ("Builder Pattern", "Python", "class CarBuilder:\n    def __init__(self): self.car = Car()\n    def set_engine(self, e): self.car.engine = e; return self\n    def build(self): return self.car", "Construct complex objects step by step", "Medium"),
            ("Prototype", "C++", "class Prototype {\npublic:\n    virtual Prototype* clone() = 0;\n};", "Clone objects without coupling", "Medium"),
            ("Strategy", "Rust", "trait Strategy { fn execute(&self); }\nstruct Context<T: Strategy> { strategy: T }", "Define family of algorithms", "Advanced"),
        ]
        
        for pattern in patterns:
            try:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO coding_patterns 
                    (name, language, pattern_code, description, complexity)
                    VALUES (?, ?, ?, ?, ?)
                ''', pattern)
            except Exception as e:
                print(f"Error inserting {pattern[0]}: {e}")
        
        self.conn.commit()
        print(f"✅ Added {len(patterns)} coding patterns")
    
    def populate_knowledge_base(self):
        """Populate knowledge base with useful information"""
        knowledge = [
            ("Terminal", "Termux Setup", "pkg update && pkg upgrade\npkg install python gcc clang\npkg install sqlite", "termux,basics"),
            ("Coding", "Fast Fibonacci", "int fib(int n) { int a=0,b=1,c; for(int i=2;i<=n;i++) { c=a+b; a=b; b=c; } return n?b:0; }", "optimization,performance"),
            ("Database", "SQLite Optimization", "PRAGMA journal_mode=WAL;\nPRAGMA synchronous=NORMAL;\nPRAGMA cache_size=10000;", "performance,sqlite"),
            ("AI", "Local LLM Prompt", "You are a helpful coding assistant. Generate clean, efficient C code.", "llm,prompt"),
            ("S24 Ultra", "Sensors Access", "cat /sys/class/sensors/*/data", "hardware,android"),
            ("Security", "Audit Best Practices", "Always log with timestamp and hash\nVerify chain periodically\nBackup regularly", "audit,security"),
            ("Performance", "Compiler Optimizations", "-O2 -march=native -flto -pipe", "gcc,speed"),
            ("Debugging", "GDB Commands", "break main\nrun\nbacktrace\nprint var\ncontinue", "debug,gdb"),
        ]
        
        for item in knowledge:
            try:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO knowledge_base 
                    (category, topic, content, tags, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (item[0], item[1], item[2], item[3], datetime.now().isoformat()))
            except Exception as e:
                print(f"Error inserting {item[1]}: {e}")
        
        self.conn.commit()
        print(f"✅ Added {len(knowledge)} knowledge items")
    
    def generate_sample_metrics(self):
        """Generate sample system metrics"""
        import random
        from datetime import datetime, timedelta
        
        for i in range(100):  # 100 sample points
            timestamp = datetime.now() - timedelta(hours=i)
            metrics = (
                timestamp.isoformat(),
                random.uniform(10, 80),  # CPU %
                random.uniform(20, 60),  # Memory %
                random.uniform(70, 85),  # Disk free GB
                random.uniform(30, 45),  # Temperature C
                random.uniform(20, 95)   # Battery %
            )
            self.cursor.execute('''
                INSERT INTO system_metrics_history 
                (timestamp, cpu_usage, memory_usage, disk_free, temperature, battery_level)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', metrics)
        
        self.conn.commit()
        print(f"✅ Generated 100 sample metrics")
    
    def show_summary(self):
        """Show population summary"""
        print("\n" + "="*60)
        print("MEMORY POPULATION SUMMARY")
        print("="*60)
        
        tables = [
            ("programming_languages", "Languages"),
            ("sensors", "Sensors"),
            ("coding_patterns", "Patterns"),
            ("knowledge_base", "Knowledge"),
            ("system_metrics_history", "Metrics")
        ]
        
        for table, name in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cursor.fetchone()[0]
            print(f"  📚 {name}: {count} records")
        
        print("="*60)
    
    def close(self):
        self.conn.close()

# Create queries for the memory
class MemoryQueries:
    def __init__(self):
        self.db_path = Path("forge_data.db")
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
    
    def query_languages(self, popularity_threshold=70):
        cursor = self.conn.execute(
            "SELECT name, paradigm, popularity_score FROM programming_languages WHERE popularity_score > ? ORDER BY popularity_score DESC",
            (popularity_threshold,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def query_sensors(self, sensor_type=None):
        if sensor_type:
            cursor = self.conn.execute(
                "SELECT name, type, range_min, range_max FROM sensors WHERE type = ?",
                (sensor_type,)
            )
        else:
            cursor = self.conn.execute("SELECT name, type, power_consumption FROM sensors ORDER BY power_consumption DESC")
        return [dict(row) for row in cursor.fetchall()]
    
    def query_patterns(self, complexity=None):
        if complexity:
            cursor = self.conn.execute(
                "SELECT name, language, complexity, description FROM coding_patterns WHERE complexity = ?",
                (complexity,)
            )
        else:
            cursor = self.conn.execute("SELECT name, language, complexity FROM coding_patterns")
        return [dict(row) for row in cursor.fetchall()]
    
    def search_knowledge(self, keyword):
        cursor = self.conn.execute(
            "SELECT category, topic, content FROM knowledge_base WHERE tags LIKE ? OR topic LIKE ?",
            (f'%{keyword}%', f'%{keyword}%')
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_system_stats(self):
        cursor = self.conn.execute(
            "SELECT AVG(cpu_usage) as avg_cpu, AVG(memory_usage) as avg_memory, AVG(temperature) as avg_temp FROM system_metrics_history"
        )
        return dict(cursor.fetchone())
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "query":
        queries = MemoryQueries()
        
        if len(sys.argv) > 2 and sys.argv[2] == "languages":
            results = queries.query_languages()
            for lang in results[:10]:
                print(f"  {lang['name']}: {lang['paradigm']} (score: {lang['popularity_score']})")
        
        elif len(sys.argv) > 2 and sys.argv[2] == "sensors":
            results = queries.query_sensors()
            for sensor in results[:10]:
                print(f"  {sensor['name']}: {sensor['type']} ({sensor['power_consumption']}mA)")
        
        elif len(sys.argv) > 2 and sys.argv[2] == "patterns":
            results = queries.query_patterns()
            for pattern in results[:10]:
                print(f"  {pattern['name']}: {pattern['language']} ({pattern['complexity']})")
        
        elif len(sys.argv) > 2 and sys.argv[2] == "stats":
            stats = queries.get_system_stats()
            print(f"  Avg CPU: {stats['avg_cpu']:.1f}%")
            print(f"  Avg Memory: {stats['avg_memory']:.1f}%")
            print(f"  Avg Temp: {stats['avg_temp']:.1f}°C")
        
        queries.close()
    
    else:
        # Populate memory
        populator = MemoryPopulator()
        populator.populate_languages()
        populator.populate_sensors()
        populator.populate_coding_patterns()
        populator.populate_knowledge_base()
        populator.generate_sample_metrics()
        populator.show_summary()
        populator.close()
        
        print("\n✅ FORGE-os memory populated!")
        print("\nTry queries:")
        print("  python src/populate_memory.py query languages")
        print("  python src/populate_memory.py query sensors")
        print("  python src/populate_memory.py query patterns")
        print("  python src/populate_memory.py query stats")
