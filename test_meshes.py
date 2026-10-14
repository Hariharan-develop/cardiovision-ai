import re
import os

with open("components/heart_viewer.html", "r", encoding="utf-8") as f:
    content = f.read()

matches = re.findall(r'"filename"\s*:\s*"([^"]+)"', content)
print(f"Total entries: {len(matches)}")

missing = []
for fname in matches:
    p1 = os.path.join("assets", "bodyparts3d", fname)
    p2 = os.path.join("3d-test", "models", fname)
    if not os.path.exists(p1) and not os.path.exists(p2):
        missing.append(fname)

print(f"Missing count: {len(missing)}")
if missing:
    print("Sample missing:", missing[:5])
else:
    print("ALL 106 MESHES EXIST ON DISK!")
