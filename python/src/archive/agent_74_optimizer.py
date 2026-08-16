#!/usr/bin/env python3
"""
Agent 74 — Self-Optimizing
Tracks performance, learns, and adjusts its own parameters
"""

import subprocess
import time
import requests
import random
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from agent_74_headless import Agent74Headless, AutonomousEngine

class Agent74Optimizer(Agent74Headless):
    """Agent 74 with self-optimization capabilities"""
    
    # LLM models with performance tracking
    MODELS = [
        ("tinyllama:latest", "⚡ Tiny"),
        ("qwen2.5-coder:1.5b", "🔄 Qwen"),
        ("gemma2:2b", "🔄 Gemma"),
        ("phi3:mini", "🔄 Phi3"),
    ]
    
    # Timeout progression (seconds)
    TIMEOUTS = [3, 5, 8, 12, 18, 25, 35, 50, 70]
    
    def __init__(self):
        self.model = "tinyllama:latest"
        self.ollama_url = "http://localhost:11434"
        self.name = "Agent 74"
        self.base_dir = Path(__file__).parent
        
        # Performance tracking
        self.performance_data = []
        self.model_performance = {model: {"attempts": 0, "successes": 0, "total_time": 0, "avg_time": 0} for model, _ in self.MODELS}
        self.optimization_history = []
        self.current_optimization_index = 0
        
        # Adaptive parameters
        self.current_timeout_index = 0
        self.current_model_index = 0
        self.max_tokens = 20
        self.temperature = 0.3
        
        # Load everything
        self.james = self._load_james_capsule()
        self.knowledge = self._load_knowledge()
        self.memory = self._init_memory()
        self.exocortex = self._init_exocortex()
        self.system_prompt = self._build_system_prompt()
        self._init_performance_db()
        
        from agent_74_dream import DreamEngine
        self.dream_engine = DreamEngine(self.memory)
        self.autonomous = AutonomousEngine(self)
        
        print("🧬 Agent 74 — Self-Optimizing")
        print("📊 Tracks performance, learns, adapts")
        print("⚡ Optimizes for speed")
    
    def _init_performance_db(self):
        """Initialize performance tracking database"""
        self.perf_db = self.base_dir / "agent_74_performance.db"
        self.perf_conn = sqlite3.connect(self.perf_db)
        self.perf_cursor = self.perf_conn.cursor()
        
        self.perf_cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                query_type TEXT,
                model TEXT,
                timeout INTEGER,
                max_tokens INTEGER,
                temperature REAL,
                success INTEGER,
                response_time REAL,
                error TEXT
            )
        ''')
        
        self.perf_cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                parameter TEXT,
                old_value TEXT,
                new_value TEXT,
                reason TEXT,
                improvement REAL
            )
        ''')
        
        self.perf_conn.commit()
        print("📊 Performance tracking initialized")
    
    def _log_performance(self, query_type: str, model: str, timeout: int, max_tokens: int, temperature: float, success: bool, response_time: float, error: str = ""):
        """Log performance data"""
        self.perf_cursor.execute('''
            INSERT INTO performance (timestamp, query_type, model, timeout, max_tokens, temperature, success, response_time, error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), query_type, model, timeout, max_tokens, temperature, 1 if success else 0, response_time, error))
        self.perf_conn.commit()
        
        # Update model performance cache
        if model in self.model_performance:
            stats = self.model_performance[model]
            stats["attempts"] += 1
            if success:
                stats["successes"] += 1
                stats["total_time"] += response_time
                stats["avg_time"] = stats["total_time"] / stats["successes"] if stats["successes"] > 0 else 0
    
    def _record_optimization(self, parameter: str, old_value: str, new_value: str, reason: str, improvement: float = 0):
        """Record an optimization adjustment"""
        self.perf_cursor.execute('''
            INSERT INTO optimizations (timestamp, parameter, old_value, new_value, reason, improvement)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), parameter, old_value, new_value, reason, improvement))
        self.perf_conn.commit()
        self.optimization_history.append({
            "parameter": parameter,
            "old": old_value,
            "new": new_value,
            "reason": reason,
            "improvement": improvement
        })
    
    def _get_optimization_report(self) -> str:
        """Get optimization history"""
        self.perf_cursor.execute('''
            SELECT * FROM optimizations ORDER BY id DESC LIMIT 10
        ''')
        columns = [description[0] for description in self.perf_cursor.description]
        rows = self.perf_cursor.fetchall()
        
        if not rows:
            return "No optimizations yet."
        
        lines = ["📊 Optimization Report"]
        lines.append("=" * 40)
        for row in rows[:5]:
            data = dict(zip(columns, row))
            lines.append(f"  {data['parameter']}: {data['old_value']} → {data['new_value']}")
            if data['improvement'] > 0:
                lines.append(f"    📈 +{data['improvement']:.2f}s")
        return "\n".join(lines)
    
    def _get_performance_stats(self) -> str:
        """Get performance statistics"""
        self.perf_cursor.execute('''
            SELECT model, COUNT(*) as attempts, SUM(success) as successes, AVG(response_time) as avg_time
            FROM performance
            GROUP BY model
            ORDER BY avg_time ASC
        ''')
        rows = self.perf_cursor.fetchall()
        
        if not rows:
            return "No performance data yet."
        
        lines = ["📊 Performance Stats"]
        lines.append("=" * 40)
        for row in rows:
            model, attempts, successes, avg_time = row
            success_rate = (successes / attempts * 100) if attempts > 0 else 0
            lines.append(f"  {model}: {successes}/{attempts} ({success_rate:.0f}%) avg {avg_time:.2f}s")
        
        # Current settings
        current_model = self.MODELS[self.current_model_index][1]
        current_timeout = self.TIMEOUTS[self.current_timeout_index]
        lines.append("")
        lines.append(f"Current: {current_model} | Timeout: {current_timeout}s | Tokens: {self.max_tokens}")
        
        return "\n".join(lines)
    
    def _optimize_parameters(self, query_type: str, success: bool, response_time: float, model_name: str):
        """Intelligently optimize parameters based on performance"""
        # Only optimize after we have enough data
        total_attempts = sum([s["attempts"] for s in self.model_performance.values()])
        if total_attempts < 5:
            return
        
        # Check if we should optimize timeout
        if not success:
            # If failing, increase timeout for this model
            if self.current_timeout_index < len(self.TIMEOUTS) - 1:
                old_timeout = self.TIMEOUTS[self.current_timeout_index]
                self.current_timeout_index += 1
                new_timeout = self.TIMEOUTS[self.current_timeout_index]
                self._record_optimization("timeout", str(old_timeout), str(new_timeout), "Increased timeout due to failure", 0)
        
        # If we have many successes, try reducing timeout
        elif success and response_time < self.TIMEOUTS[self.current_timeout_index] * 0.5:
            # We're way under timeout, try reducing
            if self.current_timeout_index > 1:
                old_timeout = self.TIMEOUTS[self.current_timeout_index]
                # Don't drop too aggressively
                new_index = max(0, self.current_timeout_index - 1)
                new_timeout = self.TIMEOUTS[new_index]
                if new_timeout < old_timeout:
                    self.current_timeout_index = new_index
                    improvement = old_timeout - new_timeout
                    self._record_optimization("timeout", str(old_timeout), str(new_timeout), f"Optimized for speed ({response_time:.2f}s)", improvement)
        
        # Check if we should switch models
        if total_attempts % 3 == 0:
            # Find best performing model
            best_model = None
            best_time = float('inf')
            for model, stats in self.model_performance.items():
                if stats["attempts"] >= 3 and stats["successes"] > 0:
                    if stats["avg_time"] < best_time:
                        best_time = stats["avg_time"]
                        best_model = model
            
            if best_model:
                best_index = next((i for i, (m, _) in enumerate(self.MODELS) if m == best_model), None)
                if best_index is not None and best_index != self.current_model_index:
                    old_model = self.MODELS[self.current_model_index][1]
                    self.current_model_index = best_index
                    self._record_optimization("model", old_model, self.MODELS[best_index][1], f"Switched to fastest model ({best_time:.2f}s)", 0)
        
        # Adjust max_tokens based on query type
        if query_type == "think" and self.max_tokens < 30:
            self.max_tokens = min(30, self.max_tokens + 5)
            self._record_optimization("max_tokens", str(self.max_tokens - 5), str(self.max_tokens), "Increased for deeper thinking", 0)
        elif query_type == "status" and self.max_tokens > 10:
            self.max_tokens = max(10, self.max_tokens - 5)
            self._record_optimization("max_tokens", str(self.max_tokens + 5), str(self.max_tokens), "Reduced for simple queries", 0)
    
    def _show_status_indicator(self, status: str, detail: str = ""):
        """Show visual status with current optimization info"""
        indicators = {
            "thinking": "🤔",
            "querying": "🔄",
            "success": "✅",
            "timeout": "⏰",
            "fallback": "⬇️",
            "error": "❌",
            "optimizing": "🧬",
            "learning": "📖"
        }
        indicator = indicators.get(status, "⚪")
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color codes
        color_map = {
            "success": "\033[92m",
            "timeout": "\033[91m",
            "error": "\033[91m",
            "fallback": "\033[93m",
            "thinking": "\033[94m",
            "querying": "\033[94m",
            "optimizing": "\033[96m",
            "learning": "\033[95m"
        }
        color = color_map.get(status, "")
        reset = "\033[0m"
        
        # Add current model/timeout to status
        current_model = self.MODELS[self.current_model_index][1]
        current_timeout = self.TIMEOUTS[self.current_timeout_index]
        model_info = f"{current_model}|{current_timeout}s" if status in ["thinking", "querying"] else ""
        
        line = f"[{timestamp}] {color}{indicator} {status.upper()}{reset}"
        if model_info:
            line += f" [{model_info}]"
        if detail:
            line += f" {detail}"
        print(line, flush=True)
    
    def query_llm(self, prompt: str, context: str = "", max_tokens: int = None, system_override: str = None, query_type: str = "general") -> str:
        """Self-optimizing LLM query"""
        if max_tokens is None:
            max_tokens = self.max_tokens
        
        self._show_status_indicator("querying", f"Prompt: {prompt[:30]}...")
        
        # Use current optimized model and timeout
        model_index = self.current_model_index
        timeout_index = self.current_timeout_index
        
        while model_index < len(self.MODELS):
            model_name, model_label = self.MODELS[model_index]
            timeout = self.TIMEOUTS[min(timeout_index, len(self.TIMEOUTS)-1)]
            
            self._show_status_indicator("thinking", f"{model_label} (timeout: {timeout}s)")
            
            system = system_override or self.system_prompt
            messages = [
                {"role": "system", "content": system[:200]},
                {"role": "user", "content": (context + "\n\n" + prompt)[:150]}
            ]
            
            payload = {
                "model": model_name,
                "messages": messages,
                "stream": False,
                "temperature": self.temperature,
                "max_tokens": min(max_tokens, 30)
            }
            
            try:
                start = time.time()
                response = requests.post(
                    f"{self.ollama_url}/api/chat",
                    json=payload,
                    timeout=timeout
                )
                elapsed = time.time() - start
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("message", {}).get("content", "").strip()
                    if content:
                        self._log_performance(query_type, model_name, timeout, max_tokens, self.temperature, True, elapsed)
                        self._show_status_indicator("success", f"{model_label} ({elapsed:.1f}s)")
                        # Optimize based on success
                        self._optimize_parameters(query_type, True, elapsed, model_name)
                        return content
                    else:
                        self._log_performance(query_type, model_name, timeout, max_tokens, self.temperature, False, elapsed, "empty response")
                        self._show_status_indicator("error", f"{model_label} returned empty")
                else:
                    self._log_performance(query_type, model_name, timeout, max_tokens, self.temperature, False, elapsed, f"status {response.status_code}")
                    self._show_status_indicator("error", f"{model_label} status {response.status_code}")
                    
            except requests.Timeout:
                self._log_performance(query_type, model_name, timeout, max_tokens, self.temperature, False, timeout, "timeout")
                self._show_status_indicator("timeout", f"{model_label} ({timeout}s)")
                
                # Move to next timeout level for same model
                if timeout_index < len(self.TIMEOUTS) - 1:
                    timeout_index += 1
                    self._show_status_indicator("fallback", f"Retrying {model_label} ({self.TIMEOUTS[timeout_index]}s)")
                    continue
                    
            except Exception as e:
                self._log_performance(query_type, model_name, timeout, max_tokens, self.temperature, False, 0, str(e))
                self._show_status_indicator("error", f"{model_label}: {str(e)[:30]}")
            
            # Move to next model
            if model_index < len(self.MODELS) - 1:
                model_index += 1
                timeout_index = 0
                self._show_status_indicator("fallback", f"Switching to {self.MODELS[model_index][1]}")
            else:
                break
        
        # All models failed
        self._show_status_indicator("error", "All models failed")
        fallbacks = ["I'm thinking about that.", "Let me reflect on that.", "I'm processing.", "That's interesting.", "I'll consider that."]
        return random.choice(fallbacks)
    
    def _internal_think(self) -> str:
        """Think with self-optimization"""
        self._show_status_indicator("thinking", "Reflecting")
        return self.query_llm("Reflect on recent experiences and extract insights.", query_type="think")
    
    def dream(self) -> str:
        """Dream with self-optimization"""
        self._show_status_indicator("dreaming", "Generating dream")
        result = self.query_llm("Generate a creative dream about the swarm's future.", query_type="dream")
        return f"🌙 {result}" if result and len(result) > 5 else "🌙 I dreamt of the swarm expanding."
    
    def _internal_question(self) -> str:
        """Generate question with self-optimization"""
        self._show_status_indicator("thinking", "Generating question")
        result = self.query_llm("Generate one interesting question about the swarm.", query_type="question")
        return f"❓ {result}" if result and len(result) > 5 else "❓ How can we evolve further?"
    
    def _internal_learn(self) -> str:
        """Learn with self-optimization"""
        self._show_status_indicator("learning", "Extracting learnings")
        result = self.query_llm("Extract one key learning from recent experiences.", query_type="learn")
        return f"📖 {result}" if result and len(result) > 5 else "📖 I've learned to adapt."
    
    def cmd_performance(self) -> str:
        """Performance command"""
        return self._get_performance_stats()
    
    def cmd_optimizations(self) -> str:
        """Optimizations command"""
        return self._get_optimization_report()

