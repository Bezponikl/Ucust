import json

with open("ai/Photo_generations.json", "r", encoding="utf-8") as f:
    d1 = json.load(f)
with open("ai/realism2.0.json", "r", encoding="utf-8") as f:
    d2 = json.load(f)

types1 = [f"ID {n.get('id')}: {n.get('type')} ({n.get('title', '')})" for n in d1.get("nodes", [])]
types2 = [f"ID {n.get('id')}: {n.get('type')} ({n.get('title', '')})" for n in d2.get("nodes", [])]

print("=== NODES IN Photo_generations.json (16 nodes) ===")
for t in types1:
    print(" ", t)

print("\n=== NODES IN realism2.0.json (26 nodes) ===")
for t in types2:
    print(" ", t)
