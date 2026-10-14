import glob, os, json

files = sorted(glob.glob('assets/bodyparts3d/*.obj'))
entries = []
for f in files:
    name = os.path.basename(f)
    parts = name.split('_')
    mid = parts[0]
    bpid = parts[1]
    fmaid = parts[2]
    desc = '_'.join(parts[3:])[:-4]
    entries.append({'id': mid, 'bpid': bpid, 'fmaid': fmaid, 'label': desc, 'filename': name})

def categorize(e):
    lbl = e['label'].lower()
    
    # Arteries
    if 'interventricular branch of left coronary' in lbl or 'anterior descending branch' in lbl or 'anterior interventricular artery' in lbl:
        if 'trunk' in lbl:
            return 'lad', 'LAD Trunk'
        else:
            return 'lad_branches', 'LAD Branch'
    if 'circumflex' in lbl or 'marginal artery' in lbl:
        if 'trunk' in lbl and 'posterior interventricular' not in lbl:
            return 'lcx', 'LCX Trunk'
        else:
            return 'lcx_branches', 'LCX Branch'
    if 'right coronary artery' in lbl:
        if 'trunk' in lbl:
            return 'rca', 'RCA Trunk'
        else:
            return 'rca_branches', 'RCA Branch'
    if 'stem of left coronary' in lbl:
        return 'left_coronary_stem', 'Left Coronary Stem (LM)'
        
    # Veins
    if 'cardiac vein' in lbl or 'coronary sinus' in lbl:
        return 'cardiac_veins', 'Cardiac Vein / Sinus'
        
    # Great vessels
    if 'aorta' in lbl and 'valve' not in lbl and 'scallop' not in lbl and 'fibrous' not in lbl:
        return 'great_vessels', 'Aorta'
    if 'pulmonary trunk' in lbl:
        return 'great_vessels', 'Pulmonary Trunk'
        
    # Valves & rings
    if 'valve' in lbl or 'cusp' in lbl or 'leaflet' in lbl or 'fibrous ring' in lbl or 'scallop' in lbl or 'anulus' in lbl:
        return 'valves', 'Valve / Fibrous Ring'
        
    # Conduction system
    if 'bundle' in lbl or 'tract' in lbl or 'sinuatrial' in lbl or 'sinu-atrial' in lbl or ('node' in lbl and 'atrioventricular' in lbl):
        return 'conduction_system', 'Conduction System'
        
    # Atria
    if 'atrium' in lbl or 'auricle' in lbl or 'interatrial' in lbl or 'crista terminalis' in lbl or 'todaro' in lbl:
        return 'atria', 'Atrium / Auricle'
        
    # Ventricles & Septa
    if 'ventricle' in lbl or 'septum' in lbl or 'crest' in lbl or 'trabecula' in lbl or 'trigone' in lbl:
        return 'ventricles', 'Ventricle / Myocardium'
        
    return 'other', 'Other'

categorized = {}
for e in entries:
    cat, subcat = categorize(e)
    e['cat'] = cat
    e['subcat'] = subcat
    categorized.setdefault(cat, []).append(e)

for cat, items in sorted(categorized.items()):
    print(f"=== {cat.upper()} ({len(items)}) ===")
    for it in items:
        print(f"  {it['id']} | {it['fmaid']} | {it['label']}")

with open('.gemini/categorized_meshes.json', 'w') as out:
    json.dump(entries, out, indent=2)
