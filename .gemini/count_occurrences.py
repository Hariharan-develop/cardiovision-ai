with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

for term in ['Export Clinical Report', 'explainable cardiovascular', 'Global coronary tree disease burden', 'Patient-specific feature attribution']:
    count = text.count(term)
    print(f'"{term}": {count} occurrences')
