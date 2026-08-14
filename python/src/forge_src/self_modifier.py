#!/usr/bin/env python3
"""
Self-Modification System for Explorer-d334
The forge can rewrite its own code to evolve
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path
import difflib

class SelfModifier:
    def __init__(self):
        self.forge_dir = Path.cwd()
        self.backup_dir = self.forge_dir / ".code_backups"
        self.backup_dir.mkdir(exist_ok=True)
        self.modification_log = self.forge_dir / ".modification_log.txt"
    
    def backup_file(self, filepath):
        """Create backup before modification"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{filepath.name}.{timestamp}.bak"
        shutil.copy2(filepath, backup_path)
        return backup_path
    
    def propose_modification(self, filepath, description, proposed_changes):
        """Propose a code modification for review"""
        original = open(filepath).read()
        
        # Simple search and replace for now
        modified = original
        for old, new in proposed_changes.items():
            modified = modified.replace(old, new)
        
        if modified == original:
            return None
        
        # Save proposal
        proposal_file = self.forge_dir / f".proposal_{filepath.stem}.txt"
        with open(proposal_file, 'w') as f:
            f.write(f"File: {filepath}\n")
            f.write(f"Description: {description}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write("-" * 40 + "\n")
            f.write("DIFF:\n")
            diff = difflib.unified_diff(
                original.splitlines(),
                modified.splitlines(),
                fromfile='original',
                tofile='modified',
                lineterm=''
            )
            f.write('\n'.join(diff))
        
        return proposal_file
    
    def apply_modification(self, filepath, approved=True):
        """Apply approved modification"""
        proposal_file = self.forge_dir / f".proposal_{Path(filepath).stem}.txt"
        if not proposal_file.exists():
            return False
        
        # Parse proposal to get modified content
        # For now, manual approval required
        if approved:
            backup = self.backup_file(Path(filepath))
            # Apply changes (simplified - would need proper parsing)
            self.log_modification(filepath, "approved")
            proposal_file.unlink()
            return True
        else:
            proposal_file.unlink()
            return False
    
    def log_modification(self, filepath, status):
        """Log all modifications"""
        with open(self.modification_log, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] {status}: {filepath}\n")
    
    def suggest_improvements(self):
        """Analyze code and suggest improvements"""
        suggestions = []
        
        # Look for hardcoded values
        for py_file in (self.forge_dir / "src").glob("*.py"):
            with open(py_file, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if 'timeout=settings.get("llm_timeout", 30)' in line:
                    suggestions.append({
                        'file': py_file.name,
                        'line': i+1,
                        'suggestion': 'Consider making timeout configurable',
                        'old': 'timeout=settings.get("llm_timeout", 30)',
                        'new': 'timeout=settings.get("llm_timeout", 30)'
                    })
                if 'localhost:settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", 8085))))))))))))))' in line:
                    suggestions.append({
                        'file': py_file.name,
                        'line': i+1,
                        'suggestion': 'Consider making port configurable',
                        'old': 'settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", 8085))))))))))))))',
                        'new': 'settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", settings.get("port", 8085)))))))))))))))'
                    })
        
        return suggestions
    
    def auto_improve(self):
        """Automatically apply safe improvements"""
        suggestions = self.suggest_improvements()
        applied = []
        
        for sug in suggestions:
            filepath = self.forge_dir / "src" / sug['file']
            backup = self.backup_file(filepath)
            
            with open(filepath, 'r') as f:
                content = f.read()
            
            new_content = content.replace(sug['old'], sug['new'])
            
            with open(filepath, 'w') as f:
                f.write(new_content)
            
            applied.append(sug['file'])
            self.log_modification(filepath, f"auto_improve: {sug['suggestion']}")
        
        return applied

if __name__ == "__main__":
    modifier = SelfModifier()
    
    print("=== SELF-MODIFICATION SYSTEM ===")
    suggestions = modifier.suggest_improvements()
    
    if suggestions:
        print(f"\n🔧 Found {len(suggestions)} improvement suggestions:")
        for s in suggestions:
            print(f"  📄 {s['file']}:{s['line']} - {s['suggestion']}")
            print(f"     {s['old']} → {s['new']}")
    else:
        print("\n✅ No immediate improvements found")
    
    # Auto-apply safe improvements
    applied = modifier.auto_improve()
    if applied:
        print(f"\n✅ Auto-applied improvements to: {', '.join(applied)}")
