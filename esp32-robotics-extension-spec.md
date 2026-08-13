# ESP32 Robotics Extension Spec

## Purpose
Deploy Replicant-inspired decision logic to a physical ESP32 robot platform with TT motors, sensors, and chassis while preserving safety and debuggability.

## Target Hardware
- Controller: ESP32 development board.
- Drive: dual TT DC motors.
- Motor driver: TB6612FNG or L298N.
- Chassis: 2WD or 4WD compatible frame.
- Power: isolated motor and logic rails with common ground.
- Sensors (minimum): front distance + bumper switch.
- Sensors (recommended): wheel encoders + IMU.

## Electrical Requirements
- Motor rail sized for stall current with headroom.
- Brownout resilience and decoupling near motor driver.
- Hardware emergency stop input.
- Firmware watchdog enabled.

## Software Architecture
1. Real-time control loop
- Frequency: 50-100 Hz.
- Read sensors, estimate state, produce motor commands.
- Highest execution priority.

2. Behavior layer
- Intent set: `Move`, `Turn`, `Stop`, `Avoid`, `Idle`.
- Rule-based decisions first; adaptive tuning second.

3. Safety layer
- Hard stop on obstacle threshold breach.
- Hard stop on bumper trigger.
- Command timeout watchdog.
- PWM clamp and acceleration limiting.

4. Learning layer
- Low-rate adaptation (1-5 Hz equivalent).
- Mutable parameters only:
- `forward_speed_gain`
- `turn_gain`
- `obstacle_margin`
- `exploration_bias`
- Uses checkpoint + rollback from self-awareness spec.

5. Telemetry and tuning
- BLE or Wi-Fi transport.
- Periodic state packet export.
- Remote parameter update endpoint with bounds checks.

## Interfaces
- Inputs:
- Distance (cm)
- Encoder ticks
- IMU heading (optional)
- Bumper state
- Battery voltage

- Outputs:
- Left PWM + direction
- Right PWM + direction
- Telemetry packet

## Performance Targets
- Obstacle reaction latency < 100 ms.
- Straight-line drift < 10% over 2 m after calibration.
- No unsafe motion during transient sensor dropouts.
- Continuous autonomous runtime >= 4 hours in indoor test track.

## Safety Constraints
- Adaptive logic cannot modify emergency-stop thresholds directly.
- Invalid sensor frame defaults to stop.
- Brownout or watchdog event enters controlled halt state.
- Manual override must preempt autonomous commands.

## Integration Milestones
1. Motor and sensor bring-up with manual teleop.
2. Autonomous obstacle avoidance with fixed parameters.
3. Add bounded adaptive tuning.
4. Add telemetry dashboard and rollback tests.
5. Run long-duration reliability validation.

## Test Plan
- Bench tests: PWM mapping, encoder direction, sensor sanity.
- Closed-course tests: obstacle approach and avoidance repeatability.
- Fault injection: stale sensor data, packet loss, low voltage simulation.
- Log review: safety events, rollback frequency, fitness trend.
