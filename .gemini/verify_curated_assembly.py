import os, json

models_dir = r'C:\Users\hario\Downloads\CardioVision_BodyParts3D_ThreeJS_Preview\CardioVision_3D_Preview\models'
files_on_disk = set(os.listdir(models_dir))

def get_exact_name(prefix):
    matches = [f for f in files_on_disk if f.startswith(prefix + '_')]
    if matches:
        return matches[0]
    return None

curated_specs = {
    "ventricles": [
        ("MM474", "Free wall of left ventricle (LV free wall)"),
        ("MM598", "Wall of inflow part of right ventricle (RV inflow)"),
        ("MM538", "Wall of outflow part of right ventricle (RV outflow / infundibulum)"),
        ("MM600", "Muscular part of interventricular septum (IV septum)"),
        ("MM568", "Membranous part of interventricular septum proper"),
        ("MM594", "Interventricular septum (muscular junction)"),
        ("MM595", "Atrioventricular septum")
    ],
    "atria": [
        ("MM559", "Anterior wall proper of right atrium"),
        ("MM560", "Lateral wall proper of right atrium"),
        ("MM590", "Septal wall of right atrium"),
        ("MM461", "Wall of right auricle proper (right atrial appendage)"),
        ("MM632", "Anterior wall proper of left atrium"),
        ("MM456", "Lateral wall of left atrium"),
        ("MM633", "Posterior wall of left atrium"),
        ("MM460", "Superior wall of left atrium"),
        ("MM458", "Septal wall of left atrium"),
        ("MM459", "Wall of left auricle (left atrial appendage)"),
        ("MM592", "Interatrial septum")
    ],
    "great_vessels": [
        ("MM558", "Wall of bulb of aorta (Aortic root / aortic sinuses)"),
        ("MM506", "Ascending aorta proper"),
        ("MM607", "Pulmonary trunk proper")
    ],
    "valves": [
        ("MM519", "Aortic valve - right posterior cusp"),
        ("MM521", "Aortic valve - left posterior cusp"),
        ("MM524", "Aortic valve - anterior cusp"),
        ("MM517", "Fibrous ring of aortic valve"),
        ("MM604", "Pulmonary valve - right anterior cusp"),
        ("MM605", "Pulmonary valve - posterior cusp"),
        ("MM606", "Pulmonary valve - left anterior cusp"),
        ("MM541", "Mitral valve - anterior leaflet"),
        ("MM542", "Mitral valve - posterior leaflet"),
        ("MM529", "Fibrous ring of mitral valve"),
        ("MM575", "Tricuspid valve - anterior leaflet"),
        ("MM570", "Tricuspid valve - posterior leaflet"),
        ("MM573", "Tricuspid valve - septal leaflet"),
        ("MM572", "Anulus proper of tricuspid valve")
    ],
    "left_coronary_stem": [
        ("MM557", "Stem of left coronary artery (Left Main)")
    ],
    "lad": [
        ("MM420", "LAD trunk - proximal segment"),
        ("MM424", "LAD trunk - mid segment"),
        ("MM425", "LAD trunk - distal segment")
    ],
    "lad_branches": [
        ("MM422", "LAD diagonal branch 1 (D1)"),
        ("MM423", "LAD diagonal branch 2 (D2)"),
        ("MM431", "LAD anterior septal branch 1"),
        ("MM432", "LAD diagonal branch 3 (D3)"),
        ("MM433", "LAD anterior septal branch 2"),
        ("MM434", "LAD anterior septal branch 3")
    ],
    "lcx": [
        ("MM426", "LCX trunk - proximal circumflex"),
        ("MM635", "LCX trunk - distal circumflex")
    ],
    "lcx_branches": [
        ("MM428", "LCX first posterior ventricular branch"),
        ("MM430", "LCX posterior interventricular branch"),
        ("MM610", "LCX left marginal artery (OM1)")
    ],
    "rca": [
        ("MM556", "RCA trunk - proximal segment & ostium"),
        ("MM436", "RCA trunk - mid segment in right AV groove"),
        ("MM439", "RCA trunk - distal segment")
    ],
    "rca_branches": [
        ("MM437", "RCA first anterior ventricular branch"),
        ("MM438", "RCA sinoatrial (SA) nodal branch"),
        ("MM440", "RCA marginal branch (acute marginal)"),
        ("MM441", "RCA conus branch"),
        ("MM443", "RCA atrioventricular (AV) node branch"),
        ("MM444", "RCA first posterior ventricular branch"),
        ("MM445", "RCA anterior atrial branch")
    ],
    "cardiac_veins": [
        ("MM447", "Great cardiac vein (in anterior IV sulcus with LAD)"),
        ("MM449", "Coronary sinus (in posterior coronary sulcus)"),
        ("MM452", "Small cardiac vein (in posterior AV groove)"),
        ("MM446", "Anterior cardiac vein"),
        ("MM451", "Right marginal vein")
    ]
}

entries_json = []
all_ok = True
for group, items in curated_specs.items():
    print(f"\nGroup: {group} ({len(items)} items)")
    for prefix, label in items:
        fn = get_exact_name(prefix)
        if not fn:
            print(f"  ERROR: {prefix} not found on disk!")
            all_ok = False
        else:
            entries_json.append({
                "group": group,
                "id": prefix,
                "label": label,
                "filename": fn
            })
            print(f"  OK: {prefix:6s} -> {fn[:40]}...")

print(f"\nTotal verified items: {len(entries_json)}")
print(f"All files verified: {all_ok}")

with open(r'c:\Users\hario\Downloads\CardioVision-AI\.gemini\curated_entries.json', 'w', encoding='utf-8') as f:
    json.dump(entries_json, f, indent=2)
print("Saved curated_entries.json")
