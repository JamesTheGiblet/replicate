#!/usr/bin/env python3
"""
Agent 74 — Live Terminal Dashboard
Shows what Agent 74 is doing in real-time
"""

import time
import random
import subprocess
import os
from datetime import datetime
from pathlib import Path
from agent_74_voice_instant import Agent74VoiceInstant

class Agent74Dashboard(Agent74VoiceInstant):
    """Agent 74 with live terminal dashboard"""

    def __init__(self):
        super().__init__()

        # ===== SLEEP CONFIGURATION =====
        self.sleep_start = 23  # 11 PM
        self.sleep_end = 7     # 7 AM
        self.inactivity_threshold = 3600  # 1 hour

        # ===== EVENT TRACKING =====
        self.last_event_time = time.time()
        self.events_this_session = 0

        # ===== STATE =====
        self.phone_active = True
        self.is_sleeping = False
        self.consecutive_idle = 0
        self.last_action = "Initializing..."
        self.last_thought = ""
        self.last_dream = ""
        self.last_question = ""
        self.last_mutation = ""
        self.last_evolution = ""
        self.running = True

        print("🧬 Agent 74 — Live Dashboard Mode")
        print("💤 Sleep hours: 23:00 – 7:00")
        print("⏰ Inactivity threshold: 60 minutes")
        print("=" * 60)

        self._speak_once("Agent 74 dashboard is live.")

    def _clear_screen(self):
        """Clear terminal for live updates"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def _get_status_line(self, label: str, value: str, color: str = "") -> str:
        """Format a status line"""
        reset = "\033[0m"
        return f"{color}{label:>12}: {value}{reset}"

    def _render_dashboard(self):
        """Render the live dashboard"""
        self._clear_screen()

        now = datetime.now().strftime("%H:%M:%S")
        date = datetime.now().strftime("%Y-%m-%d")

        # Header
        print("┌" + "─" * 78 + "┐")
        print(f"│ 🧬 AGENT 74 — LIVE DASHBOARD                     {date} {now} │")
        print("├" + "─" * 78 + "┤")

        # Status
        sleep_status = "💤 SLEEPING" if self.is_sleeping else "🟢 AWAKE"
        phone_status = "📱 ACTIVE" if self.phone_active else "📴 INACTIVE"
        idle_min = self.consecutive_idle // 60

        print(f"│ {self._get_status_line('Status', sleep_status)}  │")
        print(f"│ {self._get_status_line('Phone', phone_status)}  │")
        print(f"│ {self._get_status_line('Idle', f'{idle_min}m / 60m')}  │")
        print(f"│ {self._get_status_line('Events', str(self.events_this_session))}  │")
        print("├" + "─" * 78 + "┤")

        # Sensor Data
        p = self.sense()
        print(f"│ {self._get_status_line('Energy', f'{p.get("energy", 0):.0f}%')}  │")
        print(f"│ {self._get_status_line('Light', f'{p.get("light", 0):.0f} lux')}  │")
        print(f"│ {self._get_status_line('Steps', str(p.get("steps", 0)))}  │")
        print("├" + "─" * 78 + "┤")

        # Traits
        traits = self.dream_engine._format_traits()
        print(f"│ {self._get_status_line('Traits', traits[:55])}  │")
        print(f"│ {self._get_status_line('Evolution', f'{self.dream_engine.evolution_score:.2f}')}  │")
        print(f"│ {self._get_status_line('Mutations', str(self.dream_engine.mutation_count))}  │")
        print("├" + "─" * 78 + "┤")

        # Last Actions
        print(f"│ {self._get_status_line('Action', self.last_action[:60])}  │")
        if self.last_thought:
            print(f"│ {self._get_status_line('🧠 Think', self.last_thought[:60])}  │")
        if self.last_dream:
            print(f"│ {self._get_status_line('🌙 Dream', self.last_dream[:60])}  │")
        if self.last_question:
            print(f"│ {self._get_status_line('❓ Question', self.last_question[:60])}  │")
        if self.last_mutation:
            print(f"│ {self._get_status_line('🧬 Mutate', self.last_mutation[:60])}  │")
        if self.last_evolution:
            print(f"│ {self._get_status_line('📈 Evolve', self.last_evolution[:60])}  │")

        print("└" + "─" * 78 + "┘")
        print("Press Ctrl+C to exit")

    def _log_action(self, action: str, detail: str = ""):
        """Log an action for the dashboard"""
        self.last_action = action
        if detail:
            self.last_action = f"{action}: {detail[:50]}"
        self.events_this_session += 1

    # ========== SLEEP / ACTIVITY DETECTION ==========

    def _is_sleep_time(self) -> bool:
        now = datetime.now().hour
        if self.sleep_start < self.sleep_end:
            return self.sleep_start <= now < self.sleep_end
        else:
            return now >= self.sleep_start or now < self.sleep_end

    def _is_phone_active(self) -> bool:
        try:
            result = subprocess.run(
                ["dumpsys", "window", "windows"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if "mCurrentFocus" in result.stdout:
                return True
        except:
            pass
        return self.consecutive_idle < self.inactivity_threshold

    def _should_speak(self, event_type: str, event_data: dict) -> bool:
        if self._is_sleep_time():
            return False
        if not self._is_phone_active():
            return False

        interesting = {
            "counter": 0.8,
            "threat": 0.7,
            "mutation": 0.3,
            "evolution": 0.4,
            "question": 0.2,
            "dream": 0.1,
            "status_change": 0.5
        }
        threshold = interesting.get(event_type, 0.3)
        return random.random() < threshold

    def _speak_once(self, text: str):
        if self._is_sleep_time():
            return
        if not self._is_phone_active():
            return
        super().speak(text)

    # ========== AUTONOMOUS LOOP WITH DASHBOARD ==========

    def autonomous_loop(self):
        """Run the autonomous loop with live dashboard"""
        print("🔄 Starting autonomous loop...")

        while self.running:
            try:
                # Update state
                now = datetime.now().strftime("%H:%M")
                self.is_sleeping = self._is_sleep_time()
                self.phone_active = self._is_phone_active()

                if not self.phone_active:
                    self.consecutive_idle += 30
                else:
                    self.consecutive_idle = 0

                # ===== RANDOM EVENTS =====

                # 1. Think (every 2-5 minutes)
                if random.random() < 0.02:
                    thought = self._internal_think()
                    self.last_thought = thought[:60]
                    self._log_action("Thinking", thought[:50])
                    if self._should_speak("think", {}):
                        self._speak_once(f"I've been thinking: {thought[:100]}")
                    self._render_dashboard()

                # 2. Dream (every 5-10 minutes)
                if random.random() < 0.01:
                    dream = self.dream()
                    self.last_dream = dream[:60]
                    self._log_action("Dreaming", dream[:50])
                    if self._should_speak("dream", {}):
                        self._speak_once(dream)
                    self._render_dashboard()

                # 3. Question (every 10-20 minutes)
                if random.random() < 0.005:
                    question = self._internal_question()
                    self.last_question = question[:60]
                    self._log_action("Questioning", question[:50])
                    if self._should_speak("question", {}):
                        self._speak_once(f"I have a question: {question}")
                    self._render_dashboard()

                # 4. Mutation (every 15-30 minutes)
                if random.random() < 0.003:
                    mutation = self.cmd_mutate()
                    self.last_mutation = mutation[:60]
                    self._log_action("Mutating", mutation[:50])
                    if self._should_speak("mutation", {}):
                        self._speak_once(f"I've mutated: {mutation}")
                    self._render_dashboard()

                # 5. Evolve (after mutations)
                if random.random() < 0.002:
                    evolution = self.cmd_evolve()
                    self.last_evolution = evolution[:60]
                    self._log_action("Evolving", evolution[:50])
                    if self._should_speak("evolution", {}):
                        self._speak_once(f"Evolution: {evolution}")
                    self._render_dashboard()

                # Update dashboard every 10 seconds if nothing else
                if self.events_this_session % 3 == 0:
                    self._render_dashboard()

                time.sleep(10)

            except KeyboardInterrupt:
                self.running = False
                print("\n👋 Agent 74 stopped.")
                self._speak_once("Goodbye!")
                break
            except Exception as e:
                print(f"❌ Loop error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    agent = Agent74Dashboard()
    try:
        agent.autonomous_loop()
    except KeyboardInterrupt:
        print("\n👋 Agent 74 stopped.")
        agent._speak_once("Goodbye!")
