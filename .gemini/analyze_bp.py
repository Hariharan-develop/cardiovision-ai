import csv

with open(r'C:\Users\hario\Downloads\BodyParts3D_OBJ_inventory.csv', 'r') as f:
    for r in csv.DictReader(f):
        if r['bp'] == 'BP51876':
            print(f"{r['mm']:6s} | {r['name']:40s} | {r['vertices']} verts | {r['faces']} faces | X:[{r['xmin']},{r['xmax']}] Y:[{r['ymin']},{r['ymax']}] Z:[{r['zmin']},{r['zmax']}]")
