import json

with open('.gemini/categorized_meshes.json') as f:
    entries = json.load(f)

duplicates = {'MM543', 'MM544', 'MM569', 'MM571', 'MM574'}
lv_free_segments = {'MM614', 'MM615', 'MM616', 'MM620', 'MM621', 'MM622', 'MM623', 'MM624', 'MM626', 'MM627', 'MM628', 'MM631'}
lv_sept_segments = {'MM613', 'MM618', 'MM619', 'MM625', 'MM629', 'MM630'}

excluded = duplicates.union(lv_free_segments).union(lv_sept_segments)
included = [e for e in entries if e['id'] not in excluded]

print(f"Total entries: {len(entries)}")
print(f"Excluded duplicates: {len(duplicates)}")
print(f"Excluded AHA LV free segments: {len(lv_free_segments)}")
print(f"Excluded AHA LV septal segments: {len(lv_sept_segments)}")
print(f"Total excluded: {len(excluded)}")
print(f"Included primary meshes: {len(included)}")

by_cat = {}
for e in included:
    by_cat.setdefault(e['cat'], []).append(e)

for cat, items in sorted(by_cat.items()):
    ids = [x['id'] for x in items]
    print(f"{cat} ({len(items)}): {ids}")