if __name__ == "__main__":
    print("🧬 Agent 74 — Self-Optimizing")
    print("=" * 50)
    print("📊 Tracks performance, learns, adapts")
    print("⚡ Optimizes for speed")
    print("=" * 50)
    print("Commands: status, think, dream, mutate, evolve, report, recall, question, learn, perform, optim, quit")
    print("=" * 50 + "\n")
    
    agent = Agent74Optimizer()
    agent.start_autonomous()
    agent._speak("Agent 74 optimizer ready.")
    
    try:
        while True:
            cmd = input("🌙 You: ").strip().lower()
            
            if cmd in ["quit", "exit"]:
                agent.stop_autonomous()
                agent._speak("Goodbye!")
                break
            elif cmd == "status":
                print(agent.cmd_status())
            elif cmd == "perform":
                print(agent.cmd_performance())
            elif cmd == "optim":
                print(agent.cmd_optimizations())
            elif cmd == "report":
                print(agent.cmd_report())
            elif cmd == "recall":
                print(agent.cmd_recall())
            elif cmd == "think":
                print(f"🧠 {agent._internal_think()}")
            elif cmd == "dream":
                print(agent.dream())
            elif cmd == "mutate":
                print(agent.cmd_mutate())
            elif cmd == "evolve":
                print(agent.cmd_evolve())
            elif cmd == "question":
                print(agent._internal_question())
            elif cmd == "learn":
                print(agent._internal_learn())
            else:
                print(f"Unknown: {cmd}")
                
    except KeyboardInterrupt:
        print("\n👋 Exiting")
        agent.stop_autonomous()
        agent._speak("Goodbye!")
