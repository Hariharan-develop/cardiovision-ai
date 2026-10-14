import re

files_to_check = [
    'app.py',
    'api_server.py',
    'cardiovision_exact_dashboard.html',
    'components/heart_viewer.html',
    '3d-test/viewer.html'
]

features = ['ambient-light-sensor', 'battery', 'document-domain', 'layout-animations', 'legacy-image-formats', 'oversized-images', 'vr', 'wake-lock', 'allow-scripts', 'allow-same-origin', 'sandbox', 'allow=']

for fpath in files_to_check:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    for feat in features:
        if feat in content:
            print(f"Found '{feat}' in {fpath}")
            # print surrounding lines
            for line_no, line in enumerate(content.splitlines()):
                if feat in line:
                    print(f"  Line {line_no+1}: {line[:120]}")
