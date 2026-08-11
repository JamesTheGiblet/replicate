import sys, shutil

P = "src/world.py"
shutil.copy(P, P + ".bak")
s = open(P).read()

EDITS = [
# 1. archived claims store
("        self.claims: Dict[str, Claim] = {}\n",
 "        self.claims: Dict[str, Claim] = {}\n"
 "        self.archived_claims: Dict[str, Claim] = {}\n"),

# 2a. hide dead claims from perception
("            if ((claim.x - x)**2 + (claim.y - y)**2)**0.5 < radius:\n",
 "            if claim.strength <= 0.01:\n"
 "                continue\n"
 "            if ((claim.x - x)**2 + (claim.y - y)**2)**0.5 < radius:\n"),

# 2b. expose strength
('                    "attestations": len(claim.attestations),\n',
 '                    "strength": claim.strength,\n'
 '                    "attestations": len(claim.attestations),\n'),

# 2c. strongest first, not insertion order
('                    "agent_id": claim.agent_id\n                })\n        return result\n',
 '                    "agent_id": claim.agent_id\n                })\n'
 '        result.sort(key=lambda c: (-c["strength"], c["id"]))\n'
 '        return result\n'),

# 3. idempotency + closed-once
('        claim = self.claims[claim_id]\n        claim.attestations.append(',
 '        claim = self.claims[claim_id]\n'
 '        if claim.lens != "OPINION":\n'
 '            return\n'
 '        if any(a["agent_id"] == agent_id for a in claim.attestations):\n'
 '            return\n'
 '        claim.attestations.append('),

# 4. quarantine must not freeze the agent
("            if agent.alive and not agent.is_rogue:\n",
 "            if agent.alive:\n"),

# 5. give agents the tick
("                percepts = agent.sense(self)\n",
 "                percepts = agent.sense(self)\n"
 "                percepts[\"tick\"] = self.tick\n"),

# 6. call claim decay
("        self._decay_pheromones()\n        self.tick += 1\n",
 "        self._decay_pheromones()\n        self._decay_claims()\n        self.tick += 1\n"),

# 7. the method itself
("    def _log_event(self, event: Dict) -> None:\n",
 "    def _decay_claims(self) -> None:\n"
 "        retention = self.config.get(\"claims\", {}).get(\"food\", {}).get(\"retention_per_tick\", 0.90)\n"
 "        expired = []\n"
 "        for cid, claim in self.claims.items():\n"
 "            claim.strength *= retention\n"
 "            if claim.strength <= 0.01 and claim.lens == \"OPINION\":\n"
 "                expired.append(cid)\n"
 "        for cid in expired:\n"
 "            self.archived_claims[cid] = self.claims.pop(cid)\n"
 "\n"
 "    def _log_event(self, event: Dict) -> None:\n"),
]

for i, (old, new) in enumerate(EDITS, 1):
    n = s.count(old)
    if n != 1:
        print(f"FAIL edit {i}: matched {n} times, expected 1")
        sys.exit(1)
    s = s.replace(old, new, 1)

open(P, "w").write(s)
print("all 9 edits applied; backup at src/world.py.bak")
