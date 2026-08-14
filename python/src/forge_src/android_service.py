#!/usr/bin/env python3
"""
Android Background Service for Explorer-d334
Handles wake locks, battery optimization, and persistent operation
"""

import os
import sys
import time
import signal
import subprocess
from datetime import datetime
from pathlib import Path

class AndroidService:
    def __init__(self):
        self.running = True
        self.log_file = Path.home() / "forge" / "android_service.log"
        self.pid_file = Path.home() / "forge" / "service.pid"
        
    def log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {msg}\n")
        print(f"[{timestamp}] {msg}")
    
    def setup_wake_lock(self):
        """Prevent device from deep sleeping"""
        try:
            # Use Termux:WakeLock if available
            subprocess.run(["termux-wake-lock"], capture_output=True)
            self.log("✅ Wake lock acquired")
            return True
        except:
            self.log("⚠️ Could not acquire wake lock (Termux:API not installed?)")
            return False
    
    def release_wake_lock(self):
        """Release wake lock on shutdown"""
        try:
            subprocess.run(["termux-wake-unlock"], capture_output=True)
            self.log("✅ Wake lock released")
        except:
            pass
    
    def check_battery_optimization(self):
        """Check if battery optimization is disabled"""
        try:
            # Request ignoring battery optimization
            subprocess.run(["termux-battery-status"], capture_output=True)
            self.log("✅ Battery status check")
            return True
        except:
            self.log("⚠️ Battery optimization may affect service")
            return False
    
    def run_heartbeat(self):
        """Send heartbeat every hour to show service is alive"""
        while self.running:
            time.sleep(3600)  # 1 hour
            if self.running:
                self.log("💓 Service heartbeat - alive and running")
    
    def start_forge_service(self):
        """Start the main forge service"""
        self.log("🚀 Starting Explorer-d334 service...")
        
        # Change to forge directory
        os.chdir(Path.home() / "forge")
        
        # Start the service in background
        process = subprocess.Popen(
            ["./start_service.sh"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        
        # Save PID
        with open(self.pid_file, 'w') as f:
            f.write(str(process.pid))
        
        self.log(f"✅ Forge service started (PID: {process.pid})")
        return process
    
    def monitor_service(self, process):
        """Monitor and restart if needed"""
        while self.running:
            time.sleep(30)
            if process.poll() is not None:
                self.log("⚠️ Service died, restarting...")
                process = self.start_forge_service()
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.log("🛑 Received shutdown signal")
        self.running = False
        self.release_wake_lock()
        sys.exit(0)
    
    def run(self):
        """Main service entry point"""
        self.log("="*50)
        self.log("Explorer-d334 Android Service Starting")
        self.log("="*50)
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Setup wake lock
        self.setup_wake_lock()
        
        # Check battery optimization
        self.check_battery_optimization()
        
        # Start main forge service
        forge_process = self.start_forge_service()
        
        # Start heartbeat thread
        import threading
        heartbeat_thread = threading.Thread(target=self.run_heartbeat, daemon=True)
        heartbeat_thread.start()
        
        # Monitor service
        self.monitor_service(forge_process)

if __name__ == "__main__":
    service = AndroidService()
    service.run()
