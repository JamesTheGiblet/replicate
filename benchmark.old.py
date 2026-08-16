#!/usr/bin/env python3
"""
Replicant Benchmark: Python vs Rust
Compares performance, memory, and swarm behaviour
"""

import sys
import os
import time
import json
import subprocess
import statistics
from pathlib import Path

# Add Python src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python', 'src'))

# Benchmark configuration
BENCHMARK_CONFIG = {
    "ticks": [50, 100, 200, 500],
    "agents": [10, 20, 50, 100],
    "runs": 3,
    "seed": 42,
}

class PythonBenchmark:
    """Benchmark Python Replicant"""

    def __init__(self):
        self.world = None
        self.results = {}

    def setup(self, n_agents: int, seed: int = 42):
        from world import World
        from founders import create_founders

        config = {
            "run": {"seed": seed, "ticks": 100},
            "leighton": {"k_per_day_forage": 0.05, "k_per_day_signal": 0.02},
            "claims": {"food": {"retention_per_tick": 0.90, "commit_attestations": 2}},
            "environment": {"n_patches": 10}
        }

        world = World(seed, config)
        founders = create_founders()
        for name, agent in founders.items():
            world.add_agent(agent)

        # Add extra agents if needed
        for i in range(n_agents - 10):
            from agent import Agent, Traits
            from capsule import Capsule
            from leighton import LambdaState

            capsule = Capsule.mint(
                inherits=["replicant/protocol/run-v1"],
                declaration={"name": f"TestAgent_{i}"},
                licence="MSL-1.0"
            )
            agent = Agent(
                scp_id=capsule.scp_id,
                capsule=capsule,
                x=50.0 + i * 2,
                y=50.0 + i * 2,
                traits=Traits(),
                lambda_state=LambdaState(),
                birth_tick=0,
                role="tester"
            )
            world.add_agent(agent)

        self.world = world
        return world

    def run(self, ticks: int):
        start = time.perf_counter()
        for _ in range(ticks):
            self.world.tick_driver()
        end = time.perf_counter()
        return end - start

    def get_stats(self):
        alive = sum(1 for a in self.world.agents.values() if a.alive)
        claims = len(self.world.claims)
        counters = sum(1 for c in self.world.claims.values() if c.lens == "COUNTER")
        health = self.world.environment.metrics["overall_health"]
        return {
            "alive": alive,
            "claims": claims,
            "counters": counters,
            "health": round(health, 3),
            "ledger_entries": len(self.world.ledger),
        }


