"""
Leighton Weight Engine — λ reputation with event-ledger semantics.
Events are append-only; λ is computed on read.
Recidivism escalation: repeated offences increase penalty magnitude.
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class LambdaEvent:
    """A single reputation event."""
    tick: int
    delta: float          # signed: +trust, -distrust
    k: float              # decay rate constant
    reason: str = "unknown"


@dataclass
class LambdaState:
    """Reputation state as an append-only event ledger."""
    base: float = 1.00
    events: List[LambdaEvent] = field(default_factory=list)
    offences: Dict[str, int] = field(default_factory=dict)
    _last_compaction_tick: int = 0
    
    def compute(self, current_tick: int) -> float:
        """Compute λ at current_tick from all events."""
        total = self.base
        for e in self.events:
            dt = current_tick - e.tick
            if dt < 0:
                continue
            total += e.delta * math.exp(-e.k * dt)
        return max(0.00, min(2.00, total))
    
    def add_event(self, tick: int, delta: float, k: float, reason: str = "unknown") -> None:
        """Append a new event."""
        self.events.append(LambdaEvent(tick=tick, delta=delta, k=k, reason=reason))
    
    def compact(self, current_tick: int, threshold: float = 1e-4) -> None:
        """Drop events that have decayed below noise floor."""
        self.events = [
            e for e in self.events
            if abs(e.delta) * math.exp(-e.k * (current_tick - e.tick)) > threshold
        ]
        self._last_compaction_tick = current_tick
    
    def get_event_count(self) -> int:
        return len(self.events)


class LeightonEngine:
    """λ reputation engine with event-ledger semantics and recidivism escalation."""
    
    # Rate constants (half-lives)
    K_FORAGE = 0.02        # ~35 ticks
    K_FALSE_CLAIM = 0.005  # ~139 ticks
    K_ATTACK = 0.001       # ~693 ticks
    
    # Base deltas (before recidivism multiplier)
    DELTA_VERIFIED = 0.05
    DELTA_FALSE_CLAIM = -0.20
    DELTA_ATTACK = -0.30
    DELTA_COUNTER_REWARD = 0.03
    DELTA_CREDULITY_PENALTY = -0.05
    
    # Recidivism parameters — FIXED so N=3 lands clearly below quarantine
    RECIDIVISM_STEP = 1.0   # each prior offence adds 100% (was 0.5)
    FLOOR_FALSE_CLAIM = 0.6  # residue after full decay (was 0.4)
    
    def __init__(self):
        self._states: Dict[str, LambdaState] = {}
    
    def get_state(self, agent_id: str) -> LambdaState:
        """Get or create a LambdaState for an agent."""
        if agent_id not in self._states:
            self._states[agent_id] = LambdaState()
        return self._states[agent_id]
    
    def compute(self, agent_id: str, current_tick: int) -> float:
        """Compute λ for an agent."""
        return self.get_state(agent_id).compute(current_tick)
    
    def apply_event(self, agent_id: str, tick: int, delta: float, k: float, reason: str = "unknown") -> None:
        """Apply an event to an agent's reputation."""
        state = self.get_state(agent_id)
        state.add_event(tick, delta, k, reason)
        
        if len(state.events) > 100:
            state.compact(tick)
    
    def sweep(self, current_tick: int, threshold: float = 1e-4) -> None:
        """Sweep all states to compact old events."""
        for state in self._states.values():
            state.compact(current_tick, threshold)
    
    def _apply_with_recidivism(self, agent_id: str, tick: int, delta_base: float, k: float, reason: str, floor: float = 1.0) -> None:
        """Apply an event with recidivism escalation."""
        state = self.get_state(agent_id)
        priors = state.offences.get(reason, 0)
        multiplier = 1.0 + self.RECIDIVISM_STEP * priors
        delta = delta_base * multiplier
        state.offences[reason] = priors + 1
        self.apply_event(agent_id, tick, delta, k, reason)
    
    def claim_verified(self, agent_id: str, tick: int) -> None:
        """An agent's claim was verified (FACT)."""
        self.apply_event(agent_id, tick, self.DELTA_VERIFIED, self.K_FORAGE, "claim_verified")
    
    def claim_adjudicated_false(self, agent_id: str, tick: int) -> None:
        """An agent's claim was adjudicated false. Escalates with priors."""
        self._apply_with_recidivism(agent_id, tick, self.DELTA_FALSE_CLAIM, self.K_FALSE_CLAIM, "claim_false", self.FLOOR_FALSE_CLAIM)
    
    def attack_detected(self, agent_id: str, tick: int) -> None:
        """An agent attacked another agent. Escalates with priors."""
        self._apply_with_recidivism(agent_id, tick, self.DELTA_ATTACK, self.K_ATTACK, "attack")
    
    def counter_reward(self, agent_id: str, tick: int, share: float = 1.0) -> None:
        """An agent correctly countered a false claim."""
        self.apply_event(agent_id, tick, self.DELTA_COUNTER_REWARD * share, self.K_FORAGE, "counter_reward")
    
    def credulity_penalty(self, agent_id: str, tick: int) -> None:
        """An agent attested FOR a false claim."""
        self.apply_event(agent_id, tick, self.DELTA_CREDULITY_PENALTY, self.K_FORAGE, "credulity")
    
    def get_state_snapshot(self, agent_id: str, current_tick: int) -> Dict:
        """Get a snapshot of an agent's reputation state."""
        state = self.get_state(agent_id)
        return {
            "agent_id": agent_id,
            "lambda": state.compute(current_tick),
            "event_count": len(state.events),
            "offences": dict(state.offences),
            "base": state.base,
        }
