#!/usr/bin/env python3
"""
Documentation Editor for Explorer-d334
Allows the forge to edit its own documentation with version control
"""

import os
import shutil
import difflib
from datetime import datetime
from pathlib import Path

class DocEditor:
    def __init__(self):
        self.forge_dir = Path.cwd()
        self.docs_dir = self.forge_dir
        self.backup_dir = self.forge_dir / ".doc_backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        self.doc_files = [
            "README.md",
            "FORGE_COMPLETE.md", 
            "FORGE_COMPLETE_GUIDE.md"
        ]
    
    def backup_file(self, filename):
        """Create a timestamped backup before editing"""
        file_path = self.docs_dir / filename
        if not file_path.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{filename}.{timestamp}.bak"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def edit_section(self, filename, section_title, new_content):
        """Edit a specific section in a markdown file"""
        file_path = self.docs_dir / filename
        if not file_path.exists():
            return {"success": False, "error": f"File {filename} not found"}
        
        # Create backup
        backup = self.backup_file(filename)
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Find section
        in_section = False
        section_start = -1
        section_end = -1
        
        for i, line in enumerate(lines):
            if line.strip().startswith('##') and section_title.lower() in line.lower():
                in_section = True
                section_start = i
            elif in_section and line.strip().startswith('##') and i > section_start:
                section_end = i - 1
                break
            elif in_section and i == len(lines) - 1:
                section_end = i
        
        if section_start == -1:
            # Section not found, append at end
            new_lines = lines + [f"\n## {section_title}\n\n", new_content, "\n"]
            change_type = "appended"
        else:
            # Replace section
            if section_end == -1:
                section_end = len(lines) - 1
            new_lines = lines[:section_start] + [f"## {section_title}\n\n", new_content, "\n"] + lines[section_end+1:]
            change_type = "replaced"
        
        # Write changes
        with open(file_path, 'w') as f:
            f.writelines(new_lines)
        
        # Log change
        self.log_change(filename, section_title, change_type, backup)
        
        return {
            "success": True, 
            "backup": str(backup),
            "change_type": change_type,
            "section": section_title
        }
    
    def log_change(self, filename, section, change_type, backup_path):
        """Log documentation changes"""
        log_file = self.backup_dir / "change_log.txt"
        timestamp = datetime.now().isoformat()
        
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] {change_type.upper()} in {filename} - Section: {section}\n")
            f.write(f"   Backup: {backup_path.name}\n")
            f.write(f"   By: Explorer-d334 (self-edit)\n")
            f.write("-" * 60 + "\n")
    
    def show_changes(self, filename, section=None):
        """Show recent changes to documentation"""
        log_file = self.backup_dir / "change_log.txt"
        if not log_file.exists():
            return "No changes recorded yet."
        
        with open(log_file, 'r') as f:
            content = f.read()
        
        if filename:
            # Filter by filename
            lines = content.split('\n')
            filtered = [l for l in lines if filename in l]
            return "\n".join(filtered[:20])
        
        return content[:2000]
    
    def rollback(self, filename, backup_name=None):
        """Rollback to a previous version"""
        if backup_name:
            backup_path = self.backup_dir / backup_name
        else:
            # Get latest backup
            backups = sorted(self.backup_dir.glob(f"{filename}.*.bak"))
            if not backups:
                return {"success": False, "error": "No backups found"}
            backup_path = backups[-1]
        
        if not backup_path.exists():
            return {"success": False, "error": f"Backup {backup_path} not found"}
        
        # Restore
        target_path = self.docs_dir / filename
        shutil.copy2(backup_path, target_path)
        
        return {"success": True, "restored": str(backup_path)}
    
    def get_backups(self, filename):
        """List available backups for a file"""
        backups = sorted(self.backup_dir.glob(f"{filename}.*.bak"))
        return [b.name for b in backups]
    
    def suggest_improvements(self):
        """Suggest improvements to documentation"""
        suggestions = []
        
        for filename in self.doc_files:
            file_path = self.docs_dir / filename
            if not file_path.exists():
                continue
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for missing sections
            if "Trust System" not in content and "trust" in content.lower():
                suggestions.append(f"Add 'Trust System' section to {filename}")
            
            if "Commands" not in content and "forge" in content:
                suggestions.append(f"Add 'Commands' section to {filename}")
            
            # Check for outdated info
            if "2025" in content and datetime.now().year > 2025:
                suggestions.append(f"Update year in {filename}")
        
        return suggestions
    
    def report(self):
        """Generate documentation change report"""
        print("\n" + "="*60)
        print("📝 DOCUMENTATION CHANGE REPORT")
        print("="*60)
        
        print("\n📚 Available documentation:")
        for filename in self.doc_files:
            file_path = self.docs_dir / filename
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"   ✅ {filename} ({size} bytes)")
            else:
                print(f"   ❌ {filename} (missing)")
        
        print("\n💾 Backups available:")
        for filename in self.doc_files:
            backups = self.get_backups(filename)
            if backups:
                print(f"   {filename}: {len(backups)} backups")
                for b in backups[-3:]:
                    print(f"      - {b}")
        
        print("\n📋 Recent changes:")
        changes = self.show_changes(None)
        print(changes[:500] if len(changes) > 500 else changes)
        
        print("\n💡 Suggested improvements:")
        for sug in self.suggest_improvements()[:5]:
            print(f"   • {sug}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    import sys
    
    editor = DocEditor()
    
    if len(sys.argv) < 2:
        editor.report()
    
    elif sys.argv[1] == "edit":
        if len(sys.argv) < 4:
            print("Usage: python doc_editor.py edit <filename> <section>")
            print("Example: python doc_editor.py edit README.md 'Quick Start'")
        else:
            result = editor.edit_section(sys.argv[2], sys.argv[3], sys.stdin.read())
            if result['success']:
                print(f"✅ Edited {sys.argv[2]}")
                print(f"   Backup: {result['backup']}")
                print(f"   Change: {result['change_type']}")
            else:
                print(f"❌ {result['error']}")
    
    elif sys.argv[1] == "rollback":
        if len(sys.argv) < 3:
            print("Usage: python doc_editor.py rollback <filename> [backup_name]")
        else:
            backup = sys.argv[3] if len(sys.argv) > 3 else None
            result = editor.rollback(sys.argv[2], backup)
            if result['success']:
                print(f"✅ Rolled back {sys.argv[2]} to {result['restored']}")
            else:
                print(f"❌ {result['error']}")
    
    elif sys.argv[1] == "backups":
        if len(sys.argv) < 3:
            print("Usage: python doc_editor.py backups <filename>")
        else:
            backups = editor.get_backups(sys.argv[2])
            for b in backups:
                print(f"   {b}")
    
    elif sys.argv[1] == "suggest":
        for sug in editor.suggest_improvements():
            print(f"💡 {sug}")
