import zipfile, os, numpy as np
from scipy.spatial import cKDTree

zip_path = r'C:\Users\hario\Downloads\BP51782_FMA3_2_1_inference_isa_FMA67135_Postnatal_anatomical_structure.zip'

def read_verts(z, prefix):
    for n in z.namelist():
        if os.path.basename(n).startswith(prefix + '_'):
            v = []
            for l in z.read(n).decode('utf-8').splitlines():
                if l.startswith('v '):
                    parts = l.split()
                    v.append([float(parts[1]), float(parts[2]), float(parts[3])])
            return np.array(v), os.path.basename(n)
    return None, None

with zipfile.ZipFile(zip_path, 'r') as z:
    # Existing key structures
    v_aorta, n_aorta = read_verts(z, 'MM506') # Ascending aorta
    v_pa, n_pa = read_verts(z, 'MM607')       # Pulmonary trunk
    v_lv, n_lv = read_verts(z, 'MM474')       # LV free wall
    v_rv, n_rv = read_verts(z, 'MM598')       # RV inflow
    v_rvo, n_rvo = read_verts(z, 'MM538')     # RV outflow
    v_la, n_la = read_verts(z, 'MM632')       # LA anterior
    v_ra, n_ra = read_verts(z, 'MM559')       # RA anterior

    # Check candidate additions
    candidates = [
        ('MM558', 'Wall of bulb of aorta (Aortic root)'),
        ('MM600', 'Muscular IV septum'),
        ('MM568', 'Membranous IV septum'),
        ('MM594', 'Muscular IV septum (additional)'),
        ('MM592', 'Interatrial septum'),
        ('MM590', 'Septal wall of right atrium'),
        ('MM595', 'Atrioventricular septum'),
        ('MM517', 'Fibrous ring of aortic valve'),
        ('MM520', 'Fibrous ring of aortic valve'),
        ('MM529', 'Fibrous ring of mitral valve'),
        ('MM572', 'Anulus proper of tricuspid valve'),
        ('MM519', 'Aortic valve - right posterior cusp'),
        ('MM521', 'Aortic valve - left posterior cusp'),
        ('MM524', 'Aortic valve - anterior cusp'),
        ('MM604', 'Pulmonary valve - right anterior cusp'),
        ('MM605', 'Pulmonary valve - posterior cusp'),
        ('MM606', 'Pulmonary valve - left anterior cusp'),
        ('MM541', 'Mitral valve - anterior leaflet'),
        ('MM542', 'Mitral valve - posterior leaflet'),
        ('MM575', 'Tricuspid valve - anterior leaflet'),
        ('MM570', 'Tricuspid valve - posterior leaflet'),
        ('MM573', 'Tricuspid valve - septal leaflet'),
        ('MM447', 'Great cardiac vein (sulcus interventricularis ant)'),
        ('MM449', 'Coronary sinus (sulcus coronarius)'),
        ('MM452', 'Small cardiac vein'),
        ('MM446', 'Anterior cardiac vein'),
        ('MM451', 'Right marginal vein')
    ]

    tree_aorta = cKDTree(v_aorta)
    tree_lv = cKDTree(v_lv)
    tree_rv = cKDTree(v_rv)

    print('Candidate analysis:')
    for prefix, desc in candidates:
        v_cand, n_cand = read_verts(z, prefix)
        if v_cand is None:
            print(f'MISSING: {prefix} ({desc})')
            continue
        
        # Check proximity to aorta, LV, RV
        d_aorta = tree_aorta.query(v_cand)[0].min()
        d_lv = tree_lv.query(v_cand)[0].min()
        d_rv = tree_rv.query(v_cand)[0].min()
        
        print(f'{prefix:6s} | {len(v_cand):5d} verts | min dist: Aorta={d_aorta:5.2f}mm, LV={d_lv:5.2f}mm, RV={d_rv:5.2f}mm | {desc}')
