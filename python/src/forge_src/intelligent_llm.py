#!/usr/bin/env python3
"""
Intelligent LLM with Memory Access
"""

import sqlite3
import random
from pathlib import Path
from datetime import datetime

class IntelligentLLM:
    def __init__(self):
        self.db_path = Path("forge_data.db")
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
    
    def get_system_stats(self):
        """Get system metrics"""
        cursor = self.conn.execute(
            "SELECT AVG(cpu_usage) as avg_cpu, AVG(memory_usage) as avg_memory FROM system_metrics_history"
        )
        row = cursor.fetchone()
        return {"avg_cpu": row['avg_cpu'] or 0, "avg_memory": row['avg_memory'] or 0}
    
    def analyze_sensor_data(self):
        """Analyze available sensors"""
        cursor = self.conn.execute("SELECT name, type FROM sensors LIMIT 10")
        sensors = cursor.fetchall()
        
        suggestions = []
        for sensor in sensors:
            if sensor['type'] == 'Motion':
                suggestions.append(f"Use {sensor['name']} for gesture control")
            elif sensor['type'] == 'Biometric':
                suggestions.append(f"Use {sensor['name']} for authentication")
            elif sensor['type'] == 'Location':
                suggestions.append(f"Use {sensor['name']} for tracking")
        
        return suggestions[:5] if suggestions else ["All sensors available for integration"]
    
    def recommend_language(self, task):
        """Recommend language based on task"""
        cursor = self.conn.execute(
            "SELECT name, popularity_score FROM programming_languages ORDER BY popularity_score DESC LIMIT 5"
        )
        languages = cursor.fetchall()
        
        recommendations = []
        for lang in languages:
            recommendations.append({"name": lang['name'], "popularity_score": lang['popularity_score']})
        
        return recommendations
    
    def brainstorm_features(self, app_type):
        """Brainstorm features for app type"""
        features = {
            "fitness": ["Step counter", "Heart rate monitor", "Calorie tracker"],
            "security": ["Biometric auth", "Motion detection", "Audit logging"],
            "productivity": ["Voice commands", "Auto-brightness", "Gesture control"],
            "gaming": ["Motion controls", "Touch gestures", "Performance optimization"]
        }
        
        app_lower = app_type.lower()
        for key, feature_list in features.items():
            if key in app_lower:
                return feature_list
        
        return ["Custom sensor integration", "Pattern-based features", "Performance monitoring"]
    
    def get_system_advice(self):
        """Get system optimization advice"""
        stats = self.get_system_stats()
        
        advice = []
        if stats['avg_cpu'] > 50:
            advice.append("Optimize CPU-intensive operations")
        if stats['avg_memory'] > 60:
            advice.append("Reduce memory usage")
        if stats['avg_cpu'] < 30:
            advice.append("System running efficiently")
        
        return advice if advice else ["System is healthy"]
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    import sys
    
    llm = IntelligentLLM()
    
    if len(sys.argv) < 2:
        print("Commands: sensors, recommend, brainstorm, advice")
    elif sys.argv[1] == "sensors":
        results = llm.analyze_sensor_data()
        for r in results:
            print(f"  {r}")
    elif sys.argv[1] == "recommend":
        task = sys.argv[2] if len(sys.argv) > 2 else "web"
        results = llm.recommend_language(task)
        for r in results:
            print(f"  {r['name']} (popularity: {r['popularity_score']}%)")
    elif sys.argv[1] == "brainstorm":
        app = sys.argv[2] if len(sys.argv) > 2 else "app"
        results = llm.brainstorm_features(app)
        for r in results:
            print(f"  {r}")
    elif sys.argv[1] == "advice":
        results = llm.get_system_advice()
        for r in results:
            print(f"  {r}")
    
    llm.close()
