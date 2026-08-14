#!/usr/bin/env python3
"""
Phone Node - S24 Ultra Replicant Agent
Integrates phone sensors with Replicant colony
"""

import json
import subprocess
import time
import threading
from typing import Dict, Any, Optional

class PhoneAgent:
    """S24 Ultra as a Replicant agent"""
    
    def __init__(self, agent_id: str = "phone-001"):
        self.agent_id = agent_id
        self.x = 0.0
        self.y = 0.0
        self.altitude = 0.0
        self.heading = 0.0
        self.energy = 100.0
        self.light = 0
        self.pressure = 0
        self.steps = 0
        self.acceleration = [0, 0, 0]
        self.last_update = 0
        
    def _run_cmd(self, cmd):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout
        except:
            return None
    
    def _get_gps(self):
        output = self._run_cmd(["termux-location"])
        if output:
            try:
                return json.loads(output)
            except:
                pass
        return None
    
    def _get_sensor(self, sensor_name):
        output = self._run_cmd(["termux-sensor", "-s", sensor_name, "-n", "1"])
        if output:
            try:
                return json.loads(output)
            except:
                pass
        return None
    
    def sense(self) -> Dict[str, Any]:
        """Read all sensors and return percepts"""
        percepts = {}
        
        # GPS
        gps = self._get_gps()
        if gps:
            percepts["x"] = gps.get("longitude", 0)
            percepts["y"] = gps.get("latitude", 0)
            percepts["altitude"] = gps.get("altitude", 0)
            percepts["accuracy"] = gps.get("accuracy", 0)
            percepts["bearing"] = gps.get("bearing", 0)
            percepts["speed"] = gps.get("speed", 0)
        
        # Rotation Vector (heading)
        rot = self._get_sensor("Rotation Vector  Non-wakeup")
        if rot and "Rotation Vector  Non-wakeup" in rot:
            values = rot["Rotation Vector  Non-wakeup"]["values"]
            if values:
                percepts["heading"] = values[0]
                percepts["rotation"] = values[:4]
        
        # Accelerometer
        acc = self._get_sensor("lsm6dsv LSM6DSV Accelerometer Non-wakeup")
        if acc and "lsm6dsv LSM6DSV Accelerometer Non-wakeup" in acc:
            values = acc["lsm6dsv LSM6DSV Accelerometer Non-wakeup"]["values"]
            if values:
                percepts["acceleration"] = values[:3]
        
        # Light
        light = self._get_sensor("STK33F11 Light Ambient Light Sensor Non-wakeup")
        if light and "STK33F11 Light Ambient Light Sensor Non-wakeup" in light:
            values = light["STK33F11 Light Ambient Light Sensor Non-wakeup"]["values"]
            if values:
                percepts["light"] = values[0]
        
        # Pressure
        press = self._get_sensor("lps22df Pressure Sensor Non-wakeup")
        if press and "lps22df Pressure Sensor Non-wakeup" in press:
            values = press["lps22df Pressure Sensor Non-wakeup"]["values"]
            if values:
                percepts["pressure"] = values[0]
        
        # Steps
        steps = self._get_sensor("step_counter  Non-wakeup")
        if steps and "step_counter  Non-wakeup" in steps:
            values = steps["step_counter  Non-wakeup"]["values"]
            if values:
                percepts["steps"] = values[0]
                percepts["energy"] = max(0, 100 - (values[0] % 20000 / 20000 * 100))
        
        percepts["timestamp"] = time.time()
        self.last_update = percepts["timestamp"]
        
        # Update state
        self.x = percepts.get("x", self.x)
        self.y = percepts.get("y", self.y)
        self.altitude = percepts.get("altitude", self.altitude)
        self.heading = percepts.get("heading", self.heading)
        self.energy = percepts.get("energy", self.energy)
        self.light = percepts.get("light", self.light)
        self.pressure = percepts.get("pressure", self.pressure)
        self.steps = percepts.get("steps", self.steps)
        self.acceleration = percepts.get("acceleration", self.acceleration)
        
        return percepts
    
    def decide(self, percepts: Dict[str, Any]) -> str:
        """Decide what to do based on percepts"""
        # Simple decision logic for phone agent
        if self.energy < 20:
            return "recharge"
        elif self.light < 50:
            return "seek_light"
        elif percepts.get("accuracy", 10) > 10:
            return "improve_position"
        else:
            return "explore"
    
    def act(self, decision: str) -> None:
        """Execute the decision"""
        print(f"[{self.agent_id}] Acting: {decision}")
        # In real implementation, this would send commands via MQTT
    
    def to_replicant(self) -> Dict[str, Any]:
        """Convert to Replicant agent format"""
        return {
            "agent_id": self.agent_id,
            "type": "phone",
            "x": self.x,
            "y": self.y,
            "altitude": self.altitude,
            "heading": self.heading,
            "energy": self.energy,
            "light": self.light,
            "pressure": self.pressure,
            "steps": self.steps,
            "acceleration": self.acceleration,
            "last_update": self.last_update,
        }

if __name__ == "__main__":
    print("🧬 Phone Node - S24 Ultra Agent")
    print("=" * 50)
    
    agent = PhoneAgent()
    
    for i in range(5):
        percepts = agent.sense()
        decision = agent.decide(percepts)
        agent.act(decision)
        print(f"📊 State: {agent.to_replicant()}")
        time.sleep(2)
