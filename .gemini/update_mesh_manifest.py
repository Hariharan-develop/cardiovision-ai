import json, csv

with open(r'c:\Users\hario\Downloads\CardioVision-AI\.gemini\curated_entries.json', 'r', encoding='utf-8') as f:
    entries = json.load(f)

csv_path = r'C:\Users\hario\Downloads\CardioVision_BodyParts3D_ThreeJS_Preview\CardioVision_3D_Preview\mesh_manifest.csv'
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['group', 'id', 'filename', 'label'])
    for e in entries:
        w.writerow([e['group'], e['id'], e['filename'], e['label']])

print(f"Updated {csv_path} with {len(entries)} rows.")
