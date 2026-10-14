with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '.pvSummaryMeta' in l:
        print(f'CSS SummaryMeta: Line {i+1}')
    if '<div class="pvSummaryGrid">' in l:
        print(f'HTML SummaryGrid: Line {i+1}')
    if 'function updateBMI' in l:
        print(f'JS updateBMI: Line {i+1}')
    if 'function getClinicalData' in l:
        print(f'JS getClinicalData: Line {i+1}')
    if 'function renderClinicalTable' in l:
        print(f'JS renderClinicalTable: Line {i+1}')
