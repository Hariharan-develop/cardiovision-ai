import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx_m = text.find('function getModelData()')
end_m = text.find('function renderClinicalTable()', idx_m)
model_code = text[idx_m:end_m]

import re
items = re.findall(r'\{\s*num:\s*(\d+),\s*name:\s*[\'"]([^\'"]+)[\'"],\s*value:[^,]+,\s*type:\s*[\'"]([^\'"]+)[\'"],\s*desc:\s*[\'"]([^\'"]+)[\'"]', model_code)
print(f"Parsed {len(items)} model items:")
for num, name, ftype, desc in items:
    print(f"{num:2s}. {name:<25s} | {ftype:<16s} | {desc}")
