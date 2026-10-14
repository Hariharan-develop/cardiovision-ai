import glob, os, numpy as np
from scipy.spatial import KDTree

files = sorted(glob.glob('assets/bodyparts3d/*.obj'))
meshes = []
for f in files:
    v = []
    fc = 0
    with open(f) as fp:
        for l in fp:
            if l.startswith('v '):
                p = l.split()
                v.append([float(p[1]), float(p[2]), float(p[3])])
            elif l.startswith('f '):
                fc += 1
    meshes.append({
        'id': os.path.basename(f).split('_')[0],
        'name': os.path.basename(f),
        'v': np.array(v),
        'fc': fc,
        'bmin': np.min(v, axis=0),
        'bmax': np.max(v, axis=0)
    })

print("=== CHECKING NEAR-IDENTICAL / CO-LOCATED MESHES (Hausdorff mean < 0.1 mm) ===")
co_located = []
for i in range(len(meshes)):
    for j in range(i+1, len(meshes)):
        m1 = meshes[i]
        m2 = meshes[j]
        # check bbox distance
        d_min = np.linalg.norm(m1['bmin'] - m2['bmin'])
        d_max = np.linalg.norm(m1['bmax'] - m2['bmax'])
        if d_min < 1.0 and d_max < 1.0:
            t1 = KDTree(m1['v'])
            d21, _ = t1.query(m2['v'])
            if d21.mean() < 0.2:
                print(f"CO-LOCATED PAIR: {m1['id']} ({len(m1['v'])}v) vs {m2['id']} ({len(m2['v'])}v): mean dist = {d21.mean():.4f} mm, max = {d21.max():.4f} mm")
                print(f"   {m1['name']}")
                print(f"   {m2['name']}")
                co_located.append((m1['id'], m2['id']))

print(f"Total co-located pairs: {len(co_located)}")
