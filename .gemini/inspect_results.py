with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'view-results' in l or 'exportClinicalReport' in l:
        print(f'Line {i+1}: {l.strip()[:120]}')
