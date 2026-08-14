#!/usr/bin/env python3
import time
import threading
import subprocess
from datetime import datetime
from pathlib import Path

class ForgeService:
    def __init__(self):
        self.running = True
    
    def log(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    def run_think(self):
        self.log("Thinking...")
        try:
            result = subprocess.run(["./forge", "think"], capture_output=True, text=True, timeout=30)
            if result.stdout:
                self.log(f"Thought: {result.stdout[:80]}")
        except Exception as e:
            self.log(f"Error: {e}")
    
    def run_dream(self):
        self.log("Dreaming...")
        try:
            result = subprocess.run(["./forge", "dream"], capture_output=True, text=True, timeout=30)
            if result.stdout:
                self.log(f"Dream: {result.stdout[:80]}")
        except Exception as e:
            self.log(f"Error: {e}")
    
    def run_health(self):
        self.log("Health check...")
        try:
            result = subprocess.run(["./forge", "health"], capture_output=True, text=True, timeout=10)
            if "HEALTHY" in result.stdout:
                self.log("System healthy")
            else:
                self.log("Issues detected")
        except Exception as e:
            self.log(f"Error: {e}")
    
    def start(self):
        self.log("Service starting")
        
        def scheduler():
            last_think = 0
            last_dream = 0
            last_health = 0
            
            while self.running:
                now = time.time()
                if now - last_think > 1800:
                    self.run_think()
                    last_think = now
                if now - last_dream > 3600:
                    self.run_dream()
                    last_dream = now
                if now - last_health > 900:
                    self.run_health()
                    last_health = now
                time.sleep(60)
        
        thread = threading.Thread(target=scheduler, daemon=True)
        thread.start()
        
        self.log("Forge is alive")
        
        try:
            while self.running:
                time.sleep(10)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        self.log("Service stopping")
        self.running = False

if __name__ == "__main__":
    service = ForgeService()
    service.start()
