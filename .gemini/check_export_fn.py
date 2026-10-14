import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx_start = text.find('function exportClinicalReport(){')
idx_end = text.find('function sendNavigate(search){', idx_start)
print('idx_start:', idx_start, 'idx_end:', idx_end)
current_fn = text[idx_start:idx_end]
print("Current exportClinicalReport length:", len(current_fn))
