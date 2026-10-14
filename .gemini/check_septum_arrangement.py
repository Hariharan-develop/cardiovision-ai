import glob, os, numpy as np
from scipy.spatial import KDTree

def load_mesh(mid):
    match = glob.glob(f'assets/bodyparts3d/{mid}_*.obj')
    if not match: return None
    path = match[0]
    verts = []
    with open(path, 'r') as f:
        for line in f:
            if line.startswith('v '):
                parts = line.split()
                verts.append([float(parts[1]), float(parts[2]), float(parts[3])])
    return {'id': mid, 'name': os.path.basename(path), 'v': np.array(verts)}

m600 = load_mesh('MM600') # Muscular IV septum
m474 = load_mesh('MM474') # LV Free wall
m598 = load_mesh('MM598') # RV inflow
m538 = load_mesh('MM538') # RV outflow
m568 = load_mesh('MM568') # Membranous IV septum
m594 = load_mesh('MM594') # IV septum muscular junction
m595 = load_mesh('MM595') # AV septum

lv_sept_ids = ['MM613', 'MM618', 'MM619', 'MM625', 'MM629', 'MM630']
sept_meshes = [load_mesh(i) for i in lv_sept_ids]
all_sept_v = np.vstack([m['v'] for m in sept_meshes])

print("Checking spatial arrangement:")
print(f"MM600 center: {m600['v'].mean(axis=0).round(1)}, range X:[{m600['v'][:,0].min():.1f}, {m600['v'][:,0].max():.1f}]")
print(f"LV septal center: {all_sept_v.mean(axis=0).round(1)}, range X:[{all_sept_v[:,0].min():.1f}, {all_sept_v[:,0].max():.1f}]")
print(f"LV free center: {m474['v'].mean(axis=0).round(1)}, range X:[{m474['v'][:,0].min():.1f}, {m474['v'][:,0].max():.1f}]")
print(f"RV inflow center: {m598['v'].mean(axis=0).round(1)}, range X:[{m598['v'][:,0].min():.1f}, {m598['v'][:,0].max():.1f}]")

# Check distance between MM600 and LV free wall vs LV septal and LV free wall
t_474 = KDTree(m474['v'])
d_600_474, _ = t_474.query(m600['v'])
d_sept_474, _ = t_474.query(all_sept_v)
print(f"MM600 to MM474 min dist: {d_600_474.min():.2f}")
print(f"LV septal to MM474 min dist: {d_sept_474.min():.2f}")

# Check distance from LV septal to MM600
t_600 = KDTree(m600['v'])
d_sept_600, _ = t_600.query(all_sept_v)
print(f"LV septal to MM600 mean dist: {d_sept_600.mean():.2f}, median: {np.median(d_sept_600):.2f}, min: {d_sept_600.min():.2f}")
