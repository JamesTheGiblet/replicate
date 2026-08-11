"""
Interactive terminal visualization with keyboard controls.
"""

import os
import sys
import time
import select
import tty
import termios


class InteractiveViz:
    """Interactive terminal visualization with keyboard controls."""
    
    def __init__(self, width: int = 60, height: int = 25):
        self.width = width
        self.height = height
        self.paused = False
        self.speed = 1.0
        self.zoom = 1.0
        self.follow_agent = None
        
    def _getch(self):
        """Get a single character from stdin."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
    def _kbhit(self):
        """Check if a key has been pressed."""
        return select.select([sys.stdin], [], [], 0)[0] != []
    
    def run(self, world_func, steps: int = 1000):
        """Run interactive visualization."""
        print("🧬 Interactive Replicant Visualization")
        print("Controls:")
        print("  [SPACE]  Pause/Resume")
        print("  [+/-]    Speed up/down")
        print("  [f]      Follow an agent")
        print("  [q]      Quit")
        print("=" * 50)
        
        tick = 0
        while tick < steps:
            # Check for keypress
            if self._kbhit():
                key = self._getch()
                if key == ' ':
                    self.paused = not self.paused
                    print(f"\n{'Paused' if self.paused else 'Resumed'}")
                elif key == '+':
                    self.speed = min(5.0, self.speed * 1.5)
                    print(f"\nSpeed: {self.speed:.1f}x")
                elif key == '-':
                    self.speed = max(0.2, self.speed / 1.5)
                    print(f"\nSpeed: {self.speed:.1f}x")
                elif key == 'q':
                    break
                elif key == 'f':
                    print("\n🔍 Select agent to follow...")
            
            if not self.paused:
                world_func()
                tick += 1
            
            # Render (using your existing render function)
            self.render()
            time.sleep(0.05 / self.speed)
    
    def render(self):
        """Render the current state - implement this."""
        pass
