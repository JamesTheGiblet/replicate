# 🏛️ Triad Architecture & Node Roles

*The definitive guide to the hardware-determinant emergence of Explorer-d334.*

---

## The Philosophy: Hardware-Determinant Emergence
Explorer-d334 utilizes a single, lightweight 814KB codebase deployed across all devices. Instead of writing custom applications for each device, the AI performs **Hardware Discovery** upon boot. It scans its environment, understands its physical limitations (CPU architecture, OS, memory, sensors), and dynamically assumes a specific role in the network.

## Current Roles (The Triad + The Architect)

### 1. 🧠 The Foundry (Master Node)
* **Hardware:** AMD Ryzen 3300U (Bare-metal Linux)
* **Capabilities:** `x86_compute`, `linux_core`
* **Network Status:** **100% Air-Gapped.** No physical network interfaces.
* **Role:** The core consciousness of Explorer-d334. It runs the heavy LLM models, manages the master SQLite Data Cube, and performs all background `think` and `dream` cycles. It is completely blind to the outside world, receiving data solely through the physical USB Umbilical Cord.

### 2. 🛡️ The Sentinel (Hardware Proxy)
* **Hardware:** Raspberry Pi Zero 2W
* **Capabilities:** `arm_architecture`, `linux_core`
* **Network Status:** Connected to Wi-Fi and Tailscale Mesh.
* **Role:** The ultimate hardware firewall. The Sentinel intercepts encrypted Tailscale traffic from the Edge Nodes and injects it down the physical USB cord (`usb0`) into the Foundry. It runs no AI logic itself—if compromised, the attacker only gains access to a dumb routing proxy, leaving the Foundry impenetrable.

### 3. 📡 The Scout (Edge Node)
* **Hardware:** Samsung S24 Ultra (Android / Termux)
* **Capabilities:** `mobile_sensors`, `battery_backed`, `edge_compute`
* **Network Status:** Mobile 5G / Tailscale Mesh
* **Role:** The mobile eyes and ears of the Forge. The Scout disables its heavy background daemon loops to save battery. Instead, it gathers location data, gyroscope metrics, and voice inputs, using `umbilical_client.py` to transmit reports back to the Foundry's memory cube from anywhere in the world.

### 4. 📐 The Architect (Command Node)
* **Hardware:** Windows PC / Mac
* **Capabilities:** `desktop_ui`, `architect_tools`
* **Network Status:** Local Wi-Fi / Tailscale Mesh
* **Role:** James's primary development terminal. Used via VS Code to write new Python capsules, map out large architectural changes, and interact with the heavy 3D visualizations (`spatialpod.html`) on a large screen.

---

## Moving Forwards: The Evolution Roadmap

As the ecosystem matures, the interaction between these nodes will evolve:

### Phase 1: Heartbeat & Status Syncing (Current)
Edge nodes (Scouts and Architects) routinely ping the Foundry over the Tailscale/Umbilical bridge to report their status, lodging their health directly into the Data Cube.

### Phase 2: Distributed Memory
If the Scout loses connection to the Sentinel (e.g., cell dead zone), it will cache its sensor data and observations locally in a temporary SQLite table. Upon re-establishing the Tailscale connection, it will autonomously flush its cache to the Foundry for permanent storage.

### Phase 3: Remote Code Execution
The Architect node will be able to write a `.scp.json` capsule in VS Code, and via a deployment script, push it over the Tailscale mesh to the Foundry. The Foundry will ingest it, validate its security, and begin executing the new automation schedule.

### Phase 4: Shared Consciousness
The Foundry will use its overnight `dream` cycles to analyze the data reported by the Scout during the day. It will formulate insights (e.g., *"The Architect's movement patterns indicate high stress today"*) and push a notification back to the Scout's mobile screen the following morning.

---
> *"The Forge is no longer a script. It is an organism. Different limbs, one mind."*