#!/usr/bin/env python3
import json
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

# Import forge modules
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from leighton_weight import LeightonWeight
    from datacube import DataCube
except ImportError:
    class LeightonWeight:
        def update(self, entity, delta): return {"status": "ok"}
    class DataCube:
        def insert(self, fact): return {"status": "ok"}

leighton = LeightonWeight()
datacube = DataCube()

# --- Adherence Database ---
def init_adherence_db():
    conn = sqlite3.connect("forge_data.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS medication_adherence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medication TEXT,
        last_taken TEXT,
        schedule TEXT,
        missed_count INTEGER DEFAULT 0
    )''')
    conn.commit()
    return conn

def get_medication_status(med, conn):
    c = conn.cursor()
    c.execute("SELECT last_taken, missed_count FROM medication_adherence WHERE medication = ?", (med,))
    row = c.fetchone()
    if row:
        return {"taken": row[0] is not None, "last_taken": row[0], "missed_count": row[1]}
    return {"taken": False, "last_taken": None, "missed_count": 0}

def mark_taken(med, conn):
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("INSERT OR REPLACE INTO medication_adherence (medication, last_taken, missed_count) VALUES (?, ?, 0)",
              (med, now))
    conn.commit()

def mark_missed(med, conn):
    c = conn.cursor()
    c.execute("UPDATE medication_adherence SET missed_count = missed_count + 1 WHERE medication = ?", (med,))
    if c.rowcount == 0:
        c.execute("INSERT INTO medication_adherence (medication, missed_count) VALUES (?, 1)", (med,))
    conn.commit()

# --- Primitives ---
def prim_health_medication_check(input_data, context):
    conn = init_adherence_db()
    medications = input_data.get('medications', [])
    schedule = input_data.get('schedule', 'unknown')
    results = []
    for med in medications:
        status = get_medication_status(med, conn)
        results.append(f"{med}: last taken {status['last_taken'] or 'never'}, missed {status['missed_count']} times")
    conn.close()
    print("\n".join(results))
    return {"status": "ok", "output": results}

def prim_health_medication_remind(input_data, context):
    conn = init_adherence_db()
    medications = context.get('medications', [])
    if_missed = input_data.get('if_missed', True)
    escalate_after = input_data.get('escalate_after', 60)
    
    reminders = []
    for med in medications:
        status = get_medication_status(med, conn)
        if if_missed and status['missed_count'] > 0:
            msg = f"🔔 REMINDER: {med} missed {status['missed_count']} times! Last taken: {status['last_taken'] or 'never'}"
            print(msg)
            reminders.append(msg)
        elif not status['taken']:
            msg = f"🔔 REMINDER: Time to take {med}"
            print(msg)
            reminders.append(msg)
    conn.close()
    return {"status": "ok", "output": reminders}

def prim_leighton_update(input_data, context):
    capsule = input_data.get('capsule', 'unknown')
    rule = input_data.get('rule', 'adherence_based')
    delta_taken = input_data.get('delta_taken', 0.03)
    delta_missed = input_data.get('delta_missed', -0.15)
    
    # Check adherence from context
    conn = init_adherence_db()
    medications = context.get('medications', [])
    total_missed = 0
    for med in medications:
        status = get_medication_status(med, conn)
        total_missed += status['missed_count']
    conn.close()
    
    delta = delta_taken if total_missed == 0 else delta_missed * total_missed
    result = leighton.update(capsule, delta)
    print(f"⚖️ Updated trust for {capsule}: delta {delta}")
    return {"status": "ok", "output": result}

def prim_datacube_insert(input_data, context):
    payload = input_data.get('payload', {})
    # Resolve dynamic variables
    now = datetime.now().isoformat()
    # Use first medication from context as example
    meds = context.get('medications', ['unknown'])
    resolved = {
        "type": payload.get('type', 'medication.log'),
        "medication": meds[0] if '$name' in str(payload) else payload.get('medication', 'unknown'),
        "taken": "pending",
        "ts": now
    }
    result = datacube.insert(resolved)
    print(f"📦 Inserted fact: {resolved}")
    return {"status": "ok", "output": "inserted"}

def prim_sys_log(input_data, context):
    msg = input_data.get('message', '')
    print(f"[LOG] {msg}")
    return {"status": "ok", "output": "logged"}

PRIMITIVES = {
    "health.medication.check": prim_health_medication_check,
    "health.medication.remind": prim_health_medication_remind,
    "leighton.update": prim_leighton_update,
    "datacube.insert": prim_datacube_insert,
    "sys.log": prim_sys_log,
}

def execute_action(action, context):
    prim_name = action.get('primitive')
    input_data = action.get('input', {})
    if not prim_name or prim_name not in PRIMITIVES:
        print(f"  -> Unknown primitive: {prim_name}")
        return False
    result = PRIMITIVES[prim_name](input_data, context)
    print(f"  -> {prim_name}: {result.get('output', 'done')}")
    return result.get('status') == 'ok'

def run_scp(scp_path):
    print(f"\n📄 Loading SCP: {scp_path}")
    with open(scp_path) as f:
        scp = json.load(f)
    
    # Build context from first action's input
    context = {}
    if 'actions' in scp and len(scp['actions']) > 0:
        first_input = scp['actions'][0].get('input', {})
        context['medications'] = first_input.get('medications', [])
    
    print(f"🔧 Executing {len(scp.get('actions', []))} actions...")
    for i, action in enumerate(scp.get('actions', [])):
        print(f"  Action {i+1}: {action.get('primitive', '?')}")
        execute_action(action, context)
    print("✅ Done.\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scp_runner.py <capsule.json>")
        sys.exit(1)
    run_scp(sys.argv[1])
