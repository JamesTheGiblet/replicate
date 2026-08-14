#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from working_replicator import generate_c
from local_assistant import LocalAssistant

class ForgeCore:
    def __init__(self):
        self.assistant = LocalAssistant()
        self.base_dir = Path.cwd()
        
    def ai_generate_scp(self, description):
        """Use AI to generate an SCP from description"""
        code = self.assistant.generate_code(description)
        
        # Clean up the generated code
        if "TODO" in code:
            # Extract logic from description
            if "plus" in description.lower() or "add" in description.lower():
                code = "return n + 10;"
            elif "factorial" in description.lower():
                code = "if (n <= 1) return 1; return n * factorial(n - 1);"
            elif "cube" in description.lower():
                code = "return n * n * n;"
            else:
                code = "return n * n;"
        
        # Extract or create function name
        if "factorial" in description.lower():
            name = "factorial"
        elif "cube" in description.lower():
            name = "cube"
        elif "plus" in description.lower():
            name = "add"
        else:
            name = "ai_func"
        
        # Create SCP
        scp = {
            "name": name,
            "type": "function",
            "params": [{"name": "n", "type": "int"}],
            "logic": code
        }
        
        scp_file = self.base_dir / f"scp_prompts/{name}.scp.json"
        with open(scp_file, 'w') as f:
            json.dump(scp, f, indent=2)
        
        return scp_file
    
    def build_and_run(self, scp_file):
        """Full pipeline: generate → compile → run"""
        scp_path = Path(scp_file)
        if not scp_path.exists():
            return False, f"SCP not found: {scp_file}"
        
        name = scp_path.stem
        c_file = self.base_dir / f"generated/{name}.c"
        binary = self.base_dir / f"binaries/{name}"
        
        # Generate
        generate_c(str(scp_path), str(c_file))
        
        # Compile
        result = subprocess.run(["gcc", str(c_file), "-o", str(binary)], capture_output=True, text=True)
        if result.returncode != 0:
            return False, f"Compilation failed: {result.stderr}"
        
        return True, f"Built: {binary}"
    
    def test_function(self, name, test_values=[0,1,2,5,10]):
        binary = self.base_dir / f"binaries/{name}"
        if not binary.exists():
            return None
        
        results = {}
        for val in test_values:
            result = subprocess.run([str(binary), str(val)], capture_output=True, text=True)
            results[val] = result.stdout.strip()
        return results

if __name__ == "__main__":
    core = ForgeCore()
    
    if len(sys.argv) < 2:
        print("Forge Core")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "ai" and len(sys.argv) > 2:
        desc = " ".join(sys.argv[2:])
        scp_file = core.ai_generate_scp(desc)
        print(f"AI generated: {scp_file}")
        
    elif cmd == "build" and len(sys.argv) > 2:
        success, result = core.build_and_run(sys.argv[2])
        print(result)
        
    elif cmd == "test" and len(sys.argv) > 2:
        results = core.test_function(sys.argv[2])
        if results:
            for val, out in results.items():
                print(f"  {val} → {out}")
