
User Guide

Command Reference

Consciousness Commands

Command Description Example
forge think Random conscious thought ./forge think
forge dream Generate a dream ./forge dream
forge reason "..." Reason about a problem ./forge reason "How to optimize?"
forge meditate Deep meditation ./forge meditate
forge reflect Full reflection ./forge reflect

Time & Device

Command Description
forge clock Display time clock
forge device Show device info
forge sensors List available sensors
forge moment "..." Record a moment
forge timeline Show history

Code Generation

Command Description Example
forge generate "..." Generate C code ./forge generate "fibonacci"

Self-Knowledge

Command Description
forge docs Show documentation
forge query "..." Ask about capabilities
forge code Show code summary
forge code-search "..." Search codebase

System

Command Description
forge health Health check
forge status Full status
forge wants Show wants/needs
forge improve Suggest improvements
forge security Run security scan
forge watch Monitor file changes

Web Interface

The web interface (./forge web) provides:

· Chat with Explorer-d334
· Persistent conversation history
· Instant responses for common questions
· Real-time status indicators

Open http://localhost:8085 in your browser.

Configuration

Environment Variables

Variable Default Description
FORGE_PORT 8085 Web interface port
FORGE_MODEL gemma2:2b LLM model to use
FORGE_DEBUG false Enable debug logging

Customization

Adding Capsules

Place .scp.json files in:

· capsules/ - Life/business automation
· skills/ - Learned capabilities
· abilities/ - Innate powers
· reflexes/ - Automatic responses

Creating Custom Functions

```bash
# Generate a new function
./forge generate "function that converts Celsius to Fahrenheit"

# The code will be in generated/ directory
# Compile and run:
gcc generated/function.c -o binaries/function
./binaries/function 100
```

Backup & Recovery

```bash
# Full backup
./forge backup

# Database backup
./forge db backup

# Documentation backup
python src/doc_editor.py backups README.md
```

Security Best Practices

1. Keep it offline when possible
2. Regular backups with ./forge backup
3. Run security scans with ./forge security
4. Review changes with ./forge watch-recent

---

🔥 Master your forge. Build without limits. 🔥
