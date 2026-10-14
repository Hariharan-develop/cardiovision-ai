with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
print("Occurrences of viewerIframe:")
for m in re.finditer(r'viewerIframe', text):
    start = max(0, m.start() - 150)
    end = min(len(text), m.end() + 250)
    print("--- MATCH ---")
    print(text[start:end])

print("\nOccurrences of updateProbabilities:")
for m in re.finditer(r'updateProbabilities', text):
    start = max(0, m.start() - 150)
    end = min(len(text), m.end() + 250)
    print("--- MATCH ---")
    print(text[start:end])

print("\nOccurrences of reset or clearPredictionResults:")
for m in re.finditer(r'clearPredictionResults|resetPrediction', text):
    start = max(0, m.start() - 100)
    end = min(len(text), m.end() + 300)
    print("--- MATCH ---")
    print(text[start:end])
