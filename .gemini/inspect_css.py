with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
idx = text.find('.viewContainer')
if idx != -1:
    print(text[idx-50:idx+400])

idx2 = text.find('.mainView')
if idx2 != -1:
    print(text[idx2-50:idx2+400])
