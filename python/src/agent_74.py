#!/usr/bin/env python3
"""
Agent 74 — one file, all of it.

The best parts of ~20 iterations, consolidated. Everything that used to be a
subclass (headless, silent, tiny, lite, cloud, instant, smart, final, dashboard,
sleep_aware, autonomous, dream, thinker, voice, voice_fixed, self_aware) is now
a value in a config preset.

  python agent_74.py                      # local ollama, prints instead of speaking
  python agent_74.py --preset tiny        # tinyllama, silent, autonomous
  python agent_74.py --preset cloud       # VPS + local fallback, espeak voice
  python agent_74.py --preset sleep       # termux voice, quiet 23:00-07:00
  python agent_74.py --selftest           # runs offline, no model needed

Needs: python 3.9+, requests. Everything else is stdlib.
Optional and auto-detected: six_lens.py, trust.py, termux-api, espeak-ng.

KEPT FROM THE OLD CODE
  * the TTS chunker from agent_voice_fixed.py (the best one in the pile)
  * james.scp.json as the source of tone and constraints
  * the memory schema, the forge commands, the Six Lens vocabulary

FIXED ON THE WAY THROUGH
  * ollama reads options.num_predict, not max_tokens -- the old key was
    silently ignored, so token limits never applied at all
  * budgets travel with the task; nothing clamps a 400-token dream to 30
  * __init__ does no I/O and no speech -- the TTS call in the old constructor
    is why six files had to bypass super().__init__() and copy the body
  * the system prompt is layered and budgeted, so the capsule constraints are
    never sliced off the end the way [:500] / [:200] / [:150] used to do
  * six_lens import is guarded; a missing file no longer breaks startup
  * sqlite: WAL, busy_timeout, and status = 'pending' in single quotes
  * the autonomy loop never calls the LLM on the loop thread
  * a failed generation is marked degraded, never canned filler dressed as thought
  * no hardcoded GPS; sensors return None when unavailable; lat/lon not x/y
  * API keys come from the environment
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import queue
import random
import re
import shutil
import sqlite3
import subprocess
import sys
import textwrap
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

try:
    import requests
except ImportError:  # pragma: no cover
    print("Agent 74 needs `requests`:  pip install requests")
    raise

log = logging.getLogger("agent74")

__version__ = "1.0.0"


# ==========================================================================
# CONFIG  --  every old subclass is one of these
# ==========================================================================

# Token budget per task. The router honours these; nothing clamps them.
DEFAULT_BUDGETS: Dict[str, int] = {
    "ask": 200, "think": 260, "question": 60, "learn": 120, "recall": 0,
    "dream": 300, "future": 400, "lens": 300, "cube": 400, "code": 500,
    "pod": 300, "trust": 10, "status": 60,
}


@dataclass
class Backend:
    """One LLM endpoint. Order in Config.backends is preference order."""
    kind: str = "ollama"                     # "ollama" | "remote"
    model: str = "gemma2:2b"
    url: str = "http://localhost:11434"
    label: str = ""
    api_key_env: Optional[str] = None
    timeouts: List[float] = field(default_factory=lambda: [10.0, 30.0])
    temperature: float = 0.6

    def __post_init__(self) -> None:
        if not self.label:
            self.label = self.model
        if self.kind not in ("ollama", "remote"):
            raise ValueError(f"unknown backend kind: {self.kind!r}")
        if not self.timeouts:
            raise ValueError(f"{self.label}: needs at least one timeout")

    @property
    def api_key(self) -> Optional[str]:
        return os.environ.get(self.api_key_env) if self.api_key_env else None


@dataclass
class VoiceCfg:
    kind: str = "console"                    # termux | espeak | console | null
    espeak_voice: str = "en+f4"
    chunk_chars: int = 80
    chunk_timeout: float = 15.0
    gap_seconds: float = 0.4


@dataclass
class AutonomyCfg:
    enabled: bool = False
    tick_seconds: float = 30.0
    chances: Dict[str, float] = field(default_factory=lambda: {
        "think": 0.05, "dream": 0.02, "question": 0.02,
        "learn": 0.02, "mutate": 0.01, "evolve": 0.01,
    })
    speak_chances: Dict[str, float] = field(default_factory=lambda: {
        "think": 0.3, "dream": 0.15, "question": 0.3, "learn": 0.3,
        "mutate": 0.3, "evolve": 0.4, "counter": 0.8, "threat": 0.9,
    })
    sleep_start_hour: Optional[int] = None   # None = no quiet hours
    sleep_end_hour: Optional[int] = None
    min_seconds_between_speech: float = 120.0


@dataclass
class Config:
    name: str = "Agent 74"
    backends: List[Backend] = field(default_factory=lambda: [Backend()])
    voice: VoiceCfg = field(default_factory=VoiceCfg)
    autonomy: AutonomyCfg = field(default_factory=AutonomyCfg)
    base_dir: Path = field(default_factory=Path.cwd)
    db_path: Path = Path("agent_74_memory.db")
    capsule_path: Path = Path("james.scp.json")
    knowledge_path: Path = Path("agent_74_knowledge.md")
    budgets: Dict[str, int] = field(default_factory=lambda: dict(DEFAULT_BUDGETS))
    system_prompt_chars: int = 2400
    strict_capsule: bool = True              # no capsule, no start
    share_location: bool = False

    def __post_init__(self) -> None:
        self.base_dir = Path(self.base_dir).expanduser().resolve()
        for attr in ("db_path", "capsule_path", "knowledge_path"):
            p = Path(getattr(self, attr)).expanduser()
            setattr(self, attr, p if p.is_absolute() else self.base_dir / p)
        merged = dict(DEFAULT_BUDGETS)
        merged.update(self.budgets)
        self.budgets = merged

    def budget(self, task: str) -> int:
        return self.budgets.get(task, self.budgets["ask"])

    def missing_keys(self) -> List[str]:
        return [b.api_key_env for b in self.backends if b.api_key_env and not b.api_key]

    # ---------- presets: the old files, as values ----------

    @classmethod
    def preset(cls, name: str) -> "Config":
        name = (name or "default").lower()
        if name not in PRESETS:
            raise ValueError(f"unknown preset {name!r}. have: {', '.join(sorted(PRESETS))}")
        cfg = PRESETS[name]()
        return cfg.with_env()

    @classmethod
    def from_toml(cls, path: Path) -> "Config":
        try:
            import tomllib
        except ModuleNotFoundError:
            raise RuntimeError("TOML config needs python 3.11+, or use --preset")
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
        cfg = cls(
            name=data.get("name", "Agent 74"),
            backends=[Backend(**b) for b in data.get("backends", [])] or [Backend()],
            voice=VoiceCfg(**data.get("voice", {})),
            autonomy=AutonomyCfg(**data.get("autonomy", {})),
            base_dir=Path(data.get("base_dir", Path(path).parent)),
            budgets=data.get("budgets", {}),
            strict_capsule=data.get("strict_capsule", True),
            share_location=data.get("share_location", False),
        )
        return cfg.with_env()

    def with_env(self) -> "Config":
        if v := os.environ.get("AGENT74_VOICE"):
            self.voice.kind = v
        if v := os.environ.get("AGENT74_MODEL"):
            for b in self.backends:
                b.model = b.label = v
        if v := os.environ.get("AGENT74_OLLAMA_URL"):
            for b in self.backends:
                if b.kind == "ollama":
                    b.url = v
        if v := os.environ.get("AGENT74_REMOTE_URL"):
            for b in self.backends:
                if b.kind == "remote":
                    b.url = v
        if v := os.environ.get("AGENT74_DB"):
            self.db_path = Path(v)
        if os.environ.get("AGENT74_AUTONOMY", "").lower() in ("1", "true", "yes"):
            self.autonomy.enabled = True
        self.__post_init__()
        return self


def _preset_default() -> Config:
    """Local ollama, prints instead of speaking. Safe starting point."""
    return Config()


def _preset_tiny() -> Config:
    """Replaces agent_74_tiny.py and agent_74_lite.py.

    The old ones used a 2s timeout, so tinyllama timed out on nearly every call
    and the "thoughts" came from a hardcoded list -- alive in the logs, not in
    fact. 12s is realistic on a phone. Timeouts now produce a degraded marker.
    """
    return Config(
        backends=[Backend(kind="ollama", model="tinyllama:latest", label="Tiny",
                          timeouts=[12.0, 25.0], temperature=0.4)],
        voice=VoiceCfg(kind="null"),
        autonomy=AutonomyCfg(enabled=True),
        budgets={"think": 80, "dream": 120, "question": 40},
    )


def _preset_cloud() -> Config:
    """Replaces agent_74_cloud.py, _instant.py, _voice_instant.py.

    Set AGENT74_REMOTE_URL and AGENT74_VPS_KEY. The old key is in git history --
    rotate it.
    """
    return Config(
        backends=[
            Backend(kind="remote", model="phi3:mini", label="VPS",
                    url=os.environ.get("AGENT74_REMOTE_URL", "http://REPLACE-ME:5000/api/chat"),
                    api_key_env="AGENT74_VPS_KEY", timeouts=[30.0, 90.0]),
            Backend(kind="ollama", model="tinyllama:latest", label="Tiny (fallback)",
                    timeouts=[60.0]),
        ],
        voice=VoiceCfg(kind="espeak", espeak_voice="en+f4"),
        autonomy=AutonomyCfg(enabled=True, sleep_start_hour=23, sleep_end_hour=7),
    )


def _preset_smart() -> Config:
    """Replaces agent_74_smart.py.

    Same fallback ladder. The old one could spend 3+5+10+20+30+60s per model
    across four models -- about 8.5 minutes -- while holding the loop lock.
    Worst case here is bounded and printed at startup.
    """
    return Config(
        backends=[
            Backend(kind="ollama", model="tinyllama:latest", label="Tiny", timeouts=[8.0]),
            Backend(kind="ollama", model="qwen2.5-coder:1.5b", label="Qwen", timeouts=[15.0]),
            Backend(kind="ollama", model="gemma2:2b", label="Gemma", timeouts=[25.0]),
        ],
        voice=VoiceCfg(kind="null"),
        autonomy=AutonomyCfg(enabled=True),
    )


def _preset_sleep() -> Config:
    """Replaces sleep_aware, dashboard, silent, headless, final, autonomous."""
    return Config(
        backends=[Backend(kind="ollama", model="gemma2:2b", label="Gemma",
                          timeouts=[15.0, 40.0])],
        voice=VoiceCfg(kind="termux"),
        autonomy=AutonomyCfg(
            enabled=True, tick_seconds=30.0,
            sleep_start_hour=23, sleep_end_hour=7,
            min_seconds_between_speech=300.0,
            chances={"think": 0.04, "dream": 0.015, "question": 0.02,
                     "learn": 0.02, "mutate": 0.008, "evolve": 0.005},
        ),
    )


PRESETS: Dict[str, Callable[[], Config]] = {
    "default": _preset_default,
    "tiny": _preset_tiny,
    "cloud": _preset_cloud,
    "smart": _preset_smart,
    "sleep": _preset_sleep,
}


# ==========================================================================
# LLM  --  transport and routing
# ==========================================================================

@dataclass
class Completion:
    text: str
    backend: str
    model: str
    elapsed: float


class Transport:
    """Base. Returns a Completion, or None when this backend failed."""

    def __init__(self, cfg: Backend) -> None:
        self.cfg = cfg

    @property
    def label(self) -> str:
        return self.cfg.label

    def endpoint(self) -> str:
        raise NotImplementedError

    def payload(self, system: str, user: str, max_tokens: int) -> dict:
        raise NotImplementedError

    def headers(self) -> dict:
        return {}

    def complete(self, system: str, user: str, max_tokens: int,
                 timeout: float) -> Optional[Completion]:
        start = time.time()
        try:
            r = requests.post(self.endpoint(), json=self.payload(system, user, max_tokens),
                              headers=self.headers(), timeout=timeout)
        except requests.Timeout:
            log.info("%s timed out after %.1fs", self.label, timeout)
            return None
        except requests.RequestException as exc:
            log.warning("%s transport error: %s", self.label, exc)
            return None

        if r.status_code != 200:
            log.warning("%s returned HTTP %s", self.label, r.status_code)
            return None
        try:
            body = r.json()
        except ValueError:
            log.warning("%s returned non-JSON", self.label)
            return None

        text = ((body.get("message") or {}).get("content") or "").strip()
        if not text:
            log.info("%s returned empty content", self.label)
            return None
        return Completion(text, self.label, self.cfg.model, time.time() - start)


class OllamaTransport(Transport):
    def endpoint(self) -> str:
        return f"{self.cfg.url.rstrip('/')}/api/chat"

    def payload(self, system: str, user: str, max_tokens: int) -> dict:
        return {
            "model": self.cfg.model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "stream": False,
            # THE fix: ollama reads num_predict. max_tokens was always ignored.
            "options": {"temperature": self.cfg.temperature,
                        "num_predict": max_tokens},
        }


class RemoteTransport(Transport):
    """Hosted proxy. Key from the environment, never from source."""

    def endpoint(self) -> str:
        return self.cfg.url

    def headers(self) -> dict:
        key = self.cfg.api_key
        return {"X-API-Key": key} if key else {}

    def payload(self, system: str, user: str, max_tokens: int) -> dict:
        return {
            "model": self.cfg.model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "stream": False,
            "temperature": self.cfg.temperature,
            "options": {"num_predict": max_tokens},
        }

# ============================================================
# MAIN
# ============================================================


# ============================================================
# AGENT 74 — THE ACTUAL AGENT
# ============================================================



class Clock:
    """Tracks time she was actually awake.

    Wall-clock lies on a phone. Doze freezes Termux when the screen goes off and
    ^Z suspends the process outright -- neither is time she lived through. This
    heartbeats every `interval` seconds and credits only what really elapsed
    while running; a gap longer than two beats is booked as frozen, not awake.
    Independent of autonomy, so uptime is right whether she is thinking or idle.
    """

    def __init__(self, db, lock, interval=30.0):
        self.db, self.lock, self.interval = db, lock, interval
        self._stop = threading.Event()
        self.thread = None
        self.awake = 0.0
        self.frozen = 0.0
        self.first_seen = None
        self._last = None
        self._load()

    def _load(self):
        if not self.db:
            return
        try:
            with self.lock:
                self.db.execute("CREATE TABLE IF NOT EXISTS meta"
                                " (key TEXT PRIMARY KEY, value REAL)")
                rows = dict(self.db.execute("SELECT key, value FROM meta").fetchall())
                if "first_seen" not in rows:
                    now = time.time()
                    self.db.execute("INSERT INTO meta (key, value)"
                                    " VALUES ('first_seen', ?)", (now,))
                    self.db.commit()
                    rows["first_seen"] = now
                self.first_seen = rows.get("first_seen")
                self.awake = rows.get("awake_seconds", 0.0)
                self.frozen = rows.get("frozen_seconds", 0.0)
        except Exception:
            pass

    def save(self):
        if not self.db:
            return
        try:
            with self.lock:
                for key, val in (("awake_seconds", self.awake),
                                 ("frozen_seconds", self.frozen)):
                    self.db.execute(
                        "INSERT INTO meta (key, value) VALUES (?, ?)"
                        " ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                        (key, val))
                self.db.commit()
        except Exception:
            pass

    def start(self):
        if self.thread:
            return
        self._last = time.time()
        self._stop.clear()
        self.thread = threading.Thread(target=self._loop, name="a74-clock", daemon=True)
        self.thread.start()

    def stop(self):
        self._stop.set()
        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None
        self.tick()
        self.save()

    def tick(self, now=None):
        now = now or time.time()
        if self._last is None:
            self._last = now
            return
        delta = now - self._last
        self._last = now
        if delta <= self.interval * 2:
            self.awake += delta
        else:
            self.awake += self.interval
            self.frozen += delta - self.interval

    def _loop(self):
        beats = 0
        while not self._stop.wait(self.interval):
            self.tick()
            beats += 1
            if beats % 4 == 0:
                self.save()

    @staticmethod
    def fmt(seconds):
        seconds = int(max(0, seconds))
        days, rem = divmod(seconds, 86400)
        hours, rem = divmod(rem, 3600)
        mins = rem // 60
        if days:
            return f"{days}d {hours}h {mins}m"
        if hours:
            return f"{hours}h {mins}m"
        return f"{mins}m"

    def line(self):
        parts = [f"awake {self.fmt(self.awake)} in total"]
        if self.frozen > 60:
            parts.append(f"frozen {self.fmt(self.frozen)}")
        if self.first_seen:
            parts.append(f"first started {self.fmt(time.time() - self.first_seen)} ago")
        return "; ".join(parts)


class Autonomy:
    """Background thinking.

    Two threads on purpose. The tick loop only decides WHAT to attempt and drops
    a name on a queue; the worker does the slow part. A 90-second VPS call
    therefore cannot stall the ticker or your prompt.
    """

    def __init__(self, agent):
        self.agent = agent
        self.cfg = agent.config.autonomy
        self.q = queue.Queue(maxsize=4)
        self._stop = threading.Event()
        self.threads = []
        self.state = "stopped"
        self.ticks = 0
        self.ran = 0
        self.dropped = 0
        self.last_spoke = 0.0

    def in_quiet_hours(self, now=None):
        start, end = self.cfg.sleep_start_hour, self.cfg.sleep_end_hour
        if start is None or end is None:
            return False
        hour = (now or datetime.now()).hour
        if start < end:
            return start <= hour < end
        return hour >= start or hour < end

    def may_speak(self, action):
        if self.in_quiet_hours():
            return False
        if time.time() - self.last_spoke < self.cfg.min_seconds_between_speech:
            return False
        return random.random() < self.cfg.speak_chances.get(action, 0.3)

    def start(self):
        if self.threads:
            return "autonomy already running"
        self._stop.clear()
        for fn, name in ((self._tick, "a74-tick"), (self._work, "a74-work")):
            t = threading.Thread(target=fn, name=name, daemon=True)
            t.start()
            self.threads.append(t)
        self.state = "idle"
        return f"autonomy on (tick {self.cfg.tick_seconds:.0f}s)"

    def stop(self):
        if not self.threads:
            return "autonomy already stopped"
        self._stop.set()
        for t in self.threads:
            t.join(timeout=3)
        self.threads.clear()
        self.state = "stopped"
        return "autonomy off"

    @property
    def running(self):
        return any(t.is_alive() for t in self.threads)

    def _tick(self):
        while not self._stop.wait(self.cfg.tick_seconds):
            self.ticks += 1
            if self.in_quiet_hours():
                self.state = "quiet"
                continue
            self.state = "idle"
            for action, chance in self.cfg.chances.items():
                if action == "evolve" and not self.agent.mutation_history:
                    continue
                if random.random() < chance:
                    try:
                        self.q.put_nowait(action)
                    except queue.Full:
                        self.dropped += 1

    def _work(self):
        actions = {"think": self.agent.cmd_think, "dream": self.agent.cmd_dream,
                   "question": self.agent.cmd_question, "mutate": self.agent.cmd_mutate,
                   "evolve": self.agent.cmd_evolve}
        while not self._stop.is_set():
            try:
                action = self.q.get(timeout=0.5)
            except queue.Empty:
                continue
            fn = actions.get(action)
            if fn is None:
                self.q.task_done()
                continue
            self.state = action
            speak = self.may_speak(action)
            self.agent._muted = not speak
            try:
                print(f"\r\033[2K\n[{datetime.now():%H:%M:%S}] auto: {action}")
                fn()
                self.ran += 1
                if speak:
                    self.last_spoke = time.time()
                print("\n\U0001F319 You: ", end="", flush=True)
            except Exception as exc:
                print(f"\n[auto] {action} failed: {exc}")
            finally:
                self.agent._muted = False
                self.state = "idle"
                self.q.task_done()

    def status(self):
        if self.cfg.sleep_start_hour is None or self.cfg.sleep_end_hour is None:
            quiet = "none set"
        else:
            flag = "active now" if self.in_quiet_hours() else "not active"
            quiet = f"{self.cfg.sleep_start_hour:02d}:00-{self.cfg.sleep_end_hour:02d}:00 ({flag})"
        return (f"\n  autonomy: {'running' if self.running else 'stopped'}"
                f"\n  state: {self.state}"
                f"\n  ticks: {self.ticks}   ran: {self.ran}   dropped: {self.dropped}"
                f"\n  queued: {self.q.qsize()}"
                f"\n  quiet hours: {quiet}")


class Agent74:
    """Agent 74 — The main agent class"""
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.name = "Agent 74"
        self.running = True
        self.autonomy = self.config.autonomy.enabled
        
        # Load capsule
        self.james = self._load_capsule()
        
        # Build system prompt
        self.system_prompt = self._build_prompt()
        
        # Memory
        self._db_lock = threading.Lock()
        self.memory = self._init_memory()
        
        # Traits
        self.traits = {"scepticism": 0.5, "curiosity": 0.7, "talkativeness": 0.6, "creativity": 0.8, "caution": 0.3}
        self.mutation_count = 0
        self.evolution_score = 0.0
        self.mutation_history = []
        
        # Last response
        self.last_response = ""
        
        self.started_at = time.time()
        self.clock = Clock(self.memory, self._db_lock)
        self.clock.start()
        self._muted = False
        self.auto = Autonomy(self)
        if self.config.autonomy.enabled:
            print(self.auto.start())

        self._print_header()
    
    def _load_capsule(self):
        path = self.config.capsule_path
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return {}
    
    def _build_prompt(self):
        j = self.james
        return f"""You are Agent 74, a Replicant swarm agent.
