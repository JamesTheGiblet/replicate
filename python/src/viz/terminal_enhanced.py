"""
Enhanced terminal visualization for Replicant.
Shows agent names, energy levels, and more detail.
"""

import os
import time
from typing import Dict, List, Any


class EnhancedTerminalViz:
    """Enhanced ASCII swarm visualization."""
    
    def __init__(self, width: int = 60, height: int = 25):
        self.width = width
        self.height = height
        self.grid = [[' ' for _ in range(width)] for _ in range(height)]
        
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
            'bg_red': '\033[41m',
            'bg_green': '\033[42m',
            'bg_yellow': '\033[43m',
        }
    
    def render(self, world, tick: int):
        """Render enhanced world state."""
        self.grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        scale_x = self.width / 100.0
        scale_y = self.height / 100.0
        
        # Draw resource patches
        for patch in world.environment.patches:
            gx = int(patch.x * scale_x)
            gy = int(patch.y * scale_y)
            if 0 <= gx < self.width and 0 <= gy < self.height:
                if patch.depleted:
                    self.grid[gy][gx] = '·'
                elif patch.energy > patch.max_energy * 0.7:
                    self.grid[gy][gx] = '█'
                elif patch.energy > patch.max_energy * 0.3:
                    self.grid[gy][gx] = '▓'
                else:
                    self.grid[gy][gx] = '▒'
        
        # Draw threats
        for threat in world.environment.threats:
            if threat.active:
                for i in range(-3, 4):
                    for j in range(-3, 4):
                        if i*i + j*j <= 9:
                            gx = int((threat.x + i*3) * scale_x)
                            gy = int((threat.y + j*3) * scale_y)
                            if 0 <= gx < self.width and 0 <= gy < self.height:
                                if abs(i) <= 1 and abs(j) <= 1:
                                    self.grid[gy][gx] = '⚠'
                                else:
                                    self.grid[gy][gx] = '░'
        
        # Draw agents
        for aid, agent in world.agents.items():
            if not agent.alive:
                continue
            gx = int(agent.x * scale_x)
            gy = int(agent.y * scale_y)
            if 0 <= gx < self.width and 0 <= gy < self.height:
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
                elif agent.role == "Broadcaster":
                    char = 'N'
                    color = self.COLORS['cyan']
                elif agent.role == "Explorer":
                    char = 'E'
                    color = self.COLORS['yellow']
                elif agent.role == "Healer":
                    char = 'H'
                    color = self.COLORS['green']
                elif agent.role == "Signal":
                    char = 'I'
                    color = self.COLORS['magenta']
                elif agent.role == "Observer":
                    char = 'O'
                    color = self.COLORS['dim']
                else:
                    char = 'a'
                    color = self.COLORS['white']
                
                if agent.is_rogue:
                    char = '!'
                    color = self.COLORS['red'] + self.COLORS['bold']
                elif agent.energy < 25:
                    color = self.COLORS['red']
                elif agent.energy < 50:
                    color = self.COLORS['yellow']
                
                self.grid[gy][gx] = f"{color}{char}{self.COLORS['reset']}"
        
        # Build output
        lines = []
        
        alive = len([a for a in world.agents.values() if a.alive])
        rogue = len([a for a in world.agents.values() if a.is_rogue])
        claims = len(world.claims)
        counters = len([c for c in world.claims.values() if c.lens == "COUNTER"])
        threats = len(world.environment.threats)
        health = world.environment.metrics["overall_health"]
        season = world.environment.get_health_report()["season"]
        
        header = f"{self.COLORS['bold']}🧬 Replicant - Tick {tick}{self.COLORS['reset']}"
        lines.append(header)
        lines.append("═" * (self.width + 2))
        lines.append(f"👥 {alive} agents  |  ⚠️ {rogue} rogue  |  📋 {claims} claims  |  🔍 {counters} COUNTER")
        lines.append(f"🌿 Health: {health:.3f}  |  🌤️ {season}  |  ⚡ Threats: {threats}")
        lines.append("─" * (self.width + 2))
        
        for row in self.grid:
            line = '│'
            for cell in row:
                if isinstance(cell, str) and cell.startswith('\033'):
                    line += cell
                else:
                    line += cell
            line += '│'
            lines.append(line)
        
        lines.append("═" * (self.width + 2))
        lines.append(f"{self.COLORS['dim']}S=Founder D=Scout B=Builder T=Attester C=Forager N=Broadcast E=Explorer H=Healer I=Signal O=Observer")
        lines.append(f"█=Rich ▓=Medium ▒=Poor ·=Depleted ⚠=Threat {self.COLORS['reset']}")
        
        lines.append("─" * (self.width + 2))
        lines.append(f"{self.COLORS['bold']}Agent Details:{self.COLORS['reset']}")
        count = 0
        for aid, agent in list(world.agents.items())[:5]:
            if agent.alive:
                # LambdaState.compute() now takes only tick (k is fixed)
                lam = agent.lambda_state.compute(world.tick)
                energy_bar = '█' * int(agent.energy / 10) + '░' * (10 - int(agent.energy / 10))
                status = '✓' if not agent.is_rogue else '✗'
                lines.append(f"  {status} {agent.role[:8].ljust(8)} | ⚡[{energy_bar}] {agent.energy:.0f} | λ:{lam:.3f}")
                count += 1
        
        if count == 0:
            lines.append("  No agents alive")
        
        os.system('clear' if os.name == 'posix' else 'cls')
        print('\n'.join(lines))
    
    def animate(self, world, steps: int = 100, delay: float = 0.2):
        """Animate the simulation."""
        for tick in range(steps):
            world.step()
            self.render(world, tick)
            time.sleep(delay)
