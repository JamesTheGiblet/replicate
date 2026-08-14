
Examples

Health Automation

```bash
# Run health reminder
./binaries/health_wellness_reminder

# Check medication adherence
python src/scp_runner.py capsules/weekday/health.medication.adherence.scp.json
```

Code Generation

```bash
# Generate and run a square function
./forge generate "function that returns square of a number" > square.c
gcc square.c -o square
./square 5  # Output: 25
```

Sensor Projects

```bash
# Build a step counter
./forge generate "function that estimates steps from accelerometer data"

# Build a compass
./forge generate "function that returns direction from magnetometer"
```

Custom Capsules

Create my_capsule.scp.json:

```json
{
  "name": "my_automation",
  "type": "function",
  "params": [{"name": "n", "type": "int"}],
  "logic": "printf(\"Hello from my capsule!\\n\"); return 0;"
}
```

Then run:

```bash
python src/working_replicator.py my_capsule.scp.json generated/my.c
gcc generated/my.c -o binaries/my
./binaries/my
```

Automation Scripts

Daily Briefing

```bash
# Add to crontab (run every morning)
0 8 * * * cd ~/forge && ./binaries/daily_briefing
```

Health Monitoring

```bash
# Check health every hour
0 * * * * cd ~/forge && ./forge health
```

Backup

```bash
# Daily backup
0 0 * * * cd ~/forge && ./forge backup
```

---

🔥 Build anything. Automate everything. 🔥
