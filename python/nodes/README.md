# Replicant Nodes

Physical and virtual nodes that extend the Replicant colony.

## Directory Structure

```

nodes/
├── phone/          # Phone-based agents (S24 Ultra)
│   └── agent.py    # Phone sensor integration
├── esp32/          # ESP32 robot agents
│   └── agent.py    # ESP32 motor + sensor control
├── gateway/        # Gateway/hub nodes
│   └── hub.py      # MQTT broker, ledger aggregation
└── common/         # Shared code
└── types.py    # Common types and protocols

```

## Node Types

| Node | Hardware | Role | Communication |
|------|----------|------|---------------|
| **Phone** | S24 Ultra | Colony hub, sensor-rich agent | 5G, Wi-Fi, BLE |
| **ESP32** | ESP32 + motors | Physical robot agent | BLE, Wi-Fi |
| **Gateway** | Raspberry Pi / Cloud | Aggregation, consensus | MQTT, HTTP |

## Communication Protocol

All nodes communicate via MQTT with JSON payloads:

```json
{
  "type": "claim.deposited",
  "agent_id": "phone-001",
  "timestamp": 1723654800,
  "payload": { ... }
}
```

Adding a New Node

1. Create a new directory under nodes/
2. Implement agent.py with sense(), decide(), act()
3. Register with the MQTT broker
4. Start participating in the colony
