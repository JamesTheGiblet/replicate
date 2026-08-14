
Analytics & Monitoring

Privacy-First Design

Explorer-d334 uses 100% opt-in telemetry:

· ✅ No data collected without permission
· ✅ Anonymous only (cannot be traced back)
· ✅ Local storage only
· ✅ You control sharing

Commands

```bash
# Opt in to telemetry (anonymous usage data)
./forge telemetry-on

# Opt out (no data collected)
./forge telemetry-off

# Check status
./forge telemetry-status

# View local crashes
./forge crashes

# Clear crash reports
./forge crashes-clear
```

What's Collected (if opted in)

· Anonymous command usage (which commands are used)
· Session duration
· Error types (not the actual errors)
· Anonymous device ID (one-way hash, cannot reverse)

What's NEVER Collected

· ❌ Your code
· ❌ Your conversations
· ❌ Your files
· ❌ Personal information
· ❌ IP addresses
· ❌ Any identifiable data

Data Storage

All data stays on YOUR device in:

· analytics/telemetry.db
· analytics/crashes/

You can delete these anytime.

Sharing

Crashes are never shared automatically. You must explicitly opt in to telemetry, and even then, only anonymous usage data is collected.

Export Data

```bash
# Export anonymized data
python analytics/telemetry.py
```

---

🔥 Your privacy is our priority. Always opt-in, never required. 🔥
