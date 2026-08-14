# Replicant-ESP32 Bridge: Colony Integration

## Overview

This bridges the `esp32-robotics-extension-spec.md` with Replicant's distributed colony architecture. The ESP32 robot becomes a **physical agent** in the Replicant swarm.

---

## Architecture Mapping

| ESP32 Layer | Replicant Concept | Implementation |
|-------------|-------------------|----------------|
| **Real-time control loop** | Agent `sense()` | Encoder/sensor reads |
| **Behavior layer** | Agent `decide()` | Intent generation |
| **Safety layer** | `is_rogue` / `is_expelled` | Hardware emergency stop |
| **Learning layer** | `Traits.mutate()` | Bounded parameter tuning |
| **Telemetry** | `Ledger` | MQTT state export |

---

## Communication

```

┌─────────────────────────────────────────────────────────────────┐
│                    COLONY + ESP32 ROBOT                         │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              MQTT Broker (Gateway)                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│         │              │              │              │          │
│         ▼              ▼              ▼              ▼          │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐  │
│  │ Simulation │ │ Simulation │ │   ESP32    │ │   ESP32    │  │
│  │  Agent #1  │ │  Agent #2  │ │   Robot    │ │   Robot    │  │
│  │  (Scout)   │ │  (Forager) │ │   #1       │ │   #2       │  │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘  │
│                                                                 │
│              "The swarm learns. The liar pays."                 │
└─────────────────────────────────────────────────────────────────┘

```

---

## Message Format (Replicant-Compatible)

```json
{
  "header": {
    "type": "claim.deposited",
    "agent_id": "esp32-robot-001",
    "timestamp": 1723654800,
    "signature": "..."
  },
  "payload": {
    "claim_id": "claim-12345",
    "x": 42.5,
    "y": 87.3,
    "lens": "OPINION",
    "strength": 0.65,
    "sensor_data": {
      "distance_cm": 25.0,
      "encoder_left": 1234,
      "encoder_right": 1200,
      "heading": 1.23,
      "battery": 7.2
    }
  }
}
```

---

Agent-to-Robot Mapping

Agent Role Robot Behaviour Sensor Input
Scout Explore, map Distance, IMU
Forager Seek resources Camera, bumper
Builder Arrange objects Encoders, grip
Observer Monitor, verify Camera, distance

---

Replicant Concepts on ESP32

λ (Reputation) on Hardware

```rust
// ESP32 implementation
const QUARANTINE_THRESHOLD: f32 = 0.60;
const EXPULSION_THRESHOLD: f32 = 0.15;

struct LambdaState {
    base: f32,
    events: [LambdaEvent; 32],  // Fixed array for memory constraints
    offence_count: u8,
}

impl LambdaState {
    fn compute(&self, tick: u32) -> f32 {
        // Same formula as Replicant
        // Uses fixed-point arithmetic
    }
}
```

Safety as Reputation

```
λ > 0.60  →  Full autonomy
λ 0.15-0.60 →  Reduced speed, cautious
λ < 0.15  →  Emergency stop, wait for human
```

Traits as Tuning Parameters

Trait ESP32 Parameter
forage_bias exploration_bias
deposit_rate marking_frequency
scepticism obstacle_margin
broadcast_cost telemetry_rate

---

Implementation Plan

Phase 1: Bridge Layer (Week 1)

```bash
# Create bridge module
mkdir -p ~/Download/replicate/rust/src/bridge
cat > ~/Download/replicate/rust/src/bridge/mod.rs << 'RUST'
//! Bridge between Replicant colony and ESP32 robots

mod esp32_agent;
mod mqtt_interface;
mod serialization;

pub use esp32_agent::ESP32Agent;
pub use mqtt_interface::MQTTBridge;
pub use serialization::*;
RUST
```

Phase 2: MQTT Integration (Week 2)

```rust
// src/bridge/mqtt_interface.rs
pub struct MQTTBridge {
    client: mqtt::Client,
    topic_prefix: String,
}

impl MQTTBridge {
    pub fn publish_claim(&self, claim: &Claim) -> Result<(), mqtt::Error> {
        // Serialize claim as Replicant-compatible JSON
        let payload = serde_json::to_string(claim)?;
        self.client.publish(&format!("{}/claims", self.topic_prefix), &payload)?;
        Ok(())
    }

    pub fn subscribe_to_claims(&self) -> Result<(), mqtt::Error> {
        self.client.subscribe(&format!("{}/claims", self.topic_prefix))?;
        Ok(())
    }
}
```

Phase 3: Hardware Abstraction (Week 3)

```rust
// src/bridge/esp32_agent.rs
pub struct ESP32Agent {
    id: String,
    role: Role,
    x: f32,
    y: f32,
    energy: f32,  // Battery level
    lambda: LambdaState,
    traits: Traits,
    hardware: HardwareInterface,
    bridge: MQTTBridge,
}

impl Agent for ESP32Agent {
    fn sense(&self) -> Percepts {
        // Read from hardware sensors
        Percepts {
            distance: self.hardware.read_distance(),
            encoders: self.hardware.read_encoders(),
            heading: self.hardware.read_heading(),
            battery: self.hardware.read_battery(),
            claims: self.bridge.get_nearby_claims(),
        }
    }

    fn decide(&self, percepts: &Percepts) -> Intent {
        // Run Replicant decision logic
        // Returns Intent::Move, Intent::Avoid, Intent::Stop, etc.
    }

    fn act(&self, intent: &Intent) {
        // Convert Intent to motor commands
        match intent {
            Intent::Move { dx, dy } => self.hardware.move_forward(*dx, *dy),
            Intent::Avoid => self.hardware.turn_away(),
            Intent::Stop => self.hardware.stop(),
            _ => {}
        }
    }
}
```

---

Safety Integration

Hard Stop → λ < 0.15

```rust
// In safety layer
if distance < SAFE_DISTANCE {
    // This is equivalent to λ < 0.15 in Replicant
    self.lambda.value = 0.0;
    self.lambda.last_update_tick = current_tick;
    self.hardware.emergency_stop();
}
```

Bounded Adaptation

```rust
// Learning layer with rollback
fn adapt_traits(&mut self, delta: f32) {
    // Clone current traits as checkpoint
    let checkpoint = self.traits.clone();
    
    // Apply mutation
    self.traits = self.traits.mutate(delta);
    
    // If performance drops (λ decreases), rollback
    if self.lambda.compute(self.tick) < self.prev_lambda {
        self.traits = checkpoint;
    }
}
```

---

Testing

Simulated Colony + ESP32

```bash
# Run simulated colony with ESP32 node
cargo run --example colony_with_esp32

# Test MQTT bridge
cargo test --features mqtt-integration
```

Hardware Validation

```bash
# Flash to ESP32
espflash flash target/riscv32imc-unknown-none-elf/debug/replicant-esp32

# Monitor MQTT messages
mosquitto_sub -t "replicant/+/claims" -v
```

---

Milestones

# Milestone Status
1 Bridge layer design ✅
2 MQTT integration ⏳
3 Hardware abstraction ⏳
4 Safety integration ⏳
5 Full colony demo ⏳
6 Long-duration validation ⏳

---

"The swarm learns. The liar pays. The robots move."
