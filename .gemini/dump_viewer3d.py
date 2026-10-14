with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('view-viewer3d')
print('Index:', idx)
if idx != -1:
    print('=== VIEW-VIEWER3D SECTION ===')
    print(text[idx-100:idx+3500])

print('\n=== SEARCHING FOR viewerIframe REFERENCES IN JS ===')
import re
for match in re.finditer(r'viewerIframe', text):
    start = max(0, match.start() - 100)
    end = min(len(text), match.end() + 200)
    print(text[start:end])
    print('---')
