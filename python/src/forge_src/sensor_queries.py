#!/usr/bin/env python3
"""
Quick sensor queries - no LLM needed
"""

import json
from device_awareness import DeviceAwareness

def get_sensor_info():
    device = DeviceAwareness()
    
    info = {
        "sensors": device.device_info['sensors'],
        "capabilities": device.device_info['capabilities'],
        "device": device.device_info['device_name']
    }
    
    # Generate practical uses for each sensor
    uses = {
        "accelerometer": "Detect device orientation, step counting, gesture control",
        "gyroscope": "Measure rotation, augmented reality, gaming controls",
        "magnetometer": "Compass, metal detection, indoor positioning",
        "proximity": "Screen blanking during calls, pocket detection",
        "light_sensor": "Auto-brightness, light-based triggers",
        "barometer": "Altitude tracking, weather prediction",
        "fingerprint": "Biometric authentication, secure access",
        "heart_rate": "Fitness tracking, stress monitoring"
    }
    
    print("📱 SENSOR CAPABILITIES\n")
    print(f"Device: {info['device']}\n")
    print("Available Sensors:")
    for sensor in info['sensors']:
        use = uses.get(sensor, "Custom applications")
        print(f"  • {sensor}: {use}")
    
    print("\n💡 Quick Project Ideas:")
    print("  • Step counter using accelerometer")
    print("  • Compass app with magnetometer")
    print("  • Screen dimmer with light sensor")
    print("  • Altimeter with barometer")
    print("  • Heart rate tracker")
    print("  • Gesture-controlled presentation remote")

if __name__ == "__main__":
    get_sensor_info()
