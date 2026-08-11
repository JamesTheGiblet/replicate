import sys, re, shutil

P = "src/world.py"
shutil.copy(P, P + ".bak")
s = open(P).read()

def ind(m): return m.group(1)

EDITS = [
("archived store", "archived_claims: Dict",
 r'( *)self\.claims: Dict\[str, Claim\] = \{\}\n',
 lambda m: m.group(0) + f"{ind(m)}self.archived_claims: Dict[str, Claim] = {{}}\n"),

("attest guards", 'a["agent_id"] == agent_id for a in claim.attestations',
 r'( *)claim = self\.claims\[claim_id\]\n( *)claim\.attestations\.append\(',
 lambda m: f'{ind(m)}claim = self.claims[claim_id]\n'
           f'{ind(m)}if claim.lens != "OPINION":\n'
           f'{ind(m)}    return\n'
           f'{ind(m)}if any(a["agent_id"] == agent_id for a in claim.attestations):\n'
           f'{ind(m)}    return\n'
           f'{m.group(2)}claim.attestations.append('),

("unfreeze quarantined", None,
 r'if agent\.alive and not agent\.is_rogue:',
 lambda m: "if agent.alive:"),

("pass tick", 'percepts["tick"]',
 r'( *)percepts = agent\.sense\(self\)\n',
 lambda m: m.group(0) + f'{ind(m)}percepts["tick"] = self.tick\n'),

("call decay", "self._decay_claims()",
 r'( *)self\._decay_pheromones\(\)\n( *)self\.tick \+= 1',
 lambda m: f"{ind(m)}self._decay_pheromones()\n"
           f"{ind(m)}self._decay_claims()\n"
           f"{m.group(2)}self.tick += 1"),

("decay method", "def _decay_claims",
 r'( *)def _log_event\(self, event: Dict\) -> None:',
 lambda m: f"{ind(m)}def _decay_claims(self) -> None:\n"
           f'{ind(m)}    retention = self.config.get("claims", {{}}).get("food", {{}}).get("retention_per_tick", 0.90)\n'
           f"{ind(m)}    expired = []\n"
           f"{ind(m)}    for cid, claim in self.claims.items():\n"
           f"{ind(m)}        claim.strength *= retention\n"
           f'{ind(m)}        if claim.strength <= 0.01 and claim.lens == "OPINION":\n'
           f"{ind(m)}            expired.append(cid)\n"
           f"{ind(m)}    for cid in expired:\n"
           f"{ind(m)}        self.archived_claims[cid] = self.claims.pop(cid)\n"
           f"\n" + m.group(0)),
]

failed = False
for name, marker, pat, repl in EDITS:
    if marker and marker in s:
        print(f"  skip (already present): {name}")
        continue
    s, n = re.subn(pat, repl, s, count=1)
    if n != 1:
        print(f"  FAIL: {name}")
        failed = True
    else:
        print(f"  ok: {name}")

if failed:
    print("nothing written")
    sys.exit(1)

open(P, "w").write(s)
print("patched; backup at src/world.py.bak")
