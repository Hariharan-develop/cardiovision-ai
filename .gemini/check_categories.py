with open("cardiovision_exact_dashboard.html", "r", encoding="utf-8") as f:
    text = f.read()

idx1 = text.find('id="view-patient"')
idx2 = text.find('id="view-results"')
patient_view = text[idx1:idx2]

import re
print("Categories mentioned in patient_view:")
for line in patient_view.splitlines():
    if any(k in line for k in ['Basic Information', 'Medical History', 'Symptoms', 'Vital Signs', 'Laboratory', 'ECG', 'Additional']):
        print(" ", line.strip()[:140])

# Also check feature counts in renderPatientInfoScreen in JS
js_idx = text.find('function renderPatientInfoScreen()')
if js_idx != -1:
    print("\n--- renderPatientInfoScreen snippet ---")
    print(text[js_idx:js_idx+1500])
