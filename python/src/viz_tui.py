"""
Curses-based TUI dashboard for Replicant.
Works in Termux with full keyboard controls.
"""

import curses
import time
from typing import Dict, List, Any

try:
    import curses
except ImportError:
    print("Curses not available. Run with: pip install windows-curses (Windows) or use terminal viz.")
    sys.exit(1)


class TUIViz:
    """Curses-based TUI dashboard."""
    
    def __init__(self, world):
        self.world = world
        self.paused = False
        self.speed = 1.0
        
    def run(self, steps: int = 1000):
        """Run the TUI dashboard."""
        curses.wrapper(self._main_loop, steps)
    
    def _main_loop(self, stdscr, steps: int):
        """Main curses loop."""
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(100)
        
        tick = 0
        while tick < steps:
            # Handle input
            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key == ord(' '):
                self.paused = not self.paused
            elif key == ord('+') or key == ord('='):
                self.speed = min(5.0, self.speed + 0.5)
            elif key == ord('-'):
                self.speed = max(0.5, self.speed - 0.5)
            
            if not self.paused:
                self.world.tick_driver()
                tick += 1
            
            # Render
            self._render(stdscr, tick)
            
            # Sleep based on speed
            time.sleep(0.1 / self.speed)
    
    def _render(self, stdscr, tick: int):
        """Render the dashboard."""
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        
        # Title
        stdscr.addstr(0, 0, "🧬 REPLICANT DASHBOARD", curses.A_BOLD)
        stdscr.addstr(0, w//2, f"Tick: {tick}", curses.A_BOLD)
        
        # Controls
        controls = " [SPACE] Pause  [+/-] Speed  [q] Quit"
        stdscr.addstr(1, 0, controls, curses.A_DIM)
        
        # Stats
        alive = len([a for a in self.world.agents.values() if a.alive])
        claims = len(self.world.claims)
        counters = len([c for c in self.world.claims.values() if c.lens == "COUNTER"])
        threats = len(self.world.environment.threats)
        health = self.world.environment.metrics["overall_health"]
        
        stdscr.addstr(3, 0, f"👥 Agents:  {alive}")
        stdscr.addstr(4, 0, f"📋 Claims:  {claims}")
        stdscr.addstr(5, 0, f"🔍 COUNTER: {counters}")
        stdscr.addstr(6, 0, f"⚠️  Threats: {threats}")
        stdscr.addstr(7, 0, f"🌿 Health:  {health:.3f}")
        
        # Season
        season = self.world.environment.get_health_report()["season"]
        stdscr.addstr(8, 0, f"🌤️  Season:  {season}")
        
        # Energy bar
        total_energy = sum(p.energy for p in self.world.environment.patches)
        max_energy = sum(p.max_energy for p in self.world.environment.patches)
        if max_energy > 0:
            pct = total_energy / max_energy
            bar_len = min(40, w - 20)
            filled = int(bar_len * pct)
            bar = '█' * filled + '░' * (bar_len - filled)
            stdscr.addstr(10, 0, f"⚡ Energy: [{bar}] {pct*100:.1f}%")
        
        # Agent list
        stdscr.addstr(12, 0, "┌─ Agents ─────────────────────────────────────┐", curses.A_DIM)
        row = 13
        for aid, agent in list(self.world.agents.items())[:10]:
            if not agent.alive:
                continue
            status = "✓" if not agent.is_rogue else "✗"
            energy = f"{agent.energy:.0f}"
            lam = agent.lambda_state.compute(self.world.tick, 0.05)
            stdscr.addstr(row, 1, f"{status} {agent.role[:8].ljust(8)} | E:{energy.rjust(3)} | λ:{lam:.3f}")
            row += 1
            if row >= h - 2:
                break
        
        stdscr.addstr(row, 0, "└─────────────────────────────────────────────┘", curses.A_DIM)
        
        # Status
        if self.paused:
            stdscr.addstr(h-1, 0, "⏸️  PAUSED", curses.A_BOLD | curses.A_REVERSE)
        else:
            stdscr.addstr(h-1, 0, f"▶️  RUNNING (speed: {self.speed:.1f}x)", curses.A_DIM)
        
        stdscr.refresh()
