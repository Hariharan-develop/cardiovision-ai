import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function renderModelTable()')
print(text[idx:idx+1200])

idx_c = text.find('function renderClinicalTable()')
print("\n" + "="*50 + "\n")
print(text[idx_c:idx_c+1200])
