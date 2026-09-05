import json
import os
import hashlib

p1 = r"ai/Photo_generations.json"
p2 = r"ai/realism2.0.json"

print(f"Photo_generations.json: {os.path.getsize(p1)} bytes")
print(f"realism2.0.json:        {os.path.getsize(p2)} bytes")

h1 = hashlib.sha256(open(p1, "rb").read()).hexdigest()
h2 = hashlib.sha256(open(p2, "rb").read()).hexdigest()
print(f"SHA256 Match: {h1 == h2}")

with open(p1, "r", encoding="utf-8") as f:
    d1 = json.load(f)
with open(p2, "r", encoding="utf-8") as f:
    d2 = json.load(f)

nodes1 = len(d1.get("nodes", []))
nodes2 = len(d2.get("nodes", []))
print(f"Nodes in Photo_generations.json: {nodes1}")
print(f"Nodes in realism2.0.json:        {nodes2}")

# Check differences in nodes
diff_nodes = []
if nodes1 == nodes2:
    for n1, n2 in zip(d1["nodes"], d2["nodes"]):
        if n1 != n2:
            diff_nodes.append((n1.get("id"), n1.get("type")))
print(f"Different nodes count: {len(diff_nodes)}")
if diff_nodes:
    print("Different node IDs and types:", diff_nodes[:10])
