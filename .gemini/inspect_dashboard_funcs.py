with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'(function\s+(?:predictRisk|resetForm|doPredict|doReset|onPredict|switchNav)[^{]*\{.*?\n\})', text, re.DOTALL)
print(f"Found {len(matches)} key functions:")
for m in matches:
    print(m[:500])
    print('...\n')
