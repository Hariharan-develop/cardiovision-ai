with open("cardiovision_exact_dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

import re
matches = re.findall(r'<div[^>]*id="([^"]+)"[^>]*class="[^"]*mainView', html)
matches += re.findall(r'<div[^>]*class="[^"]*mainView[^"]*"[^>]*id="([^"]+)"', html)
print("Views:", sorted(list(set(matches))))
