with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('DOMContentLoaded')
if idx == -1: idx = text.find('window.onload')
print('DOMContentLoaded / onload index:', idx)
if idx != -1:
    print(text[idx-50:idx+1500])

# Also check IS_CUSTOM_PRED
idx2 = text.find('IS_CUSTOM_PRED')
print('IS_CUSTOM_PRED index:', idx2)
if idx2 != -1:
    print(text[idx2-50:idx2+500])
