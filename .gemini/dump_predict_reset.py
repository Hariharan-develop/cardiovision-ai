with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx_predict = text.find('function predictRisk()')
if idx_predict != -1:
    print('=== PREDICT RISK FUNCTION ===')
    print(text[idx_predict:idx_predict+2500])

idx_reset = text.find('function resetForm()')
if idx_reset != -1:
    print('=== RESET FORM FUNCTION ===')
    print(text[idx_reset:idx_reset+2000])
