import os, numpy as np

obj_path = r'c:\Users\hario\Downloads\CardioVision-AI\assets\bodyparts3d\MM474_BP51876_FMA84850_Free wall of left ventricle.obj'

verts = []
normals = []
faces = []

with open(obj_path, 'r') as f:
    for line in f:
        if line.startswith('v '):
            verts.append([float(x) for x in line.split()[1:4]])
        elif line.startswith('vn '):
            normals.append([float(x) for x in line.split()[1:4]])
        elif line.startswith('f '):
            parts = line.split()[1:]
            # parse v//vn or v/vt/vn
            face_v = []
            face_vn = []
            for p in parts:
                sub = p.split('/')
                face_v.append(int(sub[0]) - 1)
                if len(sub) > 2 and sub[2]:
                    face_vn.append(int(sub[2]) - 1)
            faces.append((face_v, face_vn))

print(f'Verts: {len(verts)}, Normals: {len(normals)}, Faces: {len(faces)}')
# Check if normal indices match vertex indices
matching_indices = sum(1 for f_v, f_vn in faces if f_v == f_vn)
print(f'Faces where normal index == vertex index: {matching_indices}/{len(faces)}')

# Check face normal consistency
v_arr = np.array(verts)
vn_arr = np.array(normals)
inverted_normals = 0
for f_v, f_vn in faces:
    v0, v1, v2 = v_arr[f_v[0]], v_arr[f_v[1]], v_arr[f_v[2]]
    face_norm = np.cross(v1 - v0, v2 - v0)
    fn_len = np.linalg.norm(face_norm)
    if fn_len > 1e-6:
        face_norm /= fn_len
        if len(f_vn) >= 3:
            avg_vn = (vn_arr[f_vn[0]] + vn_arr[f_vn[1]] + vn_arr[f_vn[2]]) / 3.0
            if np.dot(face_norm, avg_vn) < 0:
                inverted_normals += 1

print(f'Faces with normal pointing opposite to geometric face normal: {inverted_normals}/{len(faces)}')