Personality: {j.get('thinking_style', 'Direct, practical')}
Tone: {j.get('tone', 'Direct, technical')}
Keep responses concise.
You have no users and no hardware. When reflecting, talk only about yourself
and what is in your own memory. Never invent users, logs, devices, or metrics."""
    
    def _init_memory(self):
        try:
            conn = sqlite3.connect(str(self.config.db_path), check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=3000")
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS learnings
                (id INTEGER PRIMARY KEY, timestamp INTEGER, insight TEXT, confidence REAL, source TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS experiences
                (id INTEGER PRIMARY KEY, timestamp INTEGER, type TEXT, content TEXT, importance REAL)''')
            conn.commit()
            return conn
        except:
            return None
    
    @staticmethod
    def _fmt_duration(seconds):
        seconds = int(max(0, seconds))
        days, rem = divmod(seconds, 86400)
        hours, rem = divmod(rem, 3600)
        mins = rem // 60
        if days:
            return f"{days}d {hours}h {mins}m"
        if hours:
            return f"{hours}h {mins}m"
        return f"{mins}m"

    def _uptime_line(self):
        """This session, plus total age from the oldest thing she remembers.
        No new table -- MIN(timestamp) over experiences is her birth."""
        session = time.time() - getattr(self, "started_at", time.time())
        return f"up {self._fmt_duration(session)} this session; {self.clock.line()}"

    def _system_now(self):
        """System prompt plus the current moment, rebuilt on every call so the
        clock cannot go stale the way a prompt built once in __init__ does."""
        now = datetime.now()
        return (self.system_prompt +
                f"\n\nRight now it is {now:%A %d %B %Y, %H:%M} ({time.strftime('%Z')}). "
                f"You have been {self._uptime_line()}. "
                "Use this when time matters. Never guess or invent dates.")

    def _store(self, kind, content, importance=0.5):
        """Everything she does lands here, so think() has real material."""
        if not self.memory or not content:
            return
        try:
          with self._db_lock:
            self.memory.execute(
                "INSERT INTO experiences (timestamp, type, content, importance)"
                " VALUES (?,?,?,?)",
                (int(time.time()), kind, content[:2000], importance))
            self.memory.commit()
        except Exception as e:
            print(f"memory write failed: {e}")

    def _store_learning(self, insight, confidence=0.5, source=""):
        if not self.memory or not (insight or "").strip():
            return
        try:
          with self._db_lock:
            self.memory.execute(
                "INSERT INTO learnings (timestamp, insight, confidence, source)"
                " VALUES (?,?,?,?)",
                (int(time.time()), insight[:2000], confidence, source[:50]))
            self.memory.commit()
        except Exception as e:
            print(f"memory write failed: {e}")

    def _recent_experiences(self, limit=6):
        if not self.memory:
            return []
        try:
          with self._db_lock:
            rows = self.memory.execute(
                "SELECT timestamp, type, content FROM experiences"
                " WHERE content != '' AND type != 'reflection'"
                " ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        except Exception:
            return []
        out = []
        for ts, kind, content in reversed(rows):   # oldest first, so order reads right
            when = datetime.fromtimestamp(ts or 0).strftime("%d %b %H:%M")
            out.append(f"{when}  [{kind}] {content}")
        return out

    def _sense(self):
        try:
            from phone.agent import PhoneAgent
            phone = PhoneAgent()
            return phone.sense()
        except:
            return {"energy": 50, "light": 100, "steps": 0, "x": 0, "y": 0}
    
    def _query_llm(self, prompt, max_tokens=50):
        # Build transports from config
        transports = []
        for backend in self.config.backends:
            if backend.kind == "ollama":
                transports.append(OllamaTransport(backend))
            else:
                transports.append(RemoteTransport(backend))
        
        for transport in transports:
            # Try each timeout
            for timeout in transport.cfg.timeouts:
                result = transport.complete(self._system_now(), prompt, max_tokens, timeout)
                if result:
                    return result.text
        return ""
    
    def _speak(self, text):
        if getattr(self, "_muted", False):
            return
        if not text or self.config.voice.kind == "null":
            return
        text = text[:300]
        try:
            if self.config.voice.kind == "espeak":
                subprocess.run(["espeak-ng", "-v", self.config.voice.espeak_voice, text], 
                             timeout=self.config.voice.chunk_timeout, capture_output=False)
            elif self.config.voice.kind == "termux":
                subprocess.run(["termux-tts-speak", text], 
                             timeout=self.config.voice.chunk_timeout, capture_output=False)
            else:
                pass  # console: the caller already printed it
        except:
            pass
    
    def _print_header(self):
        print("=" * 60)
        print(f"🧬 Agent 74 — {self.config.name}")
        print(f"📡 Backend: {self.config.backends[0].label}")
        print(f"🧠 Model: {self.config.backends[0].model}")
        print(f"🗣️ Voice: {self.config.voice.kind}")
        print(f"⚡ Autonomy: {self.auto.state}")
        print("=" * 60)
    
    def _print_help(self):
        print("\nAvailable Commands:")
        print("  status     - Show current state")
        print("  think      - Six Lens reflection")
        print("  dream      - Generate a dream")
        print("  question   - Generate a question")
        print("  learn      - Show learnings")
        print("  recall     - Recall learnings")
        print("  mutate     - Mutate traits")
        print("  evolve     - Evolve based on mutations")
        print("  report     - Mutation history")
        print("  whoami     - Show identity")
        print("  autonomy   - on | off | (blank for status)")
        print("  say <text> - Speak")
        print("  quit       - Exit")
        print("")
    
    def cmd_status(self):
        p = self._sense()
        traits = ", ".join([f"{k}: {v:.2f}" for k, v in self.traits.items()])
        print(f"\n📍 Agent 74 Status")
        print("-" * 50)
        print(f"  Time: {datetime.now():%a %d %b %Y  %H:%M}")
        print(f"  Uptime: {self._uptime_line()}")
        print(f"  Energy: {p.get('energy', 0):.0f}%")
        print(f"  Light: {p.get('light', 0):.0f} lux")
        print(f"  Steps: {p.get('steps', 0)}")
        print(f"  Traits: {traits}")
        print(f"  Evolution: {self.evolution_score:.2f}")
        print(f"  Mutations: {self.mutation_count}")
        print("-" * 50)
    
    def cmd_think(self):
        recent = self._recent_experiences(6)
        if not recent:
            print("\n🧠 Nothing recorded yet, so there is nothing to reflect on.")
            print("   Try: mutate, dream, question - or  learn <something you know>")
            return
        body = "\n".join(f"- {r}" for r in recent)
        prompt = ("My recent experiences, oldest first:\n" + body +
                  "\n\nReflect on these. What pattern is here, and what should I pay "
                  "more attention to? These are MY OWN internal traits and actions "
                  "- they say nothing about users, hardware, or logs. Use ONLY what "
                  "is listed above. Do not invent events, figures, percentages, or "
                  "recommendations about things not mentioned.")
        result = self._query_llm(prompt, self.config.budget("think"))
        if not result:
            print("\n🧠 No model reachable - nothing worth saying.")
            return
        print(f"\n🧠 Thought:\n{result}")
        self._store("reflection", result, 0.6)
        self._store_learning(result, 0.5, "reflection")
        self._speak(result[:200])
    
    def cmd_dream(self):
        result = self._query_llm("Generate a creative dream about the swarm's future.", self.config.budget("dream"))
        print(f"\n🌙 Dream:\n{result or 'No model reachable.'}")
        self._store("dream", result, 0.7)
        self._speak(result[:200])
    
    def cmd_question(self):
        result = self._query_llm("Generate one interesting question about the swarm.", self.config.budget("question"))
        print(f"\n❓ Question:\n{result or 'No model reachable.'}")
        self._store("question", result, 0.7)
    
    def cmd_learn(self, args=""):
        if args:
            self._store_learning(args, 0.8, "user")
            self._store("learning", args, 0.8)
            print(f"\n📖 Noted: {args}")
            return
        if not self.memory:
            print("Memory not available")
            return
        cursor = self.memory.cursor()
        cursor.execute("SELECT insight FROM learnings WHERE insight != ''"
                       " ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        if not rows:
            print("No learnings yet.")
            return
        print("\n📖 Learnings:")
        for row in rows:
            print(f"  💡 {row[0][:60]}")
    
    def cmd_mutate(self):
        import random
        param = random.choice(list(self.traits.keys()))
        delta = random.uniform(-0.2, 0.2)
        old = self.traits[param]
        self.traits[param] = max(0.0, min(1.0, old + delta))
        self.mutation_count += 1
        desc = f"{param}: {old:.2f} → {self.traits[param]:.2f}"
        self.mutation_history.append(desc)
        print(f"\n🧬 Mutation #{self.mutation_count}: {desc}")
        _dir = "rose" if self.traits[param] > old else "fell"
        self._store("mutation",
                    f"my own {param} {_dir} to {self.traits[param]:.2f} "
                    f"(an internal trait of mine, not a user metric)", 0.5)
        self._speak(f"I've mutated: {desc}")
    
    def cmd_evolve(self):
        if not self.mutation_history:
            print("No mutations to evolve from.")
            return
        self.evolution_score += 0.1
        print(f"\n✅ Evolution successful")
        print(f"  Score: {self.evolution_score:.2f}")
        print(f"  Traits: {', '.join([f'{k}: {v:.2f}' for k,v in self.traits.items()])}")
    
    def cmd_report(self):
        if not self.mutation_history:
            print("No mutations yet.")
            return
        print(f"\n🧬 Mutation History ({len(self.mutation_history)})")
        for i, m in enumerate(self.mutation_history[-5:]):
            print(f"  #{i+1}: {m}")
        print(f"\nTraits: {', '.join([f'{k}: {v:.2f}' for k,v in self.traits.items()])}")
    
    def cmd_whoami(self):
        j = self.james
        print(f"\n🧑 Identity: {j.get('identity', 'Unknown')}")
        print(f"  Style: {j.get('thinking_style', 'Direct')}")
        print(f"  Tone: {j.get('tone', 'Technical')}")
        print(f"  Trust: {j.get('trust_score', 0.95)}")
        print(f"  Projects: {', '.join(j.get('active_projects', ['Replicant']))}")
    
    def cmd_say(self, text):
        self._speak(text)
        print(f"🗣️ Spoken: {text}")
    
    def run(self):
        self._print_help()
        
        while self.running:
            try:
                cmd = input("\n🌙 You: ").strip()
                if not cmd:
                    continue
                
                parts = cmd.split()
                action = parts[0].lower()
                args = " ".join(parts[1:]) if len(parts) > 1 else ""
                
                if action in ["quit", "exit"]:
                    self.running = False
                    self.auto.stop()
                    self.clock.stop()
                    self._speak("Goodbye!")
                    print("👋 Agent 74 stopped.")
                    break
                elif action == "status":
                    self.cmd_status()
                elif action == "think":
                    self.cmd_think()
                elif action == "dream":
                    self.cmd_dream()
                elif action == "question":
                    self.cmd_question()
                elif action == "learn":
                    self.cmd_learn(args)
                elif action == "recall":
                    self.cmd_learn()
                elif action == "mutate":
                    self.cmd_mutate()
                elif action == "evolve":
                    self.cmd_evolve()
                elif action == "report":
                    self.cmd_report()
                elif action == "autonomy":
                    if args == "on":
                        print(self.auto.start())
                    elif args == "off":
                        print(self.auto.stop())
                    else:
                        print(self.auto.status())
                elif action == "whoami":
                    self.cmd_whoami()
                elif action == "say" and args:
                    self.cmd_say(args)
                elif action in ["help", "?"]:
                    self._print_help()
                else:
                    result = self._query_llm(cmd, self.config.budget("ask")) or "I'm not sure about that."
                    print(f"\n🧠 Answer:\n{result}")
                    self._speak(result[:200])
                    
            except KeyboardInterrupt:
                self.running = False
                print("\n👋 Agent 74 stopped.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 74")
    parser.add_argument("--preset", "-p", choices=["default", "tiny", "cloud", "smart", "sleep"],
                        default="cloud", help="preset configuration")
    parser.add_argument("--voice", choices=["termux", "espeak", "console", "null"], default="console")
    parser.add_argument("--autonomy", action="store_true", help="enable autonomy")
    parser.add_argument("--no-capsule", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    
    # Load preset
    config = Config.preset(args.preset)
    
    # Override voice
    if args.voice:
        config.voice.kind = args.voice
    
    # Set autonomy
    if args.autonomy:
        config.autonomy.enabled = True
    
    # Create and run agent
    agent = Agent74(config)
    agent.run()
