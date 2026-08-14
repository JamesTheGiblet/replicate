#!/usr/bin/env python3
"""
Capsule Executor for EXPLORER-d334
Safely executes JSON capsules containing shell commands or Python code.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

class CapsuleExecutor:
    def __init__(self):
        # Use the absolute path for Termux compatibility
        self.capsules_dir = Path("/data/data/com.termux/files/home/forge/capsules")
        if not self.capsules_dir.exists():
            self.capsules_dir = Path("capsules")
        self.audit_file = self.capsules_dir.parent / "capsule_audit.jsonl"

    def execute_capsule(self, capsule_name):
        capsule_path = self._find_capsule(capsule_name)
        if not capsule_path:
            result = {"status": "error", "message": f"Capsule '{capsule_name}' not found."}
            self._log_execution(capsule_name, "unknown", result)
            return result

        with open(capsule_path, 'r') as f:
            capsule = json.load(f)

        action = capsule.get("action", {})
        action_type = action.get("type", "command")

        if action_type == "python":
            result = self._run_python(action.get("code", ""))
        elif action_type == "command":
            result = self._run_command(action.get("command", ""))
        else:
            result = {"status": "error", "message": f"Unknown action type: {action_type}"}
            
        self._log_execution(capsule_name, action_type, result)
        return result

    def _log_execution(self, capsule_name, action_type, result):
        """Logs capsule execution details to a JSONL audit file."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "capsule_name": capsule_name,
            "action_type": action_type,
            "status": result.get("status"),
            "message": result.get("message", ""),
            "stdout": result.get("stdout", "")[:500],  # Truncate to save space
            "stderr": result.get("stderr", "")[:500]
        }
        try:
            with open(self.audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"[Audit] Failed to write to audit log: {e}")

    def _find_capsule(self, name):
        for file_path in self.capsules_dir.rglob("*.scp.json"):
            if file_path.name == f"{name}.scp.json" or file_path.name == name:
                return file_path
        return None

    def _run_python(self, code, timeout=30):
        """Executes Python code in an isolated subprocess."""
        # Python 3.8+ audit hook to prevent file deletion and subprocess spawning
        security_prologue = """import sys
def audit_hook(event, args):
    if event in ('os.remove', 'os.rmdir', 'os.rename', 'os.unlink', 'shutil.rmtree'):
        raise PermissionError(f"Capsule security policy blocked: {event}")
    if event.startswith('subprocess.') or event == 'os.system':
        raise PermissionError("Capsule security policy blocked subprocess execution")
sys.addaudithook(audit_hook)

"""
        # Write the code to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_script:
            temp_script.write(security_prologue + code)
            temp_path = temp_script.name

        try:
            # Run the script with a strict timeout
            result = subprocess.run(
                ["python3", temp_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {"status": "success" if result.returncode == 0 else "error", "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": f"Execution timed out after {timeout} seconds."}
        finally:
            os.remove(temp_path)
            
    def _run_command(self, cmd, timeout=30):
        """Executes standard shell commands."""
        # Basic blacklist to prevent accidental deletion/overwriting in shell commands
        dangerous_keywords = ['rm ', 'mv ', 'rmdir', 'unlink', '>', '>>']
        if any(keyword in cmd for keyword in dangerous_keywords):
            return {"status": "error", "message": "Command blocked by security policy."}
            
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return {"status": "success" if result.returncode == 0 else "error", "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Command timed out."}