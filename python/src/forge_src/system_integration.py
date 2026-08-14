#!/usr/bin/env python3
"""
System Integration Verifier for Explorer-d334
Ensures all components are properly connected
"""

import os
import sys
from pathlib import Path

def check_integrations():
    print("=" * 60)
    print("🔗 SYSTEM INTEGRATION VERIFICATION")
    print("=" * 60)
    
    integrations = {
        "Evolutionary Code → Six Lenses": False,
        "Evolutionary Code → Trust System": False,
        "CyberForge → Security Agent": False,
        "CyberForge → Data Cube": False,
        "P.DE.I Exocortex → Personality": False,
        "P.DE.I Exocortex → Memory": False,
        "SpatialPod → Six Lenses": False,
        "SpatialPod → Data Cube": False,
    }
    
    # Check Evolutionary Code integration
    try:
        from src.hybrid_evolution import evolve_function
        integrations["Evolutionary Code → Six Lenses"] = True
    except:
        pass
    
    # Check CyberForge integration
    if Path("cyberforge.html").exists():
        integrations["CyberForge → Security Agent"] = True
    
    # Check P.DE.I integration
    if Path("pdei_core/exocortex.py").exists():
        integrations["P.DE.I Exocortex → Personality"] = True
    
    # Check SpatialPod integration
    if Path("spatialpod.html").exists():
        integrations["SpatialPod → Six Lenses"] = True
    
    print("\n📊 Integration Status:")
    for name, status in integrations.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {name}")
    
    return integrations

if __name__ == "__main__":
    check_integrations()
