with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'class="nav"' in line:
        print(f"Nav container: line {idx+1}")
    if 'view-predict' in line and 'id=' in line:
        print(f"view-predict: line {idx+1}")
    if 'view-results' in line and 'id=' in line:
        print(f"view-results: line {idx+1}")
    if 'view-viewer3d' in line and 'id=' in line:
        print(f"view-viewer3d: line {idx+1}")
    if 'function switchNav' in line or 'function switchView' in line:
        print(f"switchNav function: line {idx+1}")
