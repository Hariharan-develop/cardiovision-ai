with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function applyPredictions')
if idx != -1:
    print('=== APPLY PREDICTIONS ===')
    print(text[idx:idx+2500])
