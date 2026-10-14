import urllib.request, urllib.parse, re

with open(r'C:\Users\hario\Downloads\CardioVision_BodyParts3D_ThreeJS_Preview\CardioVision_3D_Preview\viewer.html', 'r', encoding='utf-8') as f:
    text = f.read()

entries = re.findall(r'"filename":\s*"([^"]+)"', text)
failures = []
for e in entries:
    url = 'http://localhost:8000/models/' + urllib.parse.quote(e)
    try:
        req = urllib.request.urlopen(url)
        if req.status != 200:
            failures.append((e, req.status))
    except Exception as err:
        failures.append((e, str(err)))

print(f'Tested {len(entries)} files. Failed: {len(failures)}')
for f, err in failures:
    print('  FAIL:', f, '->', err)