class RustBenchmark:
    """Benchmark Rust Replicant by invoking a pre-built release binary."""

    def __init__(self, rust_dir: str = "rust"):
        self.rust_dir = Path(rust_dir)
        self.binary = self.rust_dir / "target" / "release" / "replicant_bench"
        self.built = False

    def ensure_built(self):
        """Build once, outside the timing loop. cargo run pays the toolchain
        check on every single invocation -- for 16 data points that's 16
        redundant compiler checks, and it's what made small workloads look
        slower in Rust than in Python: the number being measured was mostly
        cargo, not the simulation."""
        if self.built:
            return
        print("🦀 Building Rust benchmark binary (release, once)...", flush=True)
        result = subprocess.run(
            ["cargo", "build", "--release", "--quiet", "--bin", "replicant_bench"],
            cwd=self.rust_dir,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            print("❌ Rust build failed:")
            print(result.stderr)
            raise RuntimeError("cargo build --release failed -- see stderr above")
        if not self.binary.exists():
            raise RuntimeError(f"build succeeded but binary not found at {self.binary}")
        self.built = True
        print(f"✅ Built: {self.binary}")

    def run_benchmark(self, n_agents: int, ticks: int, runs: int = 3) -> dict:
        """Run the compiled binary directly -- no cargo, no toolchain check.

        Uses the simulation's own reported time_sec as the timing figure,
        not wall-clock around the subprocess. The binary already starts its
        clock after world/agent setup and stops it after the tick loop
        (see replicant_bench.rs) -- that is the correct methodology and it
        matches how PythonBenchmark.run() is timed. Wall-clock around the
        subprocess would re-introduce process-spawn overhead into the figure.
        """
        self.ensure_built()

        times = []
        stats = {}

        for run in range(runs):
            cmd = [
                str(self.binary),
                "--agents", str(n_agents),
                "--ticks", str(ticks),
                "--seed", "42",
            ]
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
            except subprocess.TimeoutExpired:
                print(f"  ⚠️  Rust benchmark timed out at {ticks} ticks")
                times.append(float('inf'))
                continue

            if result.returncode != 0:
                print(f"  ⚠️  Rust binary exited {result.returncode}: {result.stderr.strip()[:200]}")
                times.append(float('inf'))
                continue

            # The binary prints exactly one JSON line. Parse failures are
            # reported, not swallowed -- a silent `except: pass` here is what
            # let every "behaviour comparison" row show N/A with no clue why.
            try:
                data = json.loads(result.stdout.strip())
            except json.JSONDecodeError as e:
                print(f"  ⚠️  Could not parse Rust output as JSON: {e}")
                print(f"      stdout was: {result.stdout[:200]!r}")
                times.append(float('inf'))
                continue

            times.append(data["time_sec"])
            stats = data.get("stats", {})

        valid = [t for t in times if t != float('inf')]
        return {
            "time_avg": statistics.mean(valid) if valid else float('inf'),
            "time_min": min(valid) if valid else float('inf'),
            "time_max": max(valid) if valid else float('inf'),
            "stats": stats,
        }


def run_benchmark_suite():
    """Run the complete benchmark suite"""
    print("\n🧬 Replicant Benchmark: Python vs Rust")
    print("=" * 60)

    results = {
        "python": {},
        "rust": {},
        "comparison": {}
    }

    python_bench = PythonBenchmark()
    rust_bench = RustBenchmark()
    rust_bench.ensure_built()          # build once, up front, before any timing

    # Test different configurations
    for n_agents in BENCHMARK_CONFIG["agents"]:
        for ticks in BENCHMARK_CONFIG["ticks"]:
            key = f"agents_{n_agents}_ticks_{ticks}"
            print(f"\n📊 Testing: {n_agents} agents, {ticks} ticks")
            print("-" * 40)

            # Python
            print("  🐍 Python...", end=" ", flush=True)
            try:
                python_bench.setup(n_agents, BENCHMARK_CONFIG["seed"])
                py_time = python_bench.run(ticks)
                py_stats = python_bench.get_stats()
                print(f"✅ {py_time:.3f}s")

                results["python"][key] = {
                    "time": py_time,
                    "stats": py_stats
                }
            except Exception as e:
                print(f"❌ Error: {e}")
                results["python"][key] = {"time": float('inf'), "error": str(e)}

            # Rust
            print("  🦀 Rust...", end=" ", flush=True)
            try:
                rust_result = rust_bench.run_benchmark(n_agents, ticks, 1)
                rust_time = rust_result["time_avg"]
                rust_stats = rust_result["stats"]

                if rust_time != float('inf'):
                    print(f"✅ {rust_time:.3f}s")
                else:
                    print("❌ Failed")

                results["rust"][key] = {
                    "time": rust_time,
                    "stats": rust_stats
                }
            except Exception as e:
                print(f"❌ Error: {e}")
                results["rust"][key] = {"time": float('inf'), "error": str(e)}

            # Comparison
            py_time = results["python"].get(key, {}).get("time", float('inf'))
            rust_time = results["rust"].get(key, {}).get("time", float('inf'))

            if py_time != float('inf') and rust_time != float('inf'):
                ratio = py_time / rust_time if rust_time > 0 else float('inf')
                results["comparison"][key] = {
                    "speedup": ratio,
                    "faster": "Rust" if ratio > 1 else "Python" if ratio < 1 else "Tie",
                    "py_time": py_time,
                    "rust_time": rust_time,
                }

    return results


def print_summary(results):
    """Print a summary of the benchmark results"""
    print("\n" + "=" * 60)
    print("📊 BENCHMARK SUMMARY")
    print("=" * 60)

    # Speedup table
    print("\n🔄 Speed Comparison (Rust vs Python):")
    print("-" * 50)
    print(f"{'Agents':>8} | {'Ticks':>8} | {'Python (s)':>12} | {'Rust (s)':>12} | {'Speedup':>10}")
    print("-" * 50)

    speedups = []

    for key, comp in results["comparison"].items():
        parts = key.split("_")
        n_agents = parts[1]
        ticks = parts[3]
        py_time = comp.get("py_time", 0)
        rust_time = comp.get("rust_time", 0)
        speedup = comp.get("speedup", 0)

        if py_time > 0 and rust_time > 0:
            print(f"{n_agents:>8} | {ticks:>8} | {py_time:>12.3f} | {rust_time:>12.3f} | {speedup:>10.1f}x")
            speedups.append(speedup)

    print("-" * 50)

    if speedups:
        avg_speedup = statistics.mean(speedups)
        max_speedup = max(speedups)
        min_speedup = min(speedups)
        print(f"\n📈 Average speedup: {avg_speedup:.1f}x")
        print(f"📈 Max speedup:    {max_speedup:.1f}x")
        print(f"📈 Min speedup:    {min_speedup:.1f}x")
    else:
        avg_speedup = 0

    # Stats comparison
    print("\n📊 Behaviour Comparison (200 ticks, 10 agents):")
    print("-" * 50)

    py_key = "agents_10_ticks_200"
    rust_key = "agents_10_ticks_200"

    py_stats = results["python"].get(py_key, {}).get("stats", {})
    rust_stats = results["rust"].get(rust_key, {}).get("stats", {})

    print(f"{'Metric':<15} | {'Python':>12} | {'Rust':>12}")
    print("-" * 50)
    for metric in ["alive", "claims", "counters", "health"]:
        py_val = py_stats.get(metric, "N/A")
        rust_val = rust_stats.get(metric, "N/A")
        print(f"{metric:<15} | {str(py_val):>12} | {str(rust_val):>12}")

    print("\n" + "=" * 60)

    # Recommendations
    print("\n🎯 Recommendations:")
    if avg_speedup > 5:
        print("  ✅ Rust is significantly faster. Use Rust for production.")
    elif avg_speedup > 2:
        print("  ✅ Rust is moderately faster. Consider Rust for performance-critical tasks.")
    else:
        print("  ⚠️  Python and Rust are comparable. Choose based on ecosystem needs.")

    if py_stats and rust_stats:
        py_counters = py_stats.get("counters", 0)
        rust_counters = rust_stats.get("counters", 0)
        if abs(py_counters - rust_counters) > 1:
            print(f"  ⚠️  Behaviour differs: Python ({py_counters}) vs Rust ({rust_counters}) COUNTER claims.")


if __name__ == "__main__":
    print("🧬 Replicant Benchmark Suite")
    print("=" * 60)

    results = run_benchmark_suite()
    print_summary(results)

    # Save results
    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n📁 Results saved to benchmark_results.json")
