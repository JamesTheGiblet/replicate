
API Reference

REST API (Web Interface)

The web interface exposes a simple REST API.

Endpoints

Endpoint Method Description
/chat POST Send message to forge
/history GET Get chat history
/stats GET Get cache statistics
/clear POST Clear history

Example

```bash
# Send a message
curl -X POST http://localhost:8085/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, Explorer!"}'

# Get history
curl http://localhost:8085/history
```

Python API

Import modules

```python
from src.unified_consciousness import UnifiedConsciousnessLLM
from src.simple_trust import SimpleTrust
from src.working_replicator import generate_c

# Create consciousness instance
c = UnifiedConsciousnessLLM()
print(c.think())
```

Available Modules

Module Purpose
unified_consciousness.py Core consciousness
simple_trust.py Trust system
working_replicator.py Code generation
forge_memory.py Memory storage
security_agent.py Security scanning

Command Line Interface

All CLI commands can be called directly:

```bash
# Python scripts
python src/unified_consciousness.py think
python src/forge_time.py
python src/device_awareness.py
```

WebSocket (Coming Soon)

Real-time streaming responses will be available in v1.1.

---

🔥 Build on the forge. Extend its capabilities. 🔥
