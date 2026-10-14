with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Title section
idx_title = text.find('Interactive 3D Anatomical Heart')
print("Title match:", idx_title)
if idx_title != -1:
    print(text[idx_title-50:idx_title+200])

# 2. switchNav section
idx_nav = text.find('function switchNav(viewId){')
print("\nswitchNav match:", idx_nav)
if idx_nav != -1:
    print(text[idx_nav:idx_nav+500])

# 3. clearPredictionResults 3D section
idx_clear = text.find('// 6. Clear 3D prediction highlights')
print("\nclearPredictionResults match:", idx_clear)
if idx_clear != -1:
    print(text[idx_clear:idx_clear+600])

# 4. DOMContentLoaded section
idx_dom = text.find("document.addEventListener('DOMContentLoaded', function(){")
print("\nDOMContentLoaded match:", idx_dom)
if idx_dom != -1:
    print(text[idx_dom:idx_dom+500])
