#!/usr/bin/env python3
"""
Agent 74 — Sleep-Aware Autonomous Mode
Only speaks when interesting events happen
Respects sleep time and phone inactivity
"""

import time
import random
import subprocess
from datetime import datetime
from pathlib import Path
from agent_74_voice_instant import Agent74VoiceInstant

class Agent74SleepAware(Agent74VoiceInstant):
    """Agent 74 with sleep awareness and event-based speaking"""

    def __init__(self):
        super().__init__()

        # ===== SLEEP CONFIGURATION =====
        self.sleep_start = 23  # 11 PM
        self.sleep_end = 7     # 7 AM
        self.inactivity_threshold = 3600  # 1 hour (seconds)

        # ===== EVENT TRACKING =====
        self.last_event_time = time.time()
        self.last_interesting_event = 0
        self.events_this_session = 0

        # ===== STATE =====
        self.phone_active = True
        self.is_sleeping = False
        self.consecutive_idle = 0

        print("🧬 Agent 74 — Sleep-Aware Autonomous Mode")
        print(f"💤 Sleep hours: {self.sleep_start}:00 – {self.sleep_end}:00")
        print(f"⏰ Inactivity threshold: {self.inactivity_threshold//60} minutes")
        print("=" * 50)

        self._speak_once("Agent 74 is now autonomous and sleep-aware.")

    # ========== SLEEP / ACTIVITY DETECTION ==========

    def _is_sleep_time(self) -> bool:
        """Check if current time is within sleep hours"""
        now = datetime.now().hour
        if self.sleep_start < self.sleep_end:
            return self.sleep_start <= now < self.sleep_end
        else:
            return now >= self.sleep_start or now < self.sleep_end

    def _is_phone_active(self) -> bool:
        """Check if phone has been active recently"""
        # Check if phone is unlocked (simplified)
        try:
            import subprocess
            result = subprocess.run(
                ["dumpsys", "window", "windows"],
                capture_output=True,
                text=True,
                timeout=2
            )
            # If "mCurrentFocus" is present, phone is active
            if "mCurrentFocus" in result.stdout:
                return True
        except:
            pass

        # Fallback: check if any input was received recently
        return self.consecutive_idle < self.inactivity_threshold

    def _should_speak(self, event_type: str, event_data: dict) -> bool:
        """Decide if an event is interesting enough to speak"""

        # Never speak during sleep
        if self._is_sleep_time():
            return False

        # Only speak if phone is active
        if not self._is_phone_active():
            return False

        # Interesting events
        interesting = {
            "counter": 0.8,      # COUNTER claims
            "threat": 0.7,       # Threats detected
            "mutation": 0.3,     # Significant mutations
            "evolution": 0.4,    # Successful evolution
            "question": 0.2,     # New questions
            "dream": 0.1,        # Interesting dreams
            "status_change": 0.5 # Major status changes
        }

        # Random threshold to avoid speaking too often
        threshold = interesting.get(event_type, 0.3)
        return random.random() < threshold

    def _speak_once(self, text: str):
        """Speak only if not sleeping"""
        if self._is_sleep_time():
            return
        if not self._is_phone_active():
            return
        super().speak(text)

    # ========== AUTONOMOUS LOOP ==========

    def autonomous_loop(self):
        """Run the autonomous loop"""
        print("🔄 Autonomous loop started. I'll only speak when interesting.")
        print("💤 I respect your sleep time.")

        while True:
            try:
                time.sleep(30)  # Check every 30 seconds

                # Update state
                now = datetime.now().strftime("%H:%M")
                self.is_sleeping = self._is_sleep_time()
                self.phone_active = self._is_phone_active()

                if self.is_sleeping:
                    print(f"💤 [{now}] Sleeping... (not speaking)")
                    continue

                if not self.phone_active:
                    self.consecutive_idle += 30
                    if self.consecutive_idle == self.inactivity_threshold:
                        print(f"📱 [{now}] Phone inactive for 1 hour. Entering quiet mode.")
                    continue
                else:
                    self.consecutive_idle = 0

                # ===== RANDOM EVENTS =====

                # 1. Think (every 2-5 minutes)
                if random.random() < 0.02:
                    thought = self._internal_think()
                    if self._should_speak("think", {}):
                        self._speak_once(f"I've been thinking: {thought[:100]}")
                    print(f"🧠 [{now}] {thought[:50]}...")

                # 2. Dream (every 5-10 minutes)
                if random.random() < 0.01:
                    dream = self.dream()
                    if self._should_speak("dream", {}):
                        self._speak_once(dream)
                    print(f"🌙 [{now}] Dreamed: {dream[:50]}...")

                # 3. Question (every 10-20 minutes)
                if random.random() < 0.005:
                    question = self._internal_question()
                    if self._should_speak("question", {}):
                        self._speak_once(f"I have a question: {question}")
                    print(f"❓ [{now}] Question: {question}")

                # 4. Mutation (every 15-30 minutes)
                if random.random() < 0.003:
                    mutation = self.cmd_mutate()
                    if self._should_speak("mutation", {}):
                        self._speak_once(f"I've mutated: {mutation}")
                    print(f"🧬 [{now}] {mutation}")

                # 5. Evolve (after mutations)
                if random.random() < 0.002:
                    evolution = self.cmd_evolve()
                    if self._should_speak("evolution", {}):
                        self._speak_once(f"Evolution: {evolution}")
                    print(f"🧬 [{now}] {evolution}")

            except Exception as e:
                print(f"❌ Loop error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    agent = Agent74SleepAware()

    # Run in background
    try:
        agent.autonomous_loop()
    except KeyboardInterrupt:
        print("\n👋 Agent 74 stopped.")
        agent._speak_once("Goodbye!")
