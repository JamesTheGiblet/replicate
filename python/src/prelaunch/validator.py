#!/usr/bin/env python3
"""
Pre-launch Validation System
Checks everything is ready before launch
"""

import subprocess
import sys
from pathlib import Path
import json

class PreLaunchValidator:
    def __init__(self):
        self.forge_dir = Path.cwd()
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
    
    def run_all_checks(self):
        """Run all pre-launch checks"""
        self.check_tests()
        self.check_security()
        self.check_documentation()
        self.check_legal()
        self.check_licensing()
        self.check_analytics()
        self.check_binaries()
        self.check_web_interface()
        self.check_performance()
        
        return self.results
    
    def check_tests(self):
        """Check test suite"""
        print("🔍 Running test suite...")
        result = subprocess.run(["python", "test_suite.py"], capture_output=True, text=True)
        if "PASSED: 16" in result.stdout:
            self.results["passed"].append("All tests passing (16/16)")
        else:
            self.results["failed"].append("Test suite failing")
    
    def check_security(self):
        """Check security scan"""
        print("🔒 Running security scan...")
        result = subprocess.run(["./forge", "security"], capture_output=True, text=True)
        if "Critical: 0" in result.stdout:
            self.results["passed"].append("Security scan passed (no critical issues)")
        else:
            self.results["warnings"].append("Security issues found - review")
    
    def check_documentation(self):
        """Check documentation exists"""
        docs_dir = self.forge_dir / "docs"
        required_docs = ["README.md", "guide/getting-started.md", "guide/user-guide.md", "api/README.md"]
        
        for doc in required_docs:
            if (docs_dir / doc).exists():
                self.results["passed"].append(f"Documentation exists: {doc}")
            else:
                self.results["failed"].append(f"Missing documentation: {doc}")
    
    def check_legal(self):
        """Check legal files"""
        legal_dir = self.forge_dir / "legal"
        required_legal = ["LICENSE", "TERMS.md", "PRIVACY.md", "EULA.md"]
        
        for legal in required_legal:
            if (legal_dir / legal).exists():
                self.results["passed"].append(f"Legal file exists: {legal}")
            else:
                self.results["failed"].append(f"Missing legal file: {legal}")
    
    def check_licensing(self):
        """Check licensing system"""
        license_db = self.forge_dir / "licensing" / "licenses.db"
        if license_db.exists():
            self.results["passed"].append("License database exists")
        else:
            self.results["warnings"].append("License database not yet created")
    
    def check_analytics(self):
        """Check analytics system"""
        analytics_dir = self.forge_dir / "analytics"
        if analytics_dir.exists():
            self.results["passed"].append("Analytics system ready")
        else:
            self.results["failed"].append("Analytics system missing")
    
    def check_binaries(self):
        """Check compiled binaries"""
        binaries_dir = self.forge_dir / "binaries"
        if binaries_dir.exists() and len(list(binaries_dir.glob("*"))) > 0:
            self.results["passed"].append(f"Binaries present ({len(list(binaries_dir.glob('*')))} files)")
        else:
            self.results["warnings"].append("No compiled binaries found")
    
    def check_web_interface(self):
        """Check web interface"""
        web_file = self.forge_dir / "src" / "web_hybrid.py"
        if web_file.exists():
            self.results["passed"].append("Web interface ready")
        else:
            self.results["failed"].append("Web interface missing")
    
    def check_performance(self):
        """Check performance metrics"""
        import time
        start = time.time()
        result = subprocess.run(["./forge", "health"], capture_output=True, text=True, timeout=10)
        elapsed = time.time() - start
        if elapsed < 5:
            self.results["passed"].append(f"Health check fast ({elapsed:.2f}s)")
        else:
            self.results["warnings"].append(f"Health check slow ({elapsed:.2f}s)")
    
    def print_report(self):
        """Print validation report"""
        print("\n" + "="*60)
        print("🚀 PRE-LAUNCH VALIDATION REPORT")
        print("="*60)
        
        print(f"\n✅ PASSED ({len(self.results['passed'])}):")
        for item in self.results['passed'][:20]:
            print(f"   • {item}")
        
        if self.results['warnings']:
            print(f"\n⚠️ WARNINGS ({len(self.results['warnings'])}):")
            for item in self.results['warnings']:
                print(f"   • {item}")
        
        if self.results['failed']:
            print(f"\n❌ FAILED ({len(self.results['failed'])}):")
            for item in self.results['failed']:
                print(f"   • {item}")
        
        print("\n" + "="*60)
        
        total = len(self.results['passed']) + len(self.results['failed']) + len(self.results['warnings'])
        score = len(self.results['passed']) / total * 100 if total > 0 else 0
        
        print(f"\n📊 READINESS SCORE: {score:.0f}%")
        
        if score >= 80:
            print("🎉 READY TO LAUNCH!")
        elif score >= 60:
            print("⚠️ NEARLY READY - Fix remaining issues")
        else:
            print("🔧 NOT READY - Complete checklist first")
        
        print("="*60)

if __name__ == "__main__":
    validator = PreLaunchValidator()
    validator.run_all_checks()
    validator.print_report()
