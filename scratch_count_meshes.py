import re

with open("components/heart_viewer.html", "r", encoding="utf-8") as f:
    text = f.read()

entries = re.findall(r'"filename"\s*:\s*"([^"]+)"', text)
print("Total mesh entries in components/heart_viewer.html:", len(entries))
