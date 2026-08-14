#!/usr/bin/env python3
import json
import subprocess
import sys
import os
from pathlib import Path

class ForgeLoop:
    def __init__(self):
        self.build_dir = Path("forge_workspace/build")
        self.build_dir.mkdir(parents=True, exist_ok=True)
        
    def run(self, scp_path):
        print(f"\n🔨 Starting Forge replication...")
        
        # Step 1: Generate C code
        print(f"📝 Generating C code from {scp_path}")
        c_file = self.build_dir / "program.c"
        
        gen_result = subprocess.run([
            sys.executable, "code_generator.py",
            scp_path, str(c_file)
        ], capture_output=True, text=True)
        
        if gen_result.returncode != 0:
            print(f"❌ Generator failed: {gen_result.stderr}")
            return False
        
        if not c_file.exists():
            print(f"❌ Generator didn't create {c_file}")
            return False
            
        print(f"✅ Generated {c_file}")
        
        # Step 2: Compile
        print(f"🔨 Compiling...")
        binary = self.build_dir / "program"
        
        compile_result = subprocess.run([
            "gcc", str(c_file), "-o", str(binary)
        ], capture_output=True, text=True)
        
        if compile_result.returncode != 0:
            print(f"❌ Compilation failed:\n{compile_result.stderr}")
            return False
        
        print(f"✅ Compiled to {binary}")
        
        # Step 3: Run tests
        print(f"🧪 Running tests...")
        os.chmod(binary, 0o755)
        
        test_cases = [
            (["0"], "0"),
            (["1"], "1"), 
            (["5"], "5"),
            (["10"], "55")
        ]
        
        all_passed = True
        
        for args, expected in test_cases:
            result = subprocess.run([str(binary)] + args, 
                                  capture_output=True, text=True, timeout=2)
            
            output = result.stdout.strip()
            
            if output == expected:
                print(f"  ✅ Input {args[0]:2} → {output}")
            else:
                print(f"  ❌ Input {args[0]:2} → got {output}, expected {expected}")
                all_passed = False
        
        # Step 4: Save if successful
        if all_passed:
            print(f"\n🎉 SUCCESS! Forge replicated.")
            
            # Save to successful directory
            success_dir = Path("forge_workspace/successful")
            success_dir.mkdir(exist_ok=True)
            
            import shutil
            from datetime import datetime
            
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy(c_file, success_dir / f"fibonacci_{ts}.c")
            shutil.copy(binary, success_dir / f"fibonacci_{ts}.bin")
            
            print(f"💾 Saved to {success_dir}/")
            return True
        else:
            print(f"\n💀 Tests failed. Need to fix.")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python forge_loop.py <scp_file.json>")
        sys.exit(1)
    
    loop = ForgeLoop()
    success = loop.run(sys.argv[1])
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

