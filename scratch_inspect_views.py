import re

with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'id="view-' in line:
        print(f"Line {i+1}: {line.strip()[:100]}")
