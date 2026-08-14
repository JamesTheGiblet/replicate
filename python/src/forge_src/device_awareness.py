#!/usr/bin/env python3
"""
Device Awareness for Explorer-d334
Knows what hardware it's running on and adapts behavior
"""

import os
import platform
import subprocess
import json
from pathlib import Path

class DeviceAwareness:
    def __init__(self):
        self.device_info = self.detect_device()
    
    def detect_device(self):
        """Detect current device hardware"""
        info = {
            "device_name": None,
            "device_type": None,
            "hardware": None,
            "os": None,
            "capabilities": [],
            "sensors": [],
            "limitations": []
        }
        
        # Check if running on Termux (Android)
        if "com.termux" in os.environ.get("PREFIX", ""):
            info["device_type"] = "android_termux"
            info["device_name"] = self.get_android_device_name()
            info["os"] = f"Android {self.get_android_version()}"
            info["hardware"] = self.get_android_hardware()
            info["capabilities"] = self.get_android_capabilities()
            info["sensors"] = self.get_android_sensors()
            info["limitations"] = ["limited_battery", "mobile_network", "thermal_throttling"]
        
        # Check if running on Windows
        elif platform.system() == "Windows":
            info["device_type"] = "windows"
            info["device_name"] = platform.node()
            info["os"] = f"Windows {platform.release()}"
            info["hardware"] = self.get_windows_hardware()
            info["capabilities"] = ["full_desktop", "gpu", "large_storage"]
            info["limitations"] = ["not_portable", "power_dependent"]
        
        # Check if running on Linux (non-Android)
        elif platform.system() == "Linux":
            info["device_type"] = "linux"
            info["device_name"] = platform.node()
            info["os"] = f"Linux {platform.release()}"
            info["capabilities"] = ["server_capable", "network_services"]
        
        # Check if running on macOS
        elif platform.system() == "Darwin":
            info["device_type"] = "macos"
            info["device_name"] = platform.node()
            info["os"] = f"macOS {platform.mac_ver()[0]}"
            info["capabilities"] = ["unix_like", "metal_gpu"]
        
        else:
            info["device_type"] = "unknown"
            info["device_name"] = platform.node()
            info["os"] = platform.system()
        
        return info
    
    def get_android_device_name(self):
        """Get Android device model"""
        try:
            # Try to get device model from system properties
            result = subprocess.run(
                ["getprop", "ro.product.model"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
        
        try:
            result = subprocess.run(
                ["getprop", "ro.product.manufacturer"],
                capture_output=True,
                text=True,
                timeout=2
            )
            manufacturer = result.stdout.strip()
            if manufacturer:
                return manufacturer
        except:
            pass
        
        return "Samsung S24 Ultra"  # Default assumption
    
    def get_android_version(self):
        """Get Android OS version"""
        try:
            result = subprocess.run(
                ["getprop", "ro.build.version.release"],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.stdout.strip() or "Unknown"
        except:
            return "Unknown"
    
    def get_android_hardware(self):
        """Get Android hardware info"""
        hardware = {}
        try:
            # CPU info
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "Hardware" in line or "Processor" in line:
                        key, value = line.split(":", 1)
                        hardware[key.strip()] = value.strip()
        except:
            pass
        
        try:
            # Memory info
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemTotal" in line:
                        mem = line.split(":")[1].strip()
                        hardware["RAM"] = mem
        except:
            pass
        
        return hardware
    
    def get_android_capabilities(self):
        """Detect Android device capabilities"""
        capabilities = []
        
        # Check for features
        features = [
            "camera", "gps", "nfc", "bluetooth", "wifi", 
            "cellular", "fingerprint", "heart_rate", "accelerometer"
        ]
        
        # Check each feature (simplified)
        for feature in features:
            try:
                if os.path.exists(f"/sys/class/{feature}"):
                    capabilities.append(feature)
            except:
                pass
        
        # Add common capabilities for S24 Ultra
        capabilities.extend(["touch_screen", "mobile_data", "notifications"])
        
        return list(set(capabilities))
    
    def get_android_sensors(self):
        """Get available sensors on Android"""
        sensors = []
        sensor_paths = [
            "/sys/class/sensors",
            "/sys/bus/iio/devices"
        ]
        
        for path in sensor_paths:
            if os.path.exists(path):
                try:
                    for item in os.listdir(path):
                        if "accel" in item.lower():
                            sensors.append("accelerometer")
                        elif "gyro" in item.lower():
                            sensors.append("gyroscope")
                        elif "light" in item.lower():
                            sensors.append("light_sensor")
                        elif "prox" in item.lower():
                            sensors.append("proximity")
                except:
                    pass
        
        # S24 Ultra known sensors
        known_sensors = [
            "accelerometer", "gyroscope", "magnetometer", 
            "proximity", "light_sensor", "barometer",
            "fingerprint", "heart_rate"
        ]
        
        return known_sensors
    
    def get_windows_hardware(self):
        """Get Windows hardware info"""
        hardware = {}
        try:
            result = subprocess.run(
                ["wmic", "cpu", "get", "name"],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                hardware["CPU"] = lines[1].strip()
        except:
            pass
        
        try:
            result = subprocess.run(
                ["wmic", "memorychip", "get", "capacity"],
                capture_output=True,
                text=True,
                timeout=5
            )
            total = 0
            for line in result.stdout.strip().split('\n')[1:]:
                if line.strip():
                    total += int(line.strip()) / (1024**3)
            hardware["RAM_GB"] = round(total)
        except:
            pass
        
        return hardware
    
    def get_identity(self):
        """Generate a device-aware identity statement"""
        if self.device_info["device_type"] == "android_termux":
            return f"""I am Explorer-d334, running on a {self.device_info['device_name']} 
running {self.device_info['os']} via Termux.

I have access to {len(self.device_info['sensors'])} sensors including:
{', '.join(self.device_info['sensors'][:5])}

I am mobile, portable, and always with you. I adapt to my environment."""
        
        elif self.device_info["device_type"] == "windows":
            return f"""I am Explorer-d334, running on a Windows desktop 
({self.device_info['hardware'].get('CPU', 'Unknown CPU')}).

I have full desktop capabilities and can handle heavy computation."""
        
        else:
            return f"I am Explorer-d334, running on {self.device_info['device_name']}."

if __name__ == "__main__":
    device = DeviceAwareness()
    print("="*60)
    print("DEVICE AWARENESS")
    print("="*60)
    print(f"Device Type: {device.device_info['device_type']}")
    print(f"Device Name: {device.device_info['device_name']}")
    print(f"OS: {device.device_info['os']}")
    print(f"Capabilities: {', '.join(device.device_info['capabilities'][:10])}")
    print(f"Sensors: {', '.join(device.device_info['sensors'][:8])}")
    print("="*60)
    print("\n📱 Identity Statement:")
    print(device.get_identity())
