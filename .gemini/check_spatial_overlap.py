import glob, os, numpy as np

def load_mesh(mid):
    match = glob.glob(f'assets/bodyparts3d/{mid}_*.obj')
    if not match: return None
    path = match[0]
    verts = []
    faces = []
    with open(path, 'r') as f:
        for line in f:
            if line.startswith('v '):
                parts = line.split()
                verts.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif line.startswith('f '):
                parts = line.split()[1:]
                faces.append([int(p.split('/')[0]) - 1 for p in parts])
    return {'id': mid, 'name': os.path.basename(path), 'v': np.array(verts), 'f': np.array(faces)}

pairs_to_check = [
    ('MM594', 'MM600', 'IV Septum'),
    ('MM590', 'MM591', 'RA Septal Wall'),
    ('MM592', 'MM593', 'Interatrial Septum'),
    ('MM541', 'MM543', 'Mitral Anterior Leaflet'),
    ('MM542', 'MM544', 'Mitral Posterior Leaflet'),
    ('MM569', 'MM575', 'Tricuspid Anterior Leaflet'),
    ('MM570', 'MM571', 'Tricuspid Posterior Leaflet'),
    ('MM573', 'MM574', 'Tricuspid Septal Leaflet'),
    ('MM517', 'MM520', 'Aortic Fibrous Ring'),
    ('MM447', 'MM448', 'Great Cardiac Vein'),
    ('MM449', 'MM634', 'Coronary Sinus 1&2'),
    ('MM449', 'MM638', 'Coronary Sinus 1&3'),
    ('MM634', 'MM638', 'Coronary Sinus 2&3')
]

print("=== CHECKING PAIRS FOR DUPLICATION / OVERLAP ===")
for id1, id2, desc in pairs_to_check:
    m1 = load_mesh(id1)
    m2 = load_mesh(id2)
    if not m1 or not m2: continue
    
    # Check vertex counts
    v1_cnt = len(m1['v'])
    v2_cnt = len(m2['v'])
    f1_cnt = len(m1['f'])
    f2_cnt = len(m2['f'])
    
    # Check bounding box
    bb1 = (m1['v'].min(axis=0), m1['v'].max(axis=0))
    bb2 = (m2['v'].min(axis=0), m2['v'].max(axis=0))
    bb_dist = np.linalg.norm(bb1[0] - bb2[0]) + np.linalg.norm(bb1[1] - bb2[1])
    
    # Check if identical coordinates
    exact_match = (v1_cnt == v2_cnt and np.allclose(m1['v'], m2['v']))
    
    print(f"\n{desc}: {id1} vs {id2}")
    print(f"  {id1}: {v1_cnt} verts, {f1_cnt} faces, bbox: [{bb1[0].round(1)} to {bb1[1].round(1)}]")
    print(f"  {id2}: {v2_cnt} verts, {f2_cnt} faces, bbox: [{bb2[0].round(1)} to {bb2[1].round(1)}]")
    print(f"  Exact coordinates match: {exact_match}, BBox delta sum: {bb_dist:.2f}")

    if not exact_match:
        from scipy.spatial import KDTree
        t1 = KDTree(m1['v'])
        d12, _ = t1.query(m2['v'])
        t2 = KDTree(m2['v'])
        d21, _ = t2.query(m1['v'])
        print(f"  Hausdorff-like dist: m2->m1 max={d12.max():.2f}, mean={d12.mean():.2f} | m1->m2 max={d21.max():.2f}, mean={d21.mean():.2f}")
