import json, urllib.request, urllib.parse

with open('.gemini/final_heart_entries.json') as f:
    entries = json.load(f)

print(f"Testing {len(entries)} models against http://127.0.0.1:8502/models/ ...")
failures = []
successes = 0

for e in entries:
    fname = e['filename']
    url = f"http://127.0.0.1:8502/models/{urllib.parse.quote(fname)}"
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                successes += 1
            else:
                failures.append((fname, resp.status))
    except Exception as ex:
        failures.append((fname, str(ex)))

print(f"Results: {successes} succeeded, {len(failures)} failed.")
if failures:
    print("Failures:", failures[:5])
