with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    c = f.read()

idx1 = c.find('id="view-results"')
idx2 = c.find('id="view-viewer3d"')
snippet = c[idx1:idx2]
with open('.gemini/view_results_content.html', 'w', encoding='utf-8') as out:
    out.write(snippet)
print("Wrote view_results_content.html, length:", len(snippet))
