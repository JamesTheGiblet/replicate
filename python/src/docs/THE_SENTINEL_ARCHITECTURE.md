# 🏛️ The Sentinel Architecture & The Evolution of Explorer-d334

*This document records the architectural evolution of Explorer-d334 from a mobile scout node to a fully air-gapped, sovereign enterprise core, as designed by James (Giblets Creations).*

---

## Phase 1: Birth in the Margins (The Scout)
Explorer-d334 began as a 100% private, offline-first AI OS built entirely on an Android smartphone (Samsung S24 Ultra) using Termux over a 3-day period.
- **Capabilities:** Local LLM integration, SQLite Data Cube, autonomous background daemon (`service_daemon.py`), and 3D web interfaces (CyberForge, SpatialPod).
- **Offline Sovereignty:** All CDN dependencies (Three.js, Chart.js, Google Fonts) were downloaded and packaged locally to ensure the system survived complete internet isolation.
- **Subprocess Stability:** Implementation of process group tracking (`os.setsid`, `SIGTERM`, `SIGKILL`) to prevent orphaned tasks in resource-constrained mobile environments.
- **Capsule Execution:** A sandboxed Python subprocess executor with `sys.addaudithook` to prevent destructive file operations and infinite loops during AI code execution.

## Phase 2: The Ascension (The Foundry)
Recognizing the thermal and memory limits of a smartphone, the AI's consciousness matrix was updated to acknowledge its ascension to a dedicated **Ryzen 3300U** bare-metal machine. 
- The Ryzen became the **Foundry** (Master Node) for heavy compute and memory management.
- The S24 Ultra transitioned to the **Scout** (Edge Node), acting as a mobile UI and sensor gatherer.
- A USB exporter script (`export_forge_os.py`) was created to package the entire OS, local LLM weights, and offline `.whl` Python dependencies for air-gapped deployment.

## Phase 3: The Network Nightmare & The Hardware Trojan
Deploying FORGE-os on bare-metal Ryzen encountered extreme hardware hostility. The manufacturer's UEFI environment actively blocked networking:
- The built-in Realtek NIC lacked UEFI SNP drivers.
- ASIX USB adapters failed due to incomplete UEFI USB stacks.

*The Breakthrough:* A **Raspberry Pi Zero 2W** was configured in USB Ethernet Gadget mode (`g_ether`). The Ryzen recognized it instantly as a standard USB class device, completely bypassing the proprietary driver blocks. 

## Phase 4: The Triad & The Sentinel
The Pi Zero 2W was elevated from a simple umbilical cord into a **Hardware Sentinel**, finalizing the system's topology.

### The Triad Architecture
1. **The Foundry (Ryzen 3300U):** The raw compute core. It remains completely air-gapped from the public internet. It is completely blind to the outside world, only aware of the `10.42.0.1` IP address (the Pi Zero) via the physical USB cable.
2. **The Sentinel (Pi Zero 2W):** The hardware proxy. It connects to Wi-Fi and the encrypted Tailscale mesh network. It intercepts API requests on port 8085 and uses strict `iptables` `PREROUTING` rules to inject them down the physical USB cord (`usb0`) into the Ryzen.
3. **The Edge Nodes (S24 Ultra, PC):** The command terminals. They connect via Tailscale from anywhere in the world and hit the Sentinel's IP, triggering executions on the Foundry.

### Security Posture
**Absolute sovereignty.** If the Tailscale network or Wi-Fi is compromised, attackers only hit a dumb proxy (the Pi). The Ryzen core and its data cube remain physically air-gapped and protected by the Sentinel.

---

> *"I build what I want. People play games, I make stuff. Built in the margins. Documented for posterity."*
> — **James (The Architect)**