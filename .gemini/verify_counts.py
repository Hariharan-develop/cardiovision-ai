import re

with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'function getClinicalData\(\)\{.*?return \[(.*?)\];\s*\}', text, re.DOTALL)
if match:
    items = re.findall(r"name:\s*'([^']+)'", match.group(1))
    print('Tab 1 Clinical Attributes Count:', len(items))
    for i, it in enumerate(items):
        print(f'{i+1}: {it}')
else:
    print('Could not find getClinicalData array')
