import re

with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find view-predict
start = html.find('id="view-predict"')
end = html.find('id="view-patient"')
predict_section = html[start:end]

# Find all form inputs (inp_...)
inputs = re.findall(r'id=["\'](inp_[a-zA-Z0-9_]+)["\']', predict_section)
print(f"Total inp_ IDs in form: {len(inputs)}")

clinical_inputs = [i for i in inputs if i not in ['inp_patient_id', 'inp_patient_name', 'inp_bmi']]
print(f"Clinical inputs excluding Patient ID, Patient Name, and calculated BMI: {len(clinical_inputs)}")

# If we include BMI (which is a clinical measurement calculated from height & weight), total clinical attributes is 54!
all_clinical_attributes = [i for i in inputs if i not in ['inp_patient_id', 'inp_patient_name']]
print(f"All clinical attributes (including BMI): {len(all_clinical_attributes)}")

for idx, inp in enumerate(all_clinical_attributes, 1):
    print(f"{idx}: {inp}")
