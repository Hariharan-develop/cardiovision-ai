import sys, os
sys.path.insert(0, os.path.abspath("."))
import re
from clinical_extractor import CLINICAL_PATTERNS

with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

vp = text[text.find('id="view-predict"'):text.find('id="view-patient"')]
inputs = set(n for i, n in re.findall(r'<(?:input|select)[^>]+id=["\']([^"\']+)["\'][^>]*name=["\']([^"\']+)["\']', vp))
inputs.discard('model_mode')
inputs.discard('patient_id')
inputs.discard('patient_name')

pat_keys = set(CLINICAL_PATTERNS.keys())
pat_keys.discard('patient_id')
pat_keys.discard('patient_name')

print('In inputs but not in CLINICAL_PATTERNS:', inputs - pat_keys)
print('In CLINICAL_PATTERNS but not in inputs:', pat_keys - inputs)
print('Total form input keys matching patterns:', len(inputs.intersection(pat_keys)))
