# Agent 74 - Source Code Reference

## File Locations
- Main agent: `/storage/emulated/0/Download/replicate/python/src/agent_voice_fixed.py`
- Phone sensor: `/storage/emulated/0/Download/replicate/python/src/phone/agent.py`
- Database: `/storage/emulated/0/Download/replicate/python/src/phone_db.py`
- Bridge: `/storage/emulated/0/Download/replicate/python/src/bridge_ledger.py`

## Key Functions

### VoiceAgent
- `__init__()`: Initializes Agent 74 with name, model, and personality
- `sense()`: Reads phone sensors (GPS, IMU, light, pressure, steps)
- `query_llm()`: Sends prompts to local Ollama model
- `speak()`: Converts text to speech via Termux TTS
- `talk_about_self()`: Describes current sensor state
- `talk_about_colony()`: Explains the Replicant swarm
- `answer_question()`: Responds to user questions
- `interactive_mode()`: Main chat loop

### PhoneBridge
- `run_with_voice()`: Runs simulation and speaks about events

## Data Flow
1. Sensors → PhoneAgent.sense() → Percepts
2. Percepts → SQLite (phone_data.db)
3. Percepts → Replicant World → Claims/COUNTER
4. Events → VoiceAgent.speak() → TTS

## Configuration
- Model: gemma2:2b (fast, runs on phone)
- Database: phone_data.db
- Session format: YYYYMMDD_HHMMSS
- TTS chunk size: 80 characters
