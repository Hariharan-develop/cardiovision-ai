with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if any(k in line for k in ['btnPredict', 'predictRisk', 'submitForm', 'runPrediction', 'doNavigate']):
        print(f"Line {idx+1}: {line.strip()[:100]}")
