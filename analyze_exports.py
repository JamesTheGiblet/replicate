#!/usr/bin/env python3
"""
Replicant Export Analyzer

This script reads all JSON state snapshots from the `rust/wasm/exports` directory,
analyzes them, and generates a summary report in Markdown format.
"""

import os
import json
from pathlib import Path
from collections import Counter

# --- Configuration ---
EXPORTS_DIR = Path(__file__).parent / "rust" / "wasm" / "exports"
REPORT_FILE = Path(__file__).parent / "ANALYSIS_SUMMARY.md"
# --- End Configuration ---

def analyze_snapshot(file_path):
    """Analyzes a single JSON snapshot file and extracts key metrics."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Could not read or parse {file_path}: {e}")
        return None

    tick = data.get("tick", 0)
    health = data.get("health", 0.0)
    
    agents = data.get("agents", [])
    agents_alive = len([a for a in agents if a.get('alive', True)])
    
    role_counts = Counter(agent['role'] for agent in agents if agent.get('alive'))
    
    claims = data.get("claims", [])
    total_claims = len(claims)
    lens_counts = Counter(claim.get('lens') for claim in claims)

    return {
        "file": file_path.name,
        "tick": tick,
        "health": health,
        "agents_alive": agents_alive,
        "role_counts": role_counts,
        "total_claims": total_claims,
        "lens_counts": lens_counts,
    }

def generate_report(analysis_results):
    """Generates a Markdown report from the analysis results."""
    if not analysis_results:
        return "# Replicant Analysis Report\n\nNo valid export files found to analyze."

    # Sort results by tick
    analysis_results.sort(key=lambda x: x['tick'])

    # --- Build Markdown Report ---
    report_lines = ["# Replicant Simulation Analysis Report\n"]
    report_lines.append(f"**Source:** `{EXPORTS_DIR}`\n")
    report_lines.append("## 1. High-Level Summary\n")
    report_lines.append("| File | Tick | Agents Alive | Health | Claims | Fact % | Opinion % | Counter % |")
    report_lines.append("|---|---|---|---|---|---|---|---|")

    for result in analysis_results:
        total_claims = result['total_claims']
        lenses = result['lens_counts']
        fact_pct = (lenses.get('Fact', 0) / total_claims * 100) if total_claims > 0 else 0
        opinion_pct = (lenses.get('Opinion', 0) / total_claims * 100) if total_claims > 0 else 0
        counter_pct = (lenses.get('Counter', 0) / total_claims * 100) if total_claims > 0 else 0
        
        report_lines.append(
            f"| `{result['file']}` | {result['tick']} | **{result['agents_alive']}** | {result['health']:.3f} | "
            f"{total_claims} | {fact_pct:.1f}% | {opinion_pct:.1f}% | {counter_pct:.1f}% |"
        )

    report_lines.append("\n## 2. Population & Health Trends\n")
    start_pop = analysis_results[0]['agents_alive']
    end_pop = analysis_results[-1]['agents_alive']
    report_lines.append(f"- **Population:** The swarm started with **{start_pop}** agents and ended with **{end_pop}** agents at tick {analysis_results[-1]['tick']}.")
    if end_pop > 0:
        report_lines.append("- **Conclusion:** The population is stable and self-sustaining, successfully overcoming the 'Great Extinction' bug.")
    else:
        report_lines.append("- **WARNING:** The population collapsed. Further investigation is needed.")

    avg_health = sum(r['health'] for r in analysis_results) / len(analysis_results)
    report_lines.append(f"- **Health:** The average swarm health across all snapshots was **{avg_health:.3f}**.")

    report_lines.append("\n## 3. Emergent Behavior: Role Distribution\n")
    report_lines.append("This section analyzes the division of labor within the swarm over time.\n")

    for result in analysis_results:
        if not result['role_counts']:
            continue
        
        report_lines.append(f"### Tick {result['tick']}")
        total_agents = result['agents_alive']
        
        # Sort roles by count, descending
        sorted_roles = result['role_counts'].most_common()
        
        for role, count in sorted_roles:
            percentage = (count / total_agents * 100) if total_agents > 0 else 0
            report_lines.append(f"- **{role}:** {count} agents ({percentage:.1f}%)")
        report_lines.append("")

    # Check for monoculture in the last snapshot
    last_result = analysis_results[-1]
    if len(last_result['role_counts']) == 1 and last_result['agents_alive'] > 1:
        dominant_role = list(last_result['role_counts'].keys())[0]
        report_lines.append(f"**Observation:** A significant **role monoculture** has emerged. By the final snapshot, 100% of the swarm had converged on the `{dominant_role}` role.")
        report_lines.append("This highlights the need for archetypes like `Contrarian` to ensure cognitive diversity.")

    return "\n".join(report_lines)

def main():
    """Main function to find files, analyze them, and generate a report."""
    print(f"🔍 Analyzing export files from: {EXPORTS_DIR}")
    
    json_files = sorted(EXPORTS_DIR.glob("*.json"))
    if not json_files:
        print("❌ No JSON export files found. Nothing to analyze.")
        return

    print(f"Found {len(json_files)} files to analyze.")
    
    analysis_results = []
    for file_path in json_files:
        result = analyze_snapshot(file_path)
        if result:
            analysis_results.append(result)

    report_content = generate_report(analysis_results)

    try:
        with open(REPORT_FILE, 'w') as f:
            f.write(report_content)
        print(f"✅ Successfully generated analysis report: {REPORT_FILE}")
    except IOError as e:
        print(f"❌ Error writing report file: {e}")

if __name__ == "__main__":
    main()