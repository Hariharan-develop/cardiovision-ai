import zipfile, trimesh, io

zip_path = r'C:\Users\hario\Downloads\BP51782_FMA3_2_1_inference_isa_FMA67135_Postnatal_anatomical_structure.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    for name in ['MM474', 'MM614', 'MM600', 'MM598', 'MM558']:
        for n in z.namelist():
            if os.path.basename(n).startswith(name + '_'):
                data = z.read(n).decode('utf-8')
                mesh = trimesh.load(io.StringIO(data), file_type='obj')
                print(f'{name:6s} | is_watertight: {mesh.is_watertight} | is_volume: {mesh.is_volume} | euler_num: {mesh.euler_number} | bounds:\n   min: {mesh.bounds[0]}\n   max: {mesh.bounds[1]}')
                break
