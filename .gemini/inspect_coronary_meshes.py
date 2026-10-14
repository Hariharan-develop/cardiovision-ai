import json

with open('.gemini/final_heart_entries.json') as f:
    entries = json.load(f)

print('Total entries:', len(entries))
groups = {}
for e in entries:
    g = e.get('group', 'unknown')
    groups.setdefault(g, []).append(e)

for g, items in sorted(groups.items()):
    print(f"\n=== GROUP: {g} ({len(items)} meshes) ===")
    for it in items:
        print(f"  [{it['id']}] {it['filename']} -> {it['label']}")
