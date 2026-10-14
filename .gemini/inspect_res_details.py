with open("cardiovision_exact_dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

idx1 = html.find('id="view-results"')
idx2 = html.find('id="view-heart"')
res_section = html[idx1:idx2]

# Let's inspect headings, classes, and sections
import re
print("Headings:")
for h in re.findall(r'<h[1-4][^>]*>(.*?)</h[1-4]>', res_section):
    print(" ", h.strip())

print("\nPatient bar:")
pat_bar = re.search(r'(<div[^>]*patient[^>]*>.*?</div>)', res_section, re.DOTALL | re.IGNORECASE)
if pat_bar:
    print(pat_bar.group(1)[:300])

print("\nSearch for notices / warnings:")
for match in re.finditer(r'<div[^>]*class="[^"]*(?:Notice|Alert|Note|warning)[^"]*"[^>]*>(.*?)</div>', res_section, re.DOTALL | re.IGNORECASE):
    clean = re.sub(r'<[^>]+>', ' ', match.group(0))
    clean = ' '.join(clean.split())
    print(" -", clean[:150])
