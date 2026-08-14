#!/usr/bin/env python3
"""
Integrate database with existing forge components
"""

import sys
import json
import subprocess
from pathlib import Path
from forge_db import ForgeDB

class ForgeDBIntegration:
    def __init__(self):
        self.db = ForgeDB()
    
    def import_scp_from_file(self, scp_path):
        """Import an SCP from JSON file into database"""
        with open(scp_path) as f:
            scp_data = json.load(f)
        
        name = scp_data.get('name', Path(scp_path).stem)
        self.db.save_scp(name, scp_data)
        print(f"Imported {name} from {scp_path}")
    
    def import_all_scps(self):
        """Import all SCPs from scp_prompts directory"""
        scp_dir = Path("scp_prompts")
        if scp_dir.exists():
            for scp_file in scp_dir.glob("*.json"):
                self.import_scp_from_file(scp_file)
    
    def track_execution(self, function_name, input_val, output_val, duration):
        """Track function execution in database"""
        self.db.log_execution(function_name, input_val, output_val, duration, True)
    
    def show_dashboard(self):
        """Show database dashboard"""
        print("\n" + "="*50)
        print("FORGE DATABASE DASHBOARD")
        print("="*50)
        
        stats = self.db.get_execution_stats()
        scps = self.db.list_scps(10)
        
        print(f"\n📊 Database Stats:")
        print(f"   Total executions: {stats.get('total_calls', 0)}")
        print(f"   Success rate: {stats.get('successes', 0) / max(1, stats.get('total_calls', 1)) * 100:.1f}%")
        print(f"   Avg execution time: {stats.get('avg_time', 0)*1000:.2f}ms")
        
        print(f"\n📝 Recent SCPs:")
        for scp in scps[:5]:
            print(f"   {scp['name']} (v{scp['version']})")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    integration = ForgeDBIntegration()
    
    if len(sys.argv) < 2:
        integration.show_dashboard()
    elif sys.argv[1] == "import":
        integration.import_all_scps()
    elif sys.argv[1] == "dashboard":
        integration.show_dashboard()
    
    integration.db.close()
