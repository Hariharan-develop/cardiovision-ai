with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
print("Matches for Predict Cardiovascular Risk or submit / predict button:")
for m in re.finditer(r'Predict Cardiovascular Risk|runPrediction|submitForm|handlePredict', text):
    start = max(0, m.start() - 100)
    end = min(len(text), m.end() + 500)
    print("--- MATCH ---")
    print(text[start:end])
