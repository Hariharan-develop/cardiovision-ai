with open("cardiovision_exact_dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

idx1 = html.find('id="view-results"')
idx2 = html.find('id="view-heart"')
res_view = html[idx1:idx2]

import re
matches = set(re.findall(r'\{([A-Z0-9_]+)\}', res_view))
print("Placeholders in view-results:", sorted(list(matches)))

# Compare with app.py replacements
with open("app.py", "r", encoding="utf-8") as f:
    app_code = f.read()

for m in sorted(list(matches)):
    in_app = f'"{m}"' in app_code or f'"{m}' in app_code or f'{{{m}}}' in app_code
    print(f"  {m}: in_app={in_app}")
