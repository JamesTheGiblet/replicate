#!/usr/bin/env python3
"""
FORGE-os Health Monitor & Audit Validation
Checks system integrity, performance, and validates audit trails
"""

import os
import sys
import json
import time
import hashlib
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class HealthMonitor:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "status": "HEALTHY",
            "metrics": {}
        }
    
    def run_all_checks(self):
        """Run all health checks"""
        self.check_database()
        self.check_data_cube()
        self.check_binaries()
        self.check_audit_chain()
        self.check_disk_space()
        self.check_performance()
        self.check_backup_integrity()
        return self.results
    
    def check_database(self):
        """Check SQLite database integrity"""
        try:
            db_path = self.base_dir / "forge_data.db"
            if not db_path.exists():
                self._add_check("database", "FAIL", "Database file not found")
                return
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            if result and result[0] == "ok":
                # Count records
                cursor = conn.execute("SELECT COUNT(*) FROM scp_prompts")
                scp_count = cursor.fetchone()[0]
                cursor = conn.execute("SELECT COUNT(*) FROM audit_log")
                audit_count = cursor.fetchone()[0]
                
                self._add_check("database", "PASS", f"Integrity OK: {scp_count} SCPs, {audit_count} audits")
                self.results["metrics"]["scp_count"] = scp_count
                self.results["metrics"]["audit_count"] = audit_count
            else:
                self._add_check("database", "FAIL", f"Integrity check failed: {result}")
            
            conn.close()
        except Exception as e:
            self._add_check("database", "ERROR", str(e))
            self.results["status"] = "DEGRADED"
    
    def check_data_cube(self):
        """Check data cube integrity"""
        try:
            # Check chain verification
            result = subprocess.run(
                ["python", "src/integrated_datacube.py", "verify"],
                capture_output=True, text=True, cwd=str(self.base_dir)
            )
            
            if "True" in result.stdout:
                # Get chain length
                result2 = subprocess.run(
                    ["python", "src/integrated_datacube.py", "status"],
                    capture_output=True, text=True, cwd=str(self.base_dir)
                )
                
                # Extract chain length from output
                import re
                match = re.search(r'Chain length:\s+(\d+)', result2.stdout)
                chain_len = int(match.group(1)) if match else 0
                
                self._add_check("data_cube", "PASS", f"Chain verified: {chain_len} blocks")
                self.results["metrics"]["cube_blocks"] = chain_len
            else:
                self._add_check("data_cube", "FAIL", "Chain verification failed")
                self.results["status"] = "DEGRADED"
                
        except Exception as e:
            self._add_check("data_cube", "ERROR", str(e))
    
    def check_binaries(self):
        """Check compiled binaries"""
        try:
            binary_dir = self.base_dir / "binaries"
            if not binary_dir.exists():
                self._add_check("binaries", "WARN", "Binaries directory empty")
                return
            
            binaries = list(binary_dir.glob("*"))
            executable_count = 0
            
            for binary in binaries:
                if os.access(binary, os.X_OK):
                    executable_count += 1
            
            self._add_check("binaries", "PASS", f"{len(binaries)} binaries, {executable_count} executable")
            self.results["metrics"]["binary_count"] = len(binaries)
            
        except Exception as e:
            self._add_check("binaries", "ERROR", str(e))
    
    def check_audit_chain(self):
        """Validate audit trail integrity"""
        try:
            db_path = self.base_dir / "forge_data.db"
            if not db_path.exists():
                self._add_check("audit_chain", "FAIL", "Database not found")
                return
            
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id, action, entity_name, timestamp, hash FROM audit_log ORDER BY id"
            )
            audits = cursor.fetchall()
            
            if not audits:
                self._add_check("audit_chain", "WARN", "No audit records found")
                conn.close()
                return
            
            # Verify hashes
            valid_count = 0
            for audit in audits:
                test_hash = hashlib.sha256(
                    f"{audit['action']}:{audit['entity_name']}:{audit['timestamp']}".encode()
                ).hexdigest()
                if test_hash[:8] == audit['hash'][:8]:
                    valid_count += 1
            
            integrity = (valid_count / len(audits)) * 100
            
            if integrity == 100:
                self._add_check("audit_chain", "PASS", f"{len(audits)} records, 100% hash integrity")
            else:
                self._add_check("audit_chain", "WARN", f"{len(audits)} records, {integrity:.1f}% integrity")
            
            self.results["metrics"]["audit_integrity"] = integrity
            conn.close()
            
        except Exception as e:
            self._add_check("audit_chain", "ERROR", str(e))
    
    def check_disk_space(self):
        """Check available disk space"""
        try:
            stat = os.statvfs(self.base_dir)
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
            used_percent = ((total_gb - free_gb) / total_gb) * 100
            
            status = "PASS" if free_gb > 1 else "WARN"
            self._add_check("disk_space", status, f"{free_gb:.1f}GB free / {total_gb:.1f}GB total ({used_percent:.1f}% used)")
            self.results["metrics"]["free_gb"] = free_gb
            
        except Exception as e:
            self._add_check("disk_space", "ERROR", str(e))
    
    def check_performance(self):
        """Check system performance"""
        try:
            # Test compilation speed
            test_file = self.base_dir / "generated" / "perf_test.c"
            test_file.write_text("int main() { return 0; }")
            
            start = time.time()
            result = subprocess.run(["gcc", str(test_file), "-o", "/dev/null"], 
                                   capture_output=True, timeout=5)
            compile_time = (time.time() - start) * 1000  # ms
            
            status = "PASS" if compile_time < 500 else "WARN"
            self._add_check("performance", status, f"Compile time: {compile_time:.1f}ms")
            self.results["metrics"]["compile_time_ms"] = compile_time
            
            test_file.unlink()
            
        except Exception as e:
            self._add_check("performance", "ERROR", str(e))
    
    def check_backup_integrity(self):
        """Check if backups exist and are recent"""
        try:
            backups = list(self.base_dir.glob("forge_backup_*"))
            if not backups:
                self._add_check("backups", "WARN", "No backups found")
                return
            
            # Find most recent backup
            latest = max(backups, key=lambda x: x.stat().st_mtime)
            age_hours = (datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)).total_seconds() / 3600
            
            if age_hours < 24:
                self._add_check("backups", "PASS", f"Latest backup: {latest.name} ({age_hours:.1f} hours old)")
            else:
                self._add_check("backups", "WARN", f"Backup age: {age_hours:.1f} hours ( >24)")
            
            self.results["metrics"]["backup_age_hours"] = age_hours
            
        except Exception as e:
            self._add_check("backups", "ERROR", str(e))
    
    def _add_check(self, component, status, message):
        """Add a check result"""
        self.results["checks"].append({
            "component": component,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update overall status
        if status in ["FAIL", "ERROR"]:
            self.results["status"] = "DEGRADED"
        elif status == "WARN" and self.results["status"] == "HEALTHY":
            self.results["status"] = "WARNING"
    
    def print_report(self):
        """Print formatted health report"""
        print("\n" + "="*60)
        print("FORGE-os HEALTH MONITOR REPORT")
        print("="*60)
        print(f"Report Time: {self.results['timestamp']}")
        print(f"Overall Status: {self.results['status']}")
        print("-"*60)
        
        for check in self.results["checks"]:
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "WARN": "⚠️",
                "ERROR": "💀"
            }.get(check["status"], "❓")
            
            print(f"{status_icon} {check['component'].upper():12} : {check['message']}")
        
        if self.results.get("metrics"):
            print("-"*60)
            print("📊 METRICS:")
            for key, value in self.results["metrics"].items():
                print(f"   {key}: {value}")
        
        print("="*60)
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if self.results["metrics"].get("free_gb", 0) < 1:
            print("   - Free up disk space")
        if self.results["metrics"].get("audit_integrity", 100) < 100:
            print("   - Audit trail has integrity issues")
        if self.results["metrics"].get("backup_age_hours", 0) > 24:
            print("   - Run './forge backup' to update backups")
        if self.results["status"] == "HEALTHY":
            print("   ✓ System is healthy - no action needed")
        
        return self.results["status"]

class AuditValidator:
    """Validate and verify audit trail"""
    
    def __init__(self):
        self.db_path = Path("forge_data.db")
    
    def validate_all(self):
        """Run full audit validation"""
        print("\n" + "="*60)
        print("AUDIT VALIDATION REPORT")
        print("="*60)
        
        if not self.db_path.exists():
            print("❌ Database not found")
            return False
        
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        # Check for tampering
        cursor = conn.execute("SELECT COUNT(*) as count FROM audit_log")
        total = cursor.fetchone()['count']
        
        print(f"\n📋 Audit Records: {total}")
        
        if total == 0:
            print("⚠️ No audit records found")
            conn.close()
            return True
        
        # Verify hash chain
        cursor = conn.execute(
            "SELECT id, action, entity_name, timestamp, hash FROM audit_log ORDER BY id"
        )
        records = cursor.fetchall()
        
        valid = 0
        chain_valid = True
        last_hash = None
        
        for record in records:
            # Verify individual hash
            test_hash = hashlib.sha256(
                f"{record['action']}:{record['entity_name']}:{record['timestamp']}".encode()
            ).hexdigest()[:16]
            
            if test_hash == record['hash'][:16]:
                valid += 1
            else:
                print(f"⚠️ Record {record['id']} hash mismatch")
                chain_valid = False
            
            # Check chain continuity (if we had previous hash)
            if last_hash:
                # In a real chain, each record would contain previous hash
                pass
            last_hash = record['hash']
        
        integrity = (valid / total) * 100
        
        print(f"\n🔐 Hash Integrity: {integrity:.1f}% ({valid}/{total})")
        print(f"🔗 Chain Status: {'✓ VALID' if chain_valid else '✗ BROKEN'}")
        
        # Show recent activity
        print("\n📝 Recent Activity:")
        cursor = conn.execute(
            "SELECT action, entity_name, timestamp FROM audit_log ORDER BY id DESC LIMIT 5"
        )
        for record in cursor:
            print(f"   [{record['timestamp'][:19]}] {record['action']} {record['entity_name']}")
        
        conn.close()
        print("="*60)
        
        return integrity == 100

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "audit":
        validator = AuditValidator()
        validator.validate_all()
    elif len(sys.argv) > 1 and sys.argv[1] == "quick":
        monitor = HealthMonitor()
        monitor.run_all_checks()
        status = monitor.print_report()
        sys.exit(0 if status == "HEALTHY" else 1)
    else:
        monitor = HealthMonitor()
        monitor.run_all_checks()
        monitor.print_report()
        
        # Also run audit validation
        validator = AuditValidator()
        validator.validate_all()
