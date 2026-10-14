from clinical_extractor import parse_clinical_entities, process_uploaded_document

sample_text = """
CARDIOLOGY CLINICAL REPORT
Patient Name: Eleanor Vance
MRN: CV-90210
Age: 62 y/o | Gender: Female
Height: 165 cm | Weight: 68 kg
Vital Signs: BP: 142/88 mmHg, Heart Rate: 74 bpm
Medical History: Patient has a 10-year history of diabetes mellitus (T2DM) and essential hypertension.
Smoking status: Ex-smoker. Denies typical chest pain.
Echocardiogram: LVEF: 55%.
Labs:
Fasting Blood Sugar: 128 mg/dL
Serum Creatinine: 1.1 mg/dL
Total Triglycerides: 185 mg/dL
LDL-C: 130 mg/dL
HDL-C: 45 mg/dL
WBC: 6500 /uL
"""

entities = parse_clinical_entities(sample_text)
keys_to_show = ['patient_name', 'patient_id', 'age', 'sex', 'length', 'weight', 'bmi', 'bp', 'pr', 'ef_tte', 'dm', 'htn', 'ex_smoker', 'chest_pain', 'fbs', 'cr', 'tg', 'ldl', 'hdl', 'wbc', 'edema']
for k in keys_to_show:
    item = entities[k]
    print(f"{k:14}: val={item['value']} (Status: {item['status']}, Conf: {item['confidence']})")
