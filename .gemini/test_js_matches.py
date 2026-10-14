with open(".gemini/update_results_js.py", "r", encoding="utf-8") as f:
    content = f.read()

with open("cardiovision_exact_dashboard.html", "r", encoding="utf-8") as f:
    text = f.read()

import re
old_vars = re.findall(r'old_([a-zA-Z0-9_]+)\s*=\s*"""(.*?)"""', content, re.DOTALL)
print(f"Found {len(old_vars)} old_* variables")
for var_name, var_content in old_vars:
    in_text = var_content in text
    print(f"old_{var_name}: in_text={in_text}, length={len(var_content)}")
