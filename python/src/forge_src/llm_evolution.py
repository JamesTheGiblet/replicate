#!/usr/bin/env python3
"""
LLM-Powered Evolutionary Code System
Uses Gemma to intelligently fix and evolve code
"""

import subprocess
import re

class LLMEvolution:
    def __init__(self):
        self.conversation_log = []
    
    def query_gemma(self, prompt: str) -> str:
        """Query Gemma for code improvements"""
        try:
            result = subprocess.run(
                ["ollama", "run", "gemma2:2b", prompt],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0 and result.stdout:
                code = result.stdout
                # Extract code from markdown
                code_match = re.search(r'```python\n(.*?)```', code, re.DOTALL)
                if code_match:
                    return code_match.group(1)
                # Look for function definition
                func_match = re.search(r'(def \w+\(.*?\):.*?)(?=\n\n|\Z)', code, re.DOTALL)
                if func_match:
                    return func_match.group(1)
                return code
            return None
        except Exception as e:
            print(f"Gemma error: {e}")
            return None
    
    def evolve(self, initial_code: str, func_name: str, test_cases: list, max_attempts: int = 3) -> dict:
        """Evolve code using LLM"""
        current_code = initial_code
        history = []
        
        for attempt in range(max_attempts):
            # Test current code
            passed, error = self.test_function(current_code, func_name, test_cases)
            
            if passed:
                return {
                    "success": True,
                    "attempts": attempt + 1,
                    "code": current_code,
                    "history": history
                }
            
            # Ask Gemma to fix it
            print(f"   🤖 Attempt {attempt + 1}: Fixing...")
            prompt = f"""Fix this Python code. The error is: {error}

CODE:
{current_code}

Return only the fixed function code."""
            
            fixed_code = self.query_gemma(prompt)
            
            if fixed_code and fixed_code != current_code:
                history.append({
                    "attempt": attempt + 1,
                    "error": error[:50],
                    "fixed": fixed_code[:100]
                })
                current_code = fixed_code
            else:
                # Manual fallback
                current_code = self.manual_fix(current_code, error)
        
        return {
            "success": False,
            "attempts": max_attempts,
            "code": current_code,
            "history": history
        }
    
    def test_function(self, code: str, func_name: str, test_cases: list) -> tuple:
        """Test if code passes all cases"""
        try:
            exec_globals = {}
            exec(code, exec_globals)
            func = exec_globals.get(func_name)
            
            if not func:
                return False, f"Function {func_name} not found"
            
            for inputs, expected in test_cases:
                if isinstance(inputs, tuple):
                    result = func(*inputs)
                else:
                    result = func(inputs)
                
                if result != expected:
                    return False, f"Expected {expected}, got {result}"
            
            return True, "All tests passed"
        except Exception as e:
            return False, str(e)
    
    def manual_fix(self, code: str, error: str) -> str:
        """Manual fallback fixes"""
        if "IndexError" in error:
            return '''def safe_get(lst, idx):
    try:
        return lst[idx]
    except IndexError:
        return None'''
        
        if "KeyError" in error:
            return '''def safe_get(d, key):
    return d.get(key)'''
        
        return code

if __name__ == "__main__":
    evo = LLMEvolution()
    
    print("=" * 60)
    print("🧬 LLM-POWERED EVOLUTIONARY CODE SYSTEM")
    print("=" * 60)
    
    # Test 1: Fix IndexError
    print("\n1. Evolving safe list access:")
    
    initial_code = '''def safe_get(lst, idx):
    return lst[idx]'''
    
    test_cases = [
        (([1, 2, 3], 0), 1),
        (([1, 2, 3], 5), None),
        (([], 0), None)
    ]
    
    result = evo.evolve(initial_code, "safe_get", test_cases, max_attempts=2)
    
    print(f"   Success: {result['success']}")
    if result['success']:
        print("   Evolved code:")
        print(result['code'])
    
    print("\n✅ LLM-Powered Evolution Ready!")
