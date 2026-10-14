import zipfile, os

zip_path = r'C:\Users\hario\Downloads\BP51782_FMA3_2_1_inference_isa_FMA67135_Postnatal_anatomical_structure.zip'
dest1 = r'C:\Users\hario\Downloads\CardioVision_BodyParts3D_ThreeJS_Preview\CardioVision_3D_Preview\models'
dest2 = r'c:\Users\hario\Downloads\CardioVision-AI\assets\bodyparts3d'

# Extract all 129 files from zip into dest1 and dest2 so all verified meshes are available
with zipfile.ZipFile(zip_path, 'r') as z:
    for n in z.namelist():
        if not n.endswith('.obj'): continue
        base = os.path.basename(n)
        data = z.read(n)
        
        p1 = os.path.join(dest1, base)
        if not os.path.exists(p1):
            with open(p1, 'wb') as f:
                f.write(data)
                
        p2 = os.path.join(dest2, base)
        if not os.path.exists(p2):
            with open(p2, 'wb') as f:
                f.write(data)

print(f'Dest1 (models) now contains {len(os.listdir(dest1))} files.')
print(f'Dest2 (assets/bodyparts3d) now contains {len(os.listdir(dest2))} files.')
