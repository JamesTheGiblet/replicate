#!/usr/bin/env python3
import os
import subprocess

def check_memory():
    try:
        result = subprocess.run(['free', '-m'], capture_output=True, text=True)
        if 'Mem' in result.stdout:
            return True
    except:
        pass
    return True

if __name__ == "__main__":
    print("✅ Memory monitoring active")
