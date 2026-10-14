import json, os, glob

with open('.gemini/categorized_meshes.json') as f:
    entries = json.load(f)

# Exclude exact duplicates and overlapping AHA segments for default assembly
duplicates = {'MM543', 'MM544', 'MM569', 'MM571', 'MM574'}
lv_free_segments = {'MM614', 'MM615', 'MM616', 'MM620', 'MM621', 'MM622', 'MM623', 'MM624', 'MM626', 'MM627', 'MM628', 'MM631'}
lv_sept_segments = {'MM613', 'MM618', 'MM619', 'MM625', 'MM629', 'MM630'}
excluded = duplicates.union(lv_free_segments).union(lv_sept_segments)

# Map each entry to fine-tuned groups & descriptive anatomical labels
def refine_entry(e):
    mid = e['id']
    fma = e['fmaid']
    lbl = e['label']
    fn = e['filename']
    
    # 1. Coronary Arteries
    if mid == 'MM557':
        return {'group': 'left_coronary_stem', 'id': mid, 'label': 'Left coronary stem (Left Main / LM trunk)', 'filename': fn}
    if mid in ('MM420', 'MM424', 'MM425'):
        seg = 'proximal' if mid == 'MM420' else 'mid' if mid == 'MM424' else 'distal'
        return {'group': 'lad', 'id': mid, 'label': f'LAD trunk - {seg} segment', 'filename': fn}
    if mid in ('MM422', 'MM423', 'MM432'):
        d_num = '1 (D1)' if mid == 'MM422' else '2 (D2)' if mid == 'MM423' else '3 (D3)'
        return {'group': 'lad_branches', 'id': mid, 'label': f'LAD diagonal branch {d_num}', 'filename': fn}
    if mid in ('MM431', 'MM433', 'MM434'):
        s_num = '1 (S1)' if mid == 'MM431' else '2 (S2)' if mid == 'MM433' else '3 (S3)'
        return {'group': 'lad_branches', 'id': mid, 'label': f'LAD anterior septal branch {s_num}', 'filename': fn}
        
    if mid in ('MM426', 'MM635'):
        seg = 'proximal' if mid == 'MM426' else 'distal'
        return {'group': 'lcx', 'id': mid, 'label': f'LCX circumflex trunk - {seg} segment', 'filename': fn}
    if mid == 'MM610':
        return {'group': 'lcx_branches', 'id': mid, 'label': 'LCX obtuse marginal branch (OM1)', 'filename': fn}
    if mid == 'MM428':
        return {'group': 'lcx_branches', 'id': mid, 'label': 'LCX posterior ventricular branch', 'filename': fn}
    if mid == 'MM430':
        return {'group': 'lcx_branches', 'id': mid, 'label': 'LCX posterior interventricular branch (PDA in left-dominant)', 'filename': fn}
        
    if mid in ('MM556', 'MM436', 'MM439'):
        seg = 'proximal (ostium to acute margin)' if mid == 'MM556' else 'mid segment' if mid == 'MM436' else 'distal segment'
        return {'group': 'rca', 'id': mid, 'label': f'RCA trunk - {seg}', 'filename': fn}
    if mid == 'MM441':
        return {'group': 'rca_branches', 'id': mid, 'label': 'RCA conus branch (infundibular)', 'filename': fn}
    if mid == 'MM438':
        return {'group': 'rca_branches', 'id': mid, 'label': 'RCA sinoatrial (SA) nodal branch', 'filename': fn}
    if mid == 'MM437':
        return {'group': 'rca_branches', 'id': mid, 'label': 'RCA anterior ventricular branch', 'filename': fn}
    if mid == 'MM440':
        return {'group': 'rca_branches', 'id': mid, 'label': 'RCA acute marginal branch', 'filename': fn}
    if mid == 'MM443':
        return {'group': 'rca_branches', 'id': mid, 'label': 'RCA atrioventricular (AV) nodal branch', 'filename': fn}
    if mid == 'MM444':
        return {'group': 'rca_branches', 'id': mid, 'label': 'RCA posterior ventricular branch', 'filename': fn}
    if mid == 'MM445':
        return {'group': 'rca_branches', 'id': mid, 'label': 'RCA anterior atrial branch', 'filename': fn}
        
    # 2. Cardiac Veins
    if mid in ('MM447', 'MM448'):
        seg = 'anterior IV sulcus segment' if mid == 'MM447' else 'coronary sulcus tributary'
        return {'group': 'cardiac_veins', 'id': mid, 'label': f'Great cardiac vein ({seg})', 'filename': fn}
    if mid in ('MM449', 'MM634', 'MM638'):
        seg = 'main trunk' if mid == 'MM449' else 'distal confluence' if mid == 'MM634' else 'proximal atrial junction'
        return {'group': 'cardiac_veins', 'id': mid, 'label': f'Coronary sinus ({seg})', 'filename': fn}
    if mid == 'MM452':
        return {'group': 'cardiac_veins', 'id': mid, 'label': 'Small cardiac vein', 'filename': fn}
    if mid == 'MM446':
        return {'group': 'cardiac_veins', 'id': mid, 'label': 'Anterior cardiac vein', 'filename': fn}
    if mid == 'MM451':
        return {'group': 'cardiac_veins', 'id': mid, 'label': 'Right marginal vein', 'filename': fn}
    if mid == 'MM562':
        return {'group': 'cardiac_veins', 'id': mid, 'label': 'Valve of coronary sinus (Thebesian valve)', 'filename': fn}
        
    # 3. Great Vessels
    if mid == 'MM558':
        return {'group': 'great_vessels', 'id': mid, 'label': 'Wall of bulb of aorta (Aortic root & sinuses of Valsalva)', 'filename': fn}
    if mid == 'MM506':
        return {'group': 'great_vessels', 'id': mid, 'label': 'Ascending aorta proper', 'filename': fn}
    if mid == 'MM607':
        return {'group': 'great_vessels', 'id': mid, 'label': 'Pulmonary trunk proper', 'filename': fn}
        
    # 4. Ventricles & Septa (Walls)
    if mid == 'MM474':
        return {'group': 'ventricles', 'id': mid, 'label': 'Free wall of left ventricle (LV free wall)', 'filename': fn}
    if mid == 'MM598':
        return {'group': 'ventricles', 'id': mid, 'label': 'Wall of inflow part of right ventricle (RV inflow)', 'filename': fn}
    if mid == 'MM538':
        return {'group': 'ventricles', 'id': mid, 'label': 'Wall of outflow part of right ventricle (RV infundibulum)', 'filename': fn}
    if mid == 'MM534':
        return {'group': 'ventricles', 'id': mid, 'label': 'Mural limb of supraventricular crest (Crista supraventricularis)', 'filename': fn}
    if mid == 'MM563':
        return {'group': 'ventricles', 'id': mid, 'label': 'Septal limb of supraventricular crest', 'filename': fn}
    if mid == 'MM600':
        return {'group': 'ventricles', 'id': mid, 'label': 'Muscular part of interventricular septum (IV septum)', 'filename': fn}
    if mid == 'MM568':
        return {'group': 'ventricles', 'id': mid, 'label': 'Membranous part of interventricular septum proper', 'filename': fn}
    if mid == 'MM594':
        return {'group': 'ventricles', 'id': mid, 'label': 'Interventricular septum (muscular junction)', 'filename': fn}
    if mid == 'MM595':
        return {'group': 'ventricles', 'id': mid, 'label': 'Atrioventricular septum', 'filename': fn}
        
    # 5. Internal Myocardium (Papillary muscles & trabeculae)
    if mid in ('MM636', 'MM637'):
        pos = 'Anterior' if mid == 'MM636' else 'Posterior'
        return {'group': 'internal_myocardium', 'id': mid, 'label': f'{pos} papillary muscle of left ventricle', 'filename': fn}
    if mid in ('MM550', 'MM551', 'MM537'):
        pos = 'Anterior' if mid == 'MM550' else 'Posterior' if mid == 'MM551' else 'Septal'
        return {'group': 'internal_myocardium', 'id': mid, 'label': f'{pos} papillary muscle of right ventricle', 'filename': fn}
    if mid == 'MM532':
        return {'group': 'internal_myocardium', 'id': mid, 'label': 'Septomarginal trabecula (Moderator band)', 'filename': fn}
    if mid == 'MM564':
        return {'group': 'internal_myocardium', 'id': mid, 'label': 'Trabeculae carneae of right ventricle', 'filename': fn}
    if mid == 'MM599':
        return {'group': 'internal_myocardium', 'id': mid, 'label': 'Trabeculae carneae of left ventricle', 'filename': fn}
        
    # 6. Atria & Auricles
    if mid in ('MM559', 'MM560', 'MM590', 'MM591'):
        wall = 'Anterior wall proper' if mid == 'MM559' else 'Lateral wall proper' if mid == 'MM560' else 'Septal wall (inferior)' if mid == 'MM590' else 'Septal wall (superior)'
        return {'group': 'atria', 'id': mid, 'label': f'{wall} of right atrium', 'filename': fn}
    if mid == 'MM461':
        return {'group': 'atria', 'id': mid, 'label': 'Wall of right auricle proper (Right atrial appendage)', 'filename': fn}
    if mid == 'MM462':
        return {'group': 'atria', 'id': mid, 'label': 'Crista terminalis', 'filename': fn}
    if mid == 'MM466':
        return {'group': 'atria', 'id': mid, 'label': 'Pectinate muscle of right auricle', 'filename': fn}
    if mid == 'MM463':
        return {'group': 'atria', 'id': mid, 'label': 'Valve of inferior vena cava (Eustachian valve)', 'filename': fn}
    if mid == 'MM467':
        return {'group': 'atria', 'id': mid, 'label': 'Tendon of Todaro', 'filename': fn}
    if mid == 'MM609':
        return {'group': 'atria', 'id': mid, 'label': 'Triangle of sinu-atrial node (Koch triangle landmark)', 'filename': fn}
        
    if mid in ('MM632', 'MM456', 'MM633', 'MM460', 'MM458'):
        wall = 'Anterior wall proper' if mid == 'MM632' else 'Lateral wall' if mid == 'MM456' else 'Posterior wall' if mid == 'MM633' else 'Superior wall' if mid == 'MM460' else 'Septal wall'
        return {'group': 'atria', 'id': mid, 'label': f'{wall} of left atrium', 'filename': fn}
    if mid == 'MM459':
        return {'group': 'atria', 'id': mid, 'label': 'Wall of left auricle (Left atrial appendage)', 'filename': fn}
    if mid in ('MM592', 'MM593'):
        part = 'fossa ovalis region' if mid == 'MM593' else 'proper'
        return {'group': 'atria', 'id': mid, 'label': f'Interatrial septum ({part})', 'filename': fn}
        
    # 7. Valves & Fibrous Skeleton
    if mid in ('MM519', 'MM521', 'MM524'):
        cusp = 'Right posterior' if mid == 'MM519' else 'Left posterior' if mid == 'MM521' else 'Anterior'
        return {'group': 'valves', 'id': mid, 'label': f'Aortic valve - {cusp} cusp', 'filename': fn}
    if mid in ('MM517', 'MM520'):
        part = 'segment 1' if mid == 'MM517' else 'segment 2'
        return {'group': 'valves', 'id': mid, 'label': f'Fibrous ring of aortic valve ({part})', 'filename': fn}
    if mid in ('MM514', 'MM515', 'MM516'):
        scallop = 'Right posterior' if mid == 'MM514' else 'Left posterior' if mid == 'MM515' else 'Anterior'
        return {'group': 'valves', 'id': mid, 'label': f'Aortic annulus - {scallop} fibrous scallop', 'filename': fn}
        
    if mid in ('MM604', 'MM605', 'MM606'):
        cusp = 'Right anterior' if mid == 'MM604' else 'Posterior' if mid == 'MM605' else 'Left anterior'
        return {'group': 'valves', 'id': mid, 'label': f'Pulmonary valve - {cusp} cusp', 'filename': fn}
    if mid in ('MM601', 'MM602', 'MM603'):
        scallop = 'Right anterior' if mid == 'MM601' else 'Posterior' if mid == 'MM602' else 'Left anterior'
        return {'group': 'valves', 'id': mid, 'label': f'Pulmonary annulus - {scallop} fibrous scallop', 'filename': fn}
        
    if mid == 'MM541':
        return {'group': 'valves', 'id': mid, 'label': 'Mitral valve - anterior leaflet', 'filename': fn}
    if mid == 'MM542':
        return {'group': 'valves', 'id': mid, 'label': 'Mitral valve - posterior leaflet', 'filename': fn}
    if mid == 'MM529':
        return {'group': 'valves', 'id': mid, 'label': 'Fibrous ring of mitral valve (Mitral annulus)', 'filename': fn}
        
    if mid == 'MM575':
        return {'group': 'valves', 'id': mid, 'label': 'Tricuspid valve - anterior leaflet', 'filename': fn}
    if mid == 'MM570':
        return {'group': 'valves', 'id': mid, 'label': 'Tricuspid valve - posterior leaflet', 'filename': fn}
    if mid == 'MM573':
        return {'group': 'valves', 'id': mid, 'label': 'Tricuspid valve - septal leaflet', 'filename': fn}
    if mid == 'MM572':
        return {'group': 'valves', 'id': mid, 'label': 'Anulus proper of tricuspid valve', 'filename': fn}
        
    if mid in ('MM526', 'MM596'):
        side = 'Left' if mid == 'MM526' else 'Right'
        return {'group': 'valves', 'id': mid, 'label': f'{side} fibrous trigone of heart', 'filename': fn}
        
    # 8. Conduction System
    if mid == 'MM419':
        return {'group': 'conduction_system', 'id': mid, 'label': 'Sinuatrial (SA) node', 'filename': fn}
    if mid == 'MM587':
        return {'group': 'conduction_system', 'id': mid, 'label': 'Atrioventricular (AV) node', 'filename': fn}
    if mid == 'MM586':
        return {'group': 'conduction_system', 'id': mid, 'label': 'Atrioventricular bundle (Bundle of His)', 'filename': fn}
    if mid == 'MM577':
        return {'group': 'conduction_system', 'id': mid, 'label': 'Right bundle branch of AV bundle', 'filename': fn}
    if mid in ('MM578', 'MM579', 'MM580'):
        div = 'Posterior division' if mid == 'MM578' else 'Septal division' if mid == 'MM579' else 'Anterior division'
        return {'group': 'conduction_system', 'id': mid, 'label': f'Left bundle branch - {div}', 'filename': fn}
    if mid in ('MM585', 'MM584', 'MM583', 'MM582'):
        tract = 'Anterior internodal tract' if mid == 'MM585' else 'Atrial branch (Bachmann bundle)' if mid == 'MM584' else 'Middle internodal tract (Wenckebach)' if mid == 'MM583' else 'Posterior internodal tract (Thorel)'
        return {'group': 'conduction_system', 'id': mid, 'label': tract, 'filename': fn}
        
    return {'group': 'other', 'id': mid, 'label': lbl, 'filename': fn}

final_entries = [refine_entry(e) for e in entries if e['id'] not in excluded]

print(f"Final entries count: {len(final_entries)}")
with open('.gemini/final_heart_entries.json', 'w') as out:
    json.dump(final_entries, out, indent=2)

groups_count = {}
for e in final_entries:
    groups_count[e['group']] = groups_count.get(e['group'], 0) + 1

for g, c in sorted(groups_count.items()):
    print(f"  {g}: {c}")
