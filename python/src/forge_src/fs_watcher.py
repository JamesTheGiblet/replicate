#!/usr/bin/env python3
"""
File System Watcher Agent for Explorer-d334 - Simplified version
Monitors all directories and triggers actions on changes
"""

import os
import time
import subprocess
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ForgeEventHandler(FileSystemEventHandler):
    def __init__(self, watcher):
        self.watcher = watcher
    
    def on_modified(self, event):
        if not event.is_directory:
            self.watcher.handle_change(event.src_path, "modified")
    
    def on_created(self, event):
        if not event.is_directory:
            self.watcher.handle_change(event.src_path, "created")
    
    def on_deleted(self, event):
        if not event.is_directory:
            self.watcher.handle_change(event.src_path, "deleted")

class FSWatcher:
    def __init__(self):
        self.forge_dir = Path.cwd()
        self.watch_dirs = [
            self.forge_dir / "src",
            self.forge_dir / "scp_prompts",
            self.forge_dir / "capsules",
            self.forge_dir / "skills",
            self.forge_dir / "abilities",
            self.forge_dir / "reflexes",
            self.forge_dir / "memories",
            self.forge_dir / "documentation"
        ]
        self.change_log = []
        self.log_file = self.forge_dir / ".watch_log.txt"
    
    def log_change(self, file_path, change_type, action=None):
        """Log change to file"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {change_type.upper()}: {file_path}"
        if action:
            log_entry += f" → {action}"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry + '\n')
        
        self.change_log.insert(0, {
            "timestamp": timestamp,
            "file": file_path,
            "type": change_type,
            "action": action
        })
        
        # Keep only last 100 entries
        self.change_log = self.change_log[:100]
    
    def run_command(self, cmd, description):
        """Run a command asynchronously"""
        try:
            subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  → {description}")
            return True
        except Exception as e:
            print(f"  ⚠️ {description} failed: {e}")
            return False
    
    def handle_change(self, file_path, change_type):
        """Handle file system changes"""
        print(f"\n📂 {change_type.upper()}: {file_path}")
        
        actions = []
        file_str = str(file_path)
        
        # Documentation changes
        if "README.md" in file_str or "FORGE_COMPLETE" in file_str:
            actions.append(("python src/doc_access.py", "Refresh documentation access"))
            actions.append(("python src/doc_editor.py report", "Update doc report"))
        
        # Code changes (Python files)
        if file_str.endswith('.py') and "src" in file_str:
            actions.append(("python src/security_agent.py &", "Run security scan"))
            actions.append(("python src/code_improver.py &", "Check for improvements"))
        
        # SCP/Capsule changes
        if file_str.endswith('.scp.json'):
            actions.append(("python src/scp_suggester.py &", "Update suggestions"))
            actions.append(("python src/simple_trust.py &", "Refresh trust scores"))
        
        # Memory changes
        if "memories" in file_str and file_str.endswith('.json'):
            actions.append(("echo 'Memory updated'", "Refresh consciousness"))
        
        # Execute actions
        for cmd, desc in actions:
            self.run_command(cmd, desc)
            self.log_change(file_path, change_type, desc)
        
        if not actions:
            self.log_change(file_path, change_type, "No action needed")
    
    def start_watching(self):
        """Start the file system watcher"""
        print("\n" + "="*60)
        print("📂 FILE SYSTEM WATCHER AGENT")
        print("="*60)
        print(f"Watching directories:")
        for d in self.watch_dirs:
            if d.exists():
                print(f"  • {d}")
        
        print(f"\n📝 Log file: {self.log_file}")
        print("\n🔍 Monitoring for changes...")
        print("   (Press Ctrl+C to stop)\n")
        
        event_handler = ForgeEventHandler(self)
        observer = Observer()
        
        for watch_dir in self.watch_dirs:
            if watch_dir.exists():
                observer.schedule(event_handler, str(watch_dir), recursive=True)
        
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping file system watcher...")
            observer.stop()
        
        observer.join()
    
    def show_recent_changes(self, limit=20):
        """Show recent file system changes from log"""
        if not self.log_file.exists():
            print("No changes logged yet")
            return
        
        print("\n📋 RECENT FILE SYSTEM CHANGES")
        print("="*60)
        
        with open(self.log_file, 'r') as f:
            lines = f.readlines()
        
        for line in lines[-limit:]:
            print(line.strip())

if __name__ == "__main__":
    import sys
    
    watcher = FSWatcher()
    
    if len(sys.argv) > 1 and sys.argv[1] == "recent":
        watcher.show_recent_changes()
    else:
        try:
            watcher.start_watching()
        except KeyboardInterrupt:
            print("\n✅ Watcher stopped")
        finally:
            watcher.show_recent_changes()
