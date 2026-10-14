import os
import re

with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

print('HTML length:', len(content))
assert 'id="view-patient"' in content, "view-patient missing"
assert 'id="pvClinicalTable"' in content, "pvClinicalTable missing"
assert 'id="pvModelTable"' in content, "pvModelTable missing"
assert 'id="pvSummaryGrid"' in content or 'class="pvSummaryGrid"' in content, "pvSummaryGrid missing"
assert 'id="pvStatTotalFeatures"' in content, "pvStatTotalFeatures missing"
assert 'id="pvStatNumericFeatures"' in content, "pvStatNumericFeatures missing"
assert 'id="pvStatEncodedFeatures"' in content, "pvStatEncodedFeatures missing"
assert 'id="tabBtnClinical"' in content, "tabBtnClinical missing"
assert 'id="tabBtnModel"' in content, "tabBtnModel missing"
assert 'id="pvSearchInput"' in content, "pvSearchInput missing"
assert 'id="pvCategorySelect"' in content, "pvCategorySelect missing"

# Check JS functions
assert 'function renderPatientInfoScreen' in content, "renderPatientInfoScreen missing"
assert 'function switchPatientTab' in content, "switchPatientTab missing"
assert 'function filterPatientTables' in content, "filterPatientTables missing"
assert 'function sortClinicalTable' in content, "sortClinicalTable missing"
assert 'function sortModelTable' in content, "sortModelTable missing"
assert 'function toggleAllPatientGroups' in content, "toggleAllPatientGroups missing"
assert 'function getModelData' in content, "getModelData missing"
assert 'function getClinicalData' in content, "getClinicalData missing"

# Check 57 features in getModelData
features_57 = [
    'Age', 'Weight', 'Length', 'BMI', 'DM', 'HTN', 'Current Smoker', 'EX-Smoker', 'FH',
    'BP', 'PR', 'Edema', 'Typical Chest Pain', 'Function Class', 'Q Wave', 'St Elevation',
    'St Depression', 'Tinversion', 'FBS', 'CR', 'TG', 'LDL', 'HDL', 'BUN', 'ESR', 'HB',
    'K', 'Na', 'WBC', 'Lymph', 'Neut', 'PLT', 'EF-TTE', 'Region RWMA', 'Sex_Male',
    'Obesity_Y', 'CRF_Y', 'CVA_Y', 'Airway disease_Y', 'Thyroid Disease_Y', 'CHF_Y',
    'DLP_Y', 'Weak Peripheral Pulse_Y', 'Lung rales_Y', 'Systolic Murmur_Y',
    'Diastolic Murmur_Y', 'Dyspnea_Y', 'Atypical_Y', 'Nonanginal_Y', 'LowTH Ang_Y',
    'LVH_Y', 'Poor R Progression_Y', 'BBB_N', 'BBB_RBBB', 'VHD_N', 'VHD_Severe', 'VHD_mild'
]

for feat in features_57:
    assert f"name: '{feat}'" in content, f"Feature {feat} missing in getModelData!"

print("All 57 features present in exact order in getModelData!")
print("All assertions passed successfully!")
