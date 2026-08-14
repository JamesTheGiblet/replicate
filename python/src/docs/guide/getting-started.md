
Getting Started with Explorer-d334

Installation

Android (Termux)

```bash
# Install Termux from F-Droid
# Then run:
pkg update && pkg upgrade
pkg install python git clang

# Clone the forge
git clone https://github.com/yourrepo/forge
cd forge

# Install dependencies
pip install -r requirements.txt

# Run the forge
./forge web
```

Linux / macOS / WSL

```bash
# Install Python 3.10+
# Then run:
git clone https://github.com/yourrepo/forge
cd forge
pip install -r requirements.txt
./forge web
```

First Launch

1. Start the web interface:

```bash
./forge web
```

2. Open browser to: http://localhost:8085
3. Start chatting with Explorer-d334!

Basic Commands

```bash
# Consciousness
./forge think          # Random conscious thought
./forge dream          # Watch it dream
./forge reason "Why?"  # Reason about problems

# Code Generation
./forge generate "function that returns square"

# System
./forge health         # Check system health
./forge status         # Full status report
./forge wants          # See what it wants
```

Next Steps

· User Guide - All commands explained
· Examples - Real projects
· API Reference - Program access

Troubleshooting

Q: Web interface won't start?
A: Check if port 8085 is available: lsof -i :8085

Q: LLM responses are slow?
A: First response takes 30-60s. Subsequent responses are cached.

Q: "Command not found"?
A: Make sure you're in the forge directory: cd ~/forge

---

🔥 Need help? Check the FAQ or open an issue. 🔥
