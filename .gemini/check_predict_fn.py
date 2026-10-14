with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function clearPredictionResults')
if idx != -1:
    print(text[idx-1200:idx+200])
