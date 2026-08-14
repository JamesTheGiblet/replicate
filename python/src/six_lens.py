#!/usr/bin/env python3
"""
Six Lens Knowledge System
Think about any topic from six perspectives
"""

LENSES = {
    "FACT": {
        "icon": "◈",
        "color": "Cyan",
        "description": "Verifiable truth",
        "prompt": "What is the verifiable fact here?"
    },
    "COUNTER": {
        "icon": "⊘",
        "color": "Red",
        "description": "Opposing argument",
        "prompt": "What is the counter-argument?"
    },
    "OPINION": {
        "icon": "◎",
        "color": "Purple",
        "description": "Personal perspective",
        "prompt": "What is your personal perspective?"
    },
    "FICTION": {
        "icon": "◇",
        "color": "Amber",
        "description": "Speculative take",
        "prompt": "What is a speculative possibility?"
    },
    "CONTEXT": {
        "icon": "⊡",
        "color": "Green",
        "description": "Historical framing",
        "prompt": "What is the historical context?"
    },
    "UNKNOWN": {
        "icon": "?",
        "color": "Grey",
        "description": "Open questions",
        "prompt": "What remains unknown?"
    }
}

def think_in_cubes(query: str) -> dict:
    """Generate a Six Lens cube for any query"""
    return {
        "topic": query,
        "lenses": LENSES,
        "cube": {name: f"{name}: {query} (from {lens['description']})" 
                 for name, lens in LENSES.items()}
    }

def format_cube(cube: dict) -> str:
    """Format a cube for display"""
    lines = [f"🧊 {cube['topic']}"]
    lines.append("=" * 40)
    for name, lens in cube["lenses"].items():
        icon = lens["icon"]
        color = lens["color"]
        value = cube["cube"][name]
        lines.append(f"{icon} {name}: {value}")
    return "\n".join(lines)
