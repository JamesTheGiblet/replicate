#!/usr/bin/env python3
"""
Code Base Access for Explorer-d334
Allows the forge to read and understand its own source code
"""

import ast
import os
from pathlib import Path
import re

class CodeAccess:
    def __init__(self):
        self.forge_dir = Path.cwd()
        self.src_dir = self.forge_dir / "src"
        self.code_files = {}
        self.load_all_code()
    
    def load_all_code(self):
        """Load all Python source files"""
        if not self.src_dir.exists():
            return
        
        for py_file in self.src_dir.glob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    self.code_files[py_file.name] = {
                        "content": content,
                        "size": len(content),
                        "lines": len(content.split('\n')),
                        "functions": self._extract_functions(content),
                        "classes": self._extract_classes(content)
                    }
            except Exception as e:
                print(f"Error loading {py_file}: {e}")
    
    def _extract_functions(self, content):
        """Extract function names from code"""
        functions = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
        except:
            # Fallback to regex
            pattern = r'^def\s+(\w+)\s*\('
            functions = re.findall(pattern, content, re.MULTILINE)
        return functions
    
    def _extract_classes(self, content):
        """Extract class names from code"""
        classes = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
        except:
            pattern = r'^class\s+(\w+)'
            classes = re.findall(pattern, content, re.MULTILINE)
        return classes
    
    def search_code(self, keyword):
        """Search code for keyword"""
        results = []
        keyword_lower = keyword.lower()
        
        for filename, info in self.code_files.items():
            lines = info['content'].split('\n')
            for i, line in enumerate(lines):
                if keyword_lower in line.lower():
                    results.append({
                        "file": filename,
                        "line": i+1,
                        "content": line.strip()[:150],
                        "function": self._find_function_name(lines, i)
                    })
        return results[:20]
    
    def _find_function_name(self, lines, line_num):
        """Find which function a line belongs to"""
        for i in range(line_num, -1, -1):
            if lines[i].strip().startswith('def '):
                match = re.search(r'def\s+(\w+)', lines[i])
                if match:
                    return match.group(1)
        return None
    
    def get_file_summary(self):
        """Get summary of all code files"""
        summary = {}
        for filename, info in self.code_files.items():
            summary[filename] = {
                "lines": info['lines'],
                "functions": len(info['functions']),
                "classes": len(info['classes'])
            }
        return summary
    
    def get_function_code(self, function_name):
        """Get the code for a specific function"""
        for filename, info in self.code_files.items():
            lines = info['content'].split('\n')
            in_function = False
            function_lines = []
            indent_level = 0
            
            for i, line in enumerate(lines):
                if f"def {function_name}" in line:
                    in_function = True
                    function_lines.append(line)
                    # Get indentation level
                    indent_level = len(line) - len(line.lstrip())
                elif in_function:
                    # Check if we're still in the function
                    if line.strip() and len(line) - len(line.lstrip()) <= indent_level and not line.strip().startswith('#'):
                        break
                    function_lines.append(line)
            
            if function_lines:
                return "\n".join(function_lines)
        return None
    
    def explain_file(self, filename):
        """Explain what a file does"""
        if filename not in self.code_files:
            return f"File {filename} not found"
        
        info = self.code_files[filename]
        content = info['content']
        
        # Try to get docstring
        docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        docstring = docstring_match.group(1)[:200] if docstring_match else "No description"
        
        return f"""
📄 {filename}
   Lines: {info['lines']}
   Functions: {', '.join(info['functions'][:10])}
   Classes: {', '.join(info['classes'][:5])}
   Description: {docstring}
"""
    
    def answer_question(self, question):
        """Answer questions about the code base"""
        question_lower = question.lower()
        
        if "how many" in question_lower and "function" in question_lower:
            total_functions = sum(len(info['functions']) for info in self.code_files.values())
            return f"I have {total_functions} functions across {len(self.code_files)} source files."
        
        elif "largest" in question_lower or "biggest" in question_lower:
            largest = max(self.code_files.items(), key=lambda x: x[1]['lines'])
            return f"My largest file is {largest[0]} with {largest[1]['lines']} lines."
        
        elif "what does" in question_lower and any(f in question_lower for f in ['working_replicator', 'forge', 'trust', 'memory']):
            # Find the mentioned file
            for filename in self.code_files:
                if filename.replace('.py', '') in question_lower:
                    return self.explain_file(filename)
        
        elif "search" in question_lower:
            keyword = question_lower.split('search')[-1].strip()
            results = self.search_code(keyword)
            if results:
                return "\n".join([f"  {r['file']}:{r['line']} - {r['content']}" for r in results[:5]])
        
        return "I can search my code, count functions, or explain specific files. Try: 'how many functions', 'what does working_replicator do', or 'search for trust'"

if __name__ == "__main__":
    code = CodeAccess()
    
    print("=== CODE BASE ACCESS ===")
    print(f"\n📚 Loaded {len(code.code_files)} Python files")
    
    print("\n📊 Summary:")
    for name, info in code.get_file_summary().items():
        print(f"   {name}: {info['lines']} lines, {info['functions']} functions")
    
    print("\n🔍 Testing queries:")
    print(code.answer_question("how many functions"))
    print("\n" + code.answer_question("what does working_replicator do"))
