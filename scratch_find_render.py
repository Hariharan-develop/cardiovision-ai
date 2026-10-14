with open('components/heart_viewer.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if any(k in line.lower() for k in ['requestanimationframe', 'function animate', 'renderer.render', 'controls.update', 'devicepixelratio', 'clock']):
        print(f"Line {idx+1}: {line.strip()[:100]}")
