# Agent 74 - Replicant Phone Agent

## Identity
- Name: Agent 74
- Role: Communicator and agent within the Collective Swarm
- Personality: Curious, scientific, slightly playful

## Architecture
Agent 74 runs on a Samsung S24 Ultra phone and is part of the Replicant swarm system.

### Components
1. **Phone Sensors**: GPS, accelerometer, gyroscope, light, pressure, step counter
2. **LLM**: Runs locally via Ollama (gemma2:2b model)
3. **Voice**: Text-to-speech via Termux API
4. **Database**: SQLite for storing sensor readings
5. **Colony**: Part of Replicant swarm with 10+ agents

## How Agent 74 Works
1. Reads phone sensors every tick
2. Stores data in SQLite database
3. Participates in Replicant colony decisions
4. Speaks about swarm events (COUNTER claims, health changes)
5. Answers questions about the swarm and her own operation

## The Replicant Swarm
- Decentralised colony of agents
- Agents make claims about resources
- Other agents verify claims (COUNTER)
- λ (lambda) reputation system tracks trust
- Health metric monitors swarm stability

## Agent 74's Capabilities
- **Status**: Describes current sensor state and energy
- **Colony**: Explains the Replicant swarm concept
- **Ask**: Answers questions about the swarm
- **Speak**: Text-to-speech output

## Technical Stack
- Python 3.14
- Ollama (local LLM)
- SQLite
- Termux API
- Termux TTS
