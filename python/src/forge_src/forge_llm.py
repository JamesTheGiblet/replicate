#!/usr/bin/env python3
import random
import json
import sys
from pathlib import Path

class ForgeLLM:
    def __init__(self):
        self.patterns = {}
        self.load_c_patterns()
    
    def load_c_patterns(self):
        # Train on common C patterns from your existing code
        patterns = [
            ("function", ["int", "void", "float", "char*", "double"]),
            ("logic", ["return", "printf", "scanf", "malloc", "free"]),
            ("loop", ["for", "while", "do"]),
            ("condition", ["if", "else", "switch", "case"]),
            ("operator", ["+", "-", "*", "/", "%", "==", "!=", "<", ">"]),
            ("variable", ["int", "float", "char", "struct", "static"]),
            ("keyword", ["return", "break", "continue", "default", "typedef"])
        ]
        
        for category, items in patterns:
            for item in items:
                self.patterns[item] = category
    
    def generate_function(self, name, complexity="simple"):
        templates = {
            "simple": f'int {name}(int n) {{\n    return n * n;\n}}',
            "math": f'int {name}(int n) {{\n    if (n <= 1) return 1;\n    return n * {name}(n - 1);\n}}',
            "array": f'int {name}(int arr[], int size) {{\n    int sum = 0;\n    for (int i = 0; i < size; i++)\n        sum += arr[i];\n    return sum;\n}}',
            "pointer": f'int {name}(int *ptr, int size) {{\n    int result = 0;\n    for (int i = 0; i < size; i++)\n        result += ptr[i];\n    return result;\n}}'
        }
        return templates.get(complexity, templates["simple"])
    
    def analyze_code(self, code):
        """Analyze code and suggest improvements"""
        suggestions = []
        if "printf" in code and "\\n" not in code:
            suggestions.append("Add newline to printf statements")
        if "malloc" in code and "free" not in code:
            suggestions.append("Memory leak detected - add free()")
        if "for" in code and "++" not in code and "--" not in code:
            suggestions.append("Check loop increment/decrement")
        return suggestions
    
    def complete_prompt(self, partial_prompt):
        """Complete a partial SCP prompt"""
        completions = {
            "name": "my_function",
            "type": "function",
            "params": [{"name": "n", "type": "int"}],
            "logic": "return n * n;"
        }
        
        # Try to parse partial JSON
        try:
            partial = json.loads(partial_prompt)
            for key in completions:
                if key not in partial:
                    partial[key] = completions[key]
            return json.dumps(partial, indent=2)
        except:
            return json.dumps(completions, indent=2)

if __name__ == "__main__":
    llm = ForgeLLM()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "generate":
            name = sys.argv[2] if len(sys.argv) > 2 else "func"
            complexity = sys.argv[3] if len(sys.argv) > 3 else "simple"
            print(llm.generate_function(name, complexity))
        
        elif command == "analyze":
            code = sys.stdin.read()
            suggestions = llm.analyze_code(code)
            for s in suggestions:
                print(f"💡 {s}")
        
        elif command == "complete":
            prompt = sys.argv[2] if len(sys.argv) > 2 else "{}"
            print(llm.complete_prompt(prompt))
    else:
        print("ForgeLLM - Local AI for Code Generation")
        print("Usage:")
        print("  python forge_llm.py generate <name> [simple|math|array|pointer]")
        print("  echo 'code' | python forge_llm.py analyze")
        print("  python forge_llm.py complete '{\"name\":\"test\"}'")
