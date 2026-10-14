import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Find getClinicalData definition
idx_c = text.find('function getClinicalData()')
if idx_c != -1:
    end_c = text.find('function getModelData()', idx_c)
    clinical_code = text[idx_c:end_c]
    # find category occurrences
    cats = re.findall(r'category:\s*[\'"]([^\'"]+)[\'"]', clinical_code)
    from collections import Counter
    print("Clinical Categories & counts:", Counter(cats))
    print("Total Clinical Attributes:", len(cats))

# Find getModelData definition
idx_m = text.find('function getModelData()')
if idx_m != -1:
    end_m = text.find('function renderClinicalTable()', idx_m)
    model_code = text[idx_m:end_m]
    # Check types: Numeric vs One-Hot
    types = re.findall(r'type:\s*[\'"]([^\'"]+)[\'"]', model_code)
    from collections import Counter
    print("\nModel Feature types:", Counter(types))
    print("Total Model Features:", len(types))
