with open("cardiovision_exact_dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

idx1 = html.find('id="view-results"')
idx2 = html.find('id="view-viewer3d"')
res_section = html[idx1:idx2]

print("--- PATIENT INFO IN RES_SECTION ---")
for line in res_section.splitlines()[:60]:
    print(line)
