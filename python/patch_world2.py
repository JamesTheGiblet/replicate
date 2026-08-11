import sys, re, shutil

P = "src/world.py"
shutil.copy(P, P + ".bak2")
s = open(P).read()

EDITS = [
("split counter reward", "share=1.0 / max(1, len(counters))",
 r'self\.leighton\.counter_reward\(a\["agent_id"\], tick\)',
 lambda m: 'self.leighton.counter_reward(a["agent_id"], tick, '
           'share=1.0 / max(1, len(counters)))'),

("penalise wrong counters", "# obstruction penalty",
 r'( *)self\.leighton\.claim_verified\(claim\.agent_id, tick\)\n',
 lambda m: m.group(0) +
           f"\n{m.group(1)}# obstruction penalty: countered a claim that proved true\n"
           f"{m.group(1)}for a in claim.attestations:\n"
           f'{m.group(1)}    if a["outcome"] == "countered":\n'
           f'{m.group(1)}        self.leighton.credulity_penalty(a["agent_id"], tick)\n'),

("periodic sweep", "self.leighton.sweep(",
 r'( *)self\._decay_claims\(\)\n',
 lambda m: m.group(0) + f"{m.group(1)}self.leighton.sweep(self.tick)\n"),
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
print("patched; backup at src/world.py.bak2")
