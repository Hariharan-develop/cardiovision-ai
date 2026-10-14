import re

with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

vp = text[text.find('id="view-predict"'):text.find('id="view-patient"')]
inputs = re.findall(r'<(?:input|select)[^>]+id=["\']([^"\']+)["\'][^>]*name=["\']([^"\']+)["\']', vp)
print(f"Total inputs found in view-predict: {len(inputs)}")
for i, n in inputs:
    print(f"  id='{i}', name='{n}'")
