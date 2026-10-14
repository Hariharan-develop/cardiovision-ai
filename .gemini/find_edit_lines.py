import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'viewTitleBox' in l and i > 1500 and i < 1700:
        print(f"--- Header lines {i+1} to {i+20} ---")
        for j in range(i, min(len(lines), i+18)):
            print(f"{j+1}: {lines[j]}", end='')
        break

for i, l in enumerate(lines):
    if 'chartNote' in l and i > 1600 and i < 1900:
        print(f"\n--- chartNote lines {i+1} to {i+10} ---")
        for j in range(i-2, min(len(lines), i+8)):
            print(f"{j+1}: {lines[j]}", end='')
        break

for i, l in enumerate(lines):
    if 'Coronary Stenosis Interpretation' in l and i > 1700 and i < 2000:
        print(f"\n--- Stenosis Interpretation lines {i+1} to {i+25} ---")
        for j in range(i-2, min(len(lines), i+25)):
            print(f"{j+1}: {lines[j]}", end='')
        break

for i, l in enumerate(lines):
    if 'Understanding the Prediction' in l and i > 1800 and i < 2100:
        print(f"\n--- Understanding the Prediction lines {i+1} to {i+35} ---")
        for j in range(i-2, min(len(lines), i+35)):
            print(f"{j+1}: {lines[j]}", end='')
        break
