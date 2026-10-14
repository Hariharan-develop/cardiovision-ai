import os, re

models_dir = r'C:\Users\hario\Downloads\CardioVision_BodyParts3D_ThreeJS_Preview\CardioVision_3D_Preview\models'
existing = set(os.listdir(models_dir))

with open(r'C:\Users\hario\Downloads\CardioVision_BodyParts3D_ThreeJS_Preview\CardioVision_3D_Preview\viewer.html', 'r', encoding='utf-8') as f:
    text = f.read()

entries = re.findall(r'"filename":\s*"([^"]+)"', text)
print(f'Total in viewer entries: {len(entries)}')
missing = [e for e in entries if e not in existing]
print(f'Missing files in models folder ({len(missing)}):')
for m in missing:
    print(' ', m)

# Also check if it is URL encoding in viewer.html:
# path = './models/' + encodeURIComponent(entry.filename)
print('\nTesting exact URL encoded paths against python server:')
for e in entries:
    actual = os.path.join(models_dir, e)
    if not os.path.exists(actual):
        print('FILE NOT ON DISK:', e)
