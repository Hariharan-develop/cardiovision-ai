with open("cardiovision_exact_dashboard.html", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('class="chartNote"')
if idx != -1:
    print(text[idx-50:idx+400])
