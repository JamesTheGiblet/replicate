"""
Terminal-based visualization for Replicant.
Works in Termux without GUI dependencies.
"""

import os
import sys
import time
from typing import Dict, List, Any


class TerminalViz:
    """ASCII-based swarm visualization for terminal."""
    
    def __init__(self, width: int = 60, height: int = 30):
        self.width = width
        self.height = height
        self.grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Colors (ANSI escape codes)
        self.COLORS = {
            'reset': '\033[0m',
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'dim': '\033[2m',
        }
    
    def render(self, world, tick: int):
        """Render the current world state."""
        # Clear grid
        self.grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Scale coordinates to grid
        scale_x = self.width / 100.0
        scale_y = self.height / 100.0
        
        # Draw resource patches
        for patch in world.environment.patches:
            gx = int(patch.x * scale_x)
            gy = int(patch.y * scale_y)
            if 0 <= gx < self.width and 0 <= gy < self.height:
                if patch.depleted:
                    self.grid[gy][gx] = '.'  # Depleted
                elif patch.energy > patch.max_energy * 0.7:
                    self.grid[gy][gx] = '*'  # Rich
                elif patch.energy > patch.max_energy * 0.3:
                    self.grid[gy][gx] = '+'  # Medium
                else:
                    self.grid[gy][gx] = '-'  # Poor
        
        # Draw threats
        for threat in world.environment.threats:
            if threat.active:
                for i in range(-2, 3):
                    for j in range(-2, 3):
                        if i*i + j*j <= 4:
                            gx = int((threat.x + i*3) * scale_x)
                            gy = int((threat.y + j*3) * scale_y)
                            if 0 <= gx < self.width and 0 <= gy < self.height:
                                if abs(i) <= 1 and abs(j) <= 1:
                                    self.grid[gy][gx] = 'X'
                                else:
                                    self.grid[gy][gx] = 'x'
        
        # Draw agents
        agent_colors = {}
        for aid, agent in world.agents.items():
            if not agent.alive:
                continue
            gx = int(agent.x * scale_x)
            gy = int(agent.y * scale_y)
            if 0 <= gx < self.width and 0 <= gy < self.height:
                # Color by role
                if agent.role == "Founder":
                    char = 'S'
                    color = self.COLORS['yellow']
                elif agent.role == "Scout":
                    char = 'D'
                    color = self.COLORS['cyan']
                elif agent.role == "Builder":
                    char = 'B'
                    color = self.COLORS['green']
                elif agent.role == "Attester":
                    char = 'T'
                    color = self.COLORS['magenta']
                elif agent.role == "Forager":
                    char = 'C'
                    color = self.COLORS['blue']
                elif agent.role == "Observer":
                    char = 'O'
                    color = self.COLORS['dim']
                else:
                    char = 'a'
                    color = self.COLORS['white']
                
                if agent.is_rogue:
                    char = '!'
                    color = self.COLORS['red']
                elif agent.energy < 25:
                    char = char.lower()
                
                self.grid[gy][gx] = f"{color}{char}{self.COLORS['reset']}"
        
        # Build output
        lines = []
        
        # Header
        lines.append(f"{self.COLORS['bold']}🧬 Replicant - Tick {tick}{self.COLORS['reset']}")
        lines.append("=" * (self.width + 2))
        
        # Grid
        for row in self.grid:
            line = '|'
            for cell in row:
                if isinstance(cell, str) and cell.startswith('\033'):
                    line += cell
                else:
                    line += cell
            line += '|'
            lines.append(line)
        
        # Footer
        lines.append("=" * (self.width + 2))
        
        # Stats
        alive = len([a for a in world.agents.values() if a.alive])
        claims = len(world.claims)
        counters = len([c for c in world.claims.values() if c.lens == "COUNTER"])
        threats = len(world.environment.threats)
        health = world.environment.metrics["overall_health"]
        season = world.environment.get_health_report()["season"]
        
        lines.append(f"👥 Agents: {alive}  |  📋 Claims: {claims}  |  🔍 COUNTER: {counters}")
        lines.append(f"⚠️  Threats: {threats}  |  🌿 Health: {health:.3f}  |  🌤️  Season: {season}")
        
        # Energy bar
        total_energy = sum(p.energy for p in world.environment.patches)
        max_energy = sum(p.max_energy for p in world.environment.patches)
        if max_energy > 0:
            pct = total_energy / max_energy
            bar_len = 30
            filled = int(bar_len * pct)
            bar = '█' * filled + '░' * (bar_len - filled)
            lines.append(f"⚡ Energy: [{bar}] {pct*100:.1f}%")
        
        # Legend
        lines.append("\nLegend: S=Founder D=Scout B=Builder T=Attester C=Forager O=Observer")
        lines.append("  * = Rich resource  + = Medium  - = Poor  . = Depleted  X = Threat")
        
        # Clear screen and print
        os.system('clear' if os.name == 'posix' else 'cls')
        print('\n'.join(lines))
    
    def animate(self, world_func, steps: int = 100, delay: float = 0.2):
        """Animate the simulation."""
        for tick in range(steps):
            world_func()
            self.render(world, tick)
            time.sleep(delay)
