import urllib.request, re

req = urllib.request.Request("http://localhost:8501/", headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req).read().decode('utf-8')

# Find all scripts in the parent page
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print(f"Parent page scripts count: {len(scripts)}")
for s in scripts:
    if len(s) < 200:
        print(s)
