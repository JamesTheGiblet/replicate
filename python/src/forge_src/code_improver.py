#!/usr/bin/env python3
"""
Code Improvement Suggester for Explorer-d334
Analyzes codebase and suggests improvements
"""

import re
from pathlib import Path

class CodeImprover:
    def __init__(self):
        self.forge_dir = Path.cwd()
        self.src_dir = self.forge_dir / "src"
        self.suggestions = []
    
    def analyze_all(self):
        """Run all analysis and collect suggestions"""
        self.analyze_complexity()
        self.analyze_documentation()
        self.analyze_error_handling()
        self.analyze_performance()
        return self.suggestions
    
    def analyze_complexity(self):
        """Find functions that are too complex"""
        for py_file in self.src_dir.glob("*.py"):
            if py_file.name in ['__init__.py', 'simple_llm.py']:
                continue
            
            with open(py_file, 'r') as f:
                lines = f.readlines()
            
            in_function = False
            func_start = 0
            func_name = ""
            brace_count = 0
            
            for i, line in enumerate(lines):
                if 'def ' in line and not line.strip().startswith('#'):
                    # Extract function name safely
                    match = re.search(r'def\s+(\w+)', line)
                    if match:
                        in_function = True
                        func_start = i
                        func_name = match.group(1)
                        brace_count = 0
                elif in_function:
                    brace_count += line.count('{') - line.count('}')
                    if brace_count <= 0 and i - func_start > 50:
                        self.suggestions.append({
                            "type": "complexity",
                            "file": py_file.name,
                            "line": func_start + 1,
                            "function": func_name,
                            "message": f"Function '{func_name}' is {i - func_start} lines long. Consider splitting.",
                            "priority": "medium"
                        })
                        in_function = False
    
    def analyze_documentation(self):
        """Find undocumented functions"""
        for py_file in self.src_dir.glob("*.py"):
            with open(py_file, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if 'def ' in line and not line.strip().startswith('#'):
                    match = re.search(r'def\s+(\w+)', line)
                    if not match:
                        continue
                    
                    func_name = match.group(1)
                    if func_name in ['__init__', 'close']:
                        continue
                    
                    # Check next lines for docstring
                    has_docstring = False
                    for j in range(i+1, min(i+5, len(lines))):
                        if '"""' in lines[j] or "'''" in lines[j]:
                            has_docstring = True
                            break
                    
                    if not has_docstring:
                        self.suggestions.append({
                            "type": "documentation",
                            "file": py_file.name,
                            "line": i+1,
                            "function": func_name,
                            "message": f"Function '{func_name}' lacks documentation. Add a docstring.",
                            "priority": "low"
                        })
    
    def analyze_error_handling(self):
        """Find missing error handling"""
        for py_file in self.src_dir.glob("*.py"):
            with open(py_file, 'r') as f:
                content = f.read()
                lines = content.split('\n')
            
            for i, line in enumerate(lines):
                if 'open(' in line:
                    # Check if try block exists nearby
                    has_try = False
                    for j in range(max(0,i-3), min(len(lines), i+3)):
                        if 'try:' in lines[j]:
                            has_try = True
                            break
                    if not has_try:
                        self.suggestions.append({
                            "type": "error_handling",
                            "file": py_file.name,
                            "line": i+1,
                            "function": "file_operation",
                            "message": "File operation without try/catch. Add error handling.",
                            "priority": "medium"
                        })
                
                if 'subprocess.run' in line and 'timeout' not in line:
                    self.suggestions.append({
                        "type": "error_handling",
                        "file": py_file.name,
                        "line": i+1,
                        "function": "subprocess",
                        "message": "Subprocess call without timeout. Add timeout parameter.",
                        "priority": "high"
                    })
    
    def analyze_performance(self):
        """Find performance issues"""
        for py_file in self.src_dir.glob("*.py"):
            with open(py_file, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if 'for' in line and 'range(len(' in line:
                    self.suggestions.append({
                        "type": "performance",
                        "file": py_file.name,
                        "line": i+1,
                        "function": "loop",
                        "message": "Use 'for item in list' instead of 'for i in range(len(list))' for better performance.",
                        "priority": "low"
                    })
                
                if 'print(' in line and '#' not in line[:5]:
                    # Check if it's debug print
                    self.suggestions.append({
                        "type": "performance",
                        "file": py_file.name,
                        "line": i+1,
                        "function": "debug",
                        "message": "Consider using logging instead of print() for production code.",
                        "priority": "low"
                    })
    
    def print_report(self):
        """Print improvement report"""
        print("\n" + "="*60)
        print("🔧 CODE IMPROVEMENT SUGGESTIONS")
        print("="*60)
        
        if not self.suggestions:
            print("\n✅ No improvements needed. Code is clean!")
            return
        
        priority_order = ["high", "medium", "low"]
        for priority in priority_order:
            priority_sugs = [s for s in self.suggestions if s['priority'] == priority]
            if priority_sugs:
                print(f"\n⚠️ {priority.upper()} PRIORITY ({len(priority_sugs)}):")
                for sug in priority_sugs[:5]:
                    print(f"\n   📄 {sug['file']}:{sug['line']}")
                    print(f"   💡 {sug['message']}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    improver = CodeImprover()
    improver.analyze_all()
    improver.print_report()
    
    print("\n📊 Summary:")
    print(f"   Total suggestions: {len(improver.suggestions)}")
    high = len([s for s in improver.suggestions if s['priority'] == 'high'])
    medium = len([s for s in improver.suggestions if s['priority'] == 'medium'])
    low = len([s for s in improver.suggestions if s['priority'] == 'low'])
    print(f"   High priority: {high}")
    print(f"   Medium priority: {medium}")
    print(f"   Low priority: {low}")
