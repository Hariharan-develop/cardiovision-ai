with open("cardiovision_exact_dashboard.html", "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = re.findall(r'<button[^>]*onclick="([^"]*reset[^"]*)"', text, re.IGNORECASE)
print("Button onlicks with reset:", matches)

fns = re.findall(r'function\s+([a-zA-Z0-9_]*reset[a-zA-Z0-9_]*)\s*\(', text, re.IGNORECASE)
print("Functions with reset in name:", fns)
