import glob, os, numpy as np
from scipy.spatial import KDTree

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
    return {'id': mid, 'v': np.array(verts), 'f': np.array(faces)}

m474 = load_mesh('MM474')
lv_free_ids = ['MM614', 'MM615', 'MM616', 'MM620', 'MM621', 'MM622', 'MM623', 'MM624', 'MM626', 'MM627', 'MM628', 'MM631']
lv_sept_ids = ['MM613', 'MM618', 'MM619', 'MM625', 'MM629', 'MM630']

free_meshes = [load_mesh(i) for i in lv_free_ids]
sept_meshes = [load_mesh(i) for i in lv_sept_ids]

all_free_v = np.vstack([m['v'] for m in free_meshes])
all_sept_v = np.vstack([m['v'] for m in sept_meshes])
all_lv_v = np.vstack([all_free_v, all_sept_v])

print("=== MM474 VS LV FREE WALL SEGMENTS ===")
print("MM474:", len(m474['v']), "verts, bbox:", m474['v'].min(axis=0).round(1), "to", m474['v'].max(axis=0).round(1))
print("Combined Free Segments (12):", len(all_free_v), "verts, bbox:", all_free_v.min(axis=0).round(1), "to", all_free_v.max(axis=0).round(1))
print("Combined Septal Segments (6):", len(all_sept_v), "verts, bbox:", all_sept_v.min(axis=0).round(1), "to", all_sept_v.max(axis=0).round(1))

tree_474 = KDTree(m474['v'])
dists_free_to_474, _ = tree_474.query(all_free_v)
print(f"Free segments to MM474: mean={dists_free_to_474.mean():.2f}, median={np.median(dists_free_to_474):.2f}, max={dists_free_to_474.max():.2f}")
print(f"Percentage of Free segment vertices within 1mm of MM474: {(dists_free_to_474 < 1.0).mean()*100:.1f}%")
print(f"Percentage of Free segment vertices within 3mm of MM474: {(dists_free_to_474 < 3.0).mean()*100:.1f}%")

# Vice versa: MM474 to Free segments
tree_free = KDTree(all_free_v)
dists_474_to_free, _ = tree_free.query(m474['v'])
print(f"MM474 to Free segments: mean={dists_474_to_free.mean():.2f}, median={np.median(dists_474_to_free):.2f}, max={dists_474_to_free.max():.2f}")
print(f"Percentage of MM474 vertices within 1mm of Free segments: {(dists_474_to_free < 1.0).mean()*100:.1f}%")

# Check if segments have internal dividing faces!
print("\n=== ARE SEGMENTS SOLID VOLUMES WITH INTERNAL WALLS? ===")
for m in free_meshes[:4]:
    # Check edges
    edges = {}
    for f in m['f']:
        for i in range(3):
            e = tuple(sorted((f[i], f[(i+1)%3])))
            edges[e] = edges.get(e, 0) + 1
    boundary = sum(1 for c in edges.values() if c == 1)
    print(f"{m['id']}: verts={len(m['v'])}, faces={len(m['f'])}, open boundary edges={boundary} (is closed? {boundary == 0})")
