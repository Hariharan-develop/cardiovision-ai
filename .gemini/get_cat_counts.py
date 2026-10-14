import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's see the model features list in JS
idx = text.find('function renderModelTable()')
if idx != -1:
    print('Found renderModelTable at', idx)
    snippet = text[idx:idx+4000]
    # find array of features
    import re
    # Look for categories assigned to features
    matches = re.findall(r'category:\s*[\'"]([^\'"]+)[\'"]', snippet)
    print("Unique categories in renderModelTable:", sorted(list(set(matches))))

    # Let's count features per category in model features
    lines = snippet.splitlines()
    cat_counts = {}
    for line in lines:
        m = re.search(r'category:\s*[\'"]([^\'"]+)[\'"]', line)
        if m:
            cat = m.group(1)
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
    print("Model features counts by category:", cat_counts)
    print("Total features in renderModelTable:", sum(cat_counts.values()))

idx_c = text.find('function renderClinicalTable()')
if idx_c != -1:
    print('\nFound renderClinicalTable at', idx_c)
    snippet_c = text[idx_c:idx_c+4000]
    matches_c = re.findall(r'category:\s*[\'"]([^\'"]+)[\'"]', snippet_c)
    print("Unique categories in renderClinicalTable:", sorted(list(set(matches_c))))
    cat_counts_c = {}
    for line in snippet_c.splitlines():
        m = re.search(r'category:\s*[\'"]([^\'"]+)[\'"]', line)
        if m:
            cat = m.group(1)
            cat_counts_c[cat] = cat_counts_c.get(cat, 0) + 1
    print("Clinical attributes counts by category:", cat_counts_c)
    print("Total attributes in renderClinicalTable:", sum(cat_counts_c.values()))
