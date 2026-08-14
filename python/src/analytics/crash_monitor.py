#!/usr/bin/env python3
"""
Crash Monitoring System - Local only, user controls sharing
"""

import sys
import traceback
from datetime import datetime
from pathlib import Path
import json

class CrashMonitor:
    def __init__(self):
        self.forge_dir = Path.cwd()
        self.crash_dir = self.forge_dir / "analytics" / "crashes"
        self.crash_dir.mkdir(parents=True, exist_ok=True)
        
        # Check for telemetry opt-in
        self.opt_in_file = self.forge_dir / "analytics" / ".opt_in"
    
    def can_share(self):
        """Check if user has allowed sharing crash data"""
        return self.opt_in_file.exists()
    
    def capture_exception(self, e, context=None):
        """Capture an exception for later review"""
        import hashlib
        
        error_str = str(e)
        trace = traceback.format_exc()
        
        crash_id = hashlib.md5(f"{datetime.now().isoformat()}{error_str}".encode()).hexdigest()[:8]
        crash_file = self.crash_dir / f"crash_{crash_id}.json"
        
        crash_data = {
            "crash_id": crash_id,
            "timestamp": datetime.now().isoformat(),
            "error_type": type(e).__name__,
            "error_message": error_str,
            "traceback": trace,
            "context": context or {},
            "can_share": self.can_share(),
            "shared": False
        }
        
        with open(crash_file, 'w') as f:
            json.dump(crash_data, f, indent=2)
        
        return crash_id
    
    def get_crashes(self):
        """Get list of crashes"""
        crashes = []
        for crash_file in self.crash_dir.glob("*.json"):
            try:
                with open(crash_file, 'r') as f:
                    crashes.append(json.load(f))
            except:
                pass
        return sorted(crashes, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    def clear_crashes(self):
        """Clear all crash reports"""
        for crash_file in self.crash_dir.glob("*.json"):
            crash_file.unlink()
        print("✅ All crash reports cleared")

if __name__ == "__main__":
    monitor = CrashMonitor()
    crashes = monitor.get_crashes()
    
    print(f"📊 Local Crashes: {len(crashes)}")
    for crash in crashes[:5]:
        print(f"   {crash['timestamp'][:19]} - {crash['error_type']}: {crash['error_message'][:50]}")
    
    if crashes:
        print(f"\n💾 Crash reports saved in: analytics/crashes/")
        print(f"   Share consent: {'Yes' if monitor.can_share() else 'No'}")
```

Add analytics commands to forge

cat >> forge << 'EOF'

Analytics & Monitoring commands

telemetry-on)
python -c "
from analytics.telemetry import PrivacyTelemetry
t = PrivacyTelemetry()
t.opt_in()
t.close()
"
;;
telemetry-off)
python -c "
from analytics.telemetry import PrivacyTelemetry
t = PrivacyTelemetry()
t.opt_out()
t.close()
"
;;
telemetry-status)
python -c "
from analytics.telemetry import PrivacyTelemetry
t = PrivacyTelemetry()
print('='50)
print('TELEMETRY STATUS')
print('='50)
print(f'Opted in: {t.is_opted_in()}')
if t.is_opted_in():
stats = t.get_stats()
print(f'Total events: {stats.get(\"total_events\", 0)}')
print(f'Total sessions: {stats.get(\"total_sessions\", 0)}')
t.close()
"
;;
crashes)
python analytics/crash_monitor.py
;;
crashes-clear)
python -c "
from analytics.crash_monitor import CrashMonitor
m = CrashMonitor()
m.clear_crashes()
"
;;
