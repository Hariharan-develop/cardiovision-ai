with open("cardiovision_exact_dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

idx1 = html.find('id="view-results"')
idx2 = html.find('id="view-heart"')
res_section = html[idx1:idx2]

print("Length of res_section:", len(res_section))
print("--- FIRST 800 CHARS ---")
print(res_section[:800])
