import glob, os, numpy as np

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
        'bbox': (np.min(v, axis=0), np.max(v, axis=0))
    })

print("=== SCANNING ALL 129 MESHES FOR DUPLICATES / IDENTICAL GEOMETRIES ===")
duplicates = []
for i in range(len(meshes)):
    for j in range(i+1, len(meshes)):
        m1 = meshes[i]
        m2 = meshes[j]
        if len(m1['v']) == len(m2['v']) and m1['fc'] == m2['fc']:
            if np.allclose(m1['bbox'][0], m2['bbox'][0], atol=1e-2) and np.allclose(m1['bbox'][1], m2['bbox'][1], atol=1e-2):
                diff = np.max(np.abs(m1['v'] - m2['v']))
                if diff < 0.1:
                    print(f"DUPLICATE FOUND: {m1['id']} vs {m2['id']} (max vert diff = {diff:.4f} mm)")
                    print(f"   {m1['name']}")
                    print(f"   {m2['name']}")
                    duplicates.append((m1['id'], m2['id']))

print(f"Total duplicate pairs found: {len(duplicates)}")
