#!/usr/bin/env python3
import os
import re
import sys

def main():
    issues = []
    
    # Scan for potential hardcoded secrets
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                        # Look for patterns that might be keys
                        if re.search(r'["\']([A-Z0-9]{20,})["\']', content):
                            issues.append(f"Potential key in {file}")
                except:
                    pass
    
    if issues:
        print("⚠️ Found potential issues:")
        for issue in issues:
            print(f"  {issue}")
        return 1
    else:
        print("✅ No hardcoded secrets found")
        print("✅ Security scanner passed")
        return 0

if __name__ == "__main__":
    sys.exit(main())
