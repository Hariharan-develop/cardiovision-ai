import os
import sys
import json
import joblib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from shap_service import get_all_shap_explanations, compute_model_shap

feature_columns = joblib.load(os.path.join(BASE_DIR, "feature_columns.pkl"))
numeric_defaults = joblib.load(os.path.join(BASE_DIR, "numeric_defaults.pkl"))

cad_model = joblib.load(os.path.join(BASE_DIR, "cad_model.pkl"))
lad_model = joblib.load(os.path.join(BASE_DIR, "lad_model.pkl"))
lcx_model = joblib.load(os.path.join(BASE_DIR, "lcx_model.pkl"))
rca_model = joblib.load(os.path.join(BASE_DIR, "rca_model.pkl"))
lcx_model_candidate = joblib.load(os.path.join(BASE_DIR, "lcx_model_candidate.pkl"))
rca_model_candidate = joblib.load(os.path.join(BASE_DIR, "rca_model_candidate.pkl"))

with open(os.path.join(BASE_DIR, "candidate_thresholds.json"), "r") as f:
    cand_thresh = json.load(f)

print("1. CANDIDATE THRESHOLDS CHECK:")
print(f"   LCX threshold: {cand_thresh.get('LCX')} (expected 0.45)")
print(f"   RCA threshold: {cand_thresh.get('RCA')} (expected 0.40)")
assert abs(cand_thresh.get('LCX') - 0.45) < 1e-4
assert abs(cand_thresh.get('RCA') - 0.40) < 1e-4

# Test patient 1
patient1 = {col: numeric_defaults.get(col, 0) for col in feature_columns}
patient1['Age'] = 65
patient1['Weight'] = 82
patient1['Length'] = 172
patient1['Current Smoker'] = 1
patient1['Typical Chest Pain'] = 1
patient1['Dyspnea_Y'] = 0
patient1['DM'] = 1

df1 = pd.DataFrame([[patient1[col] for col in feature_columns]], columns=feature_columns)

print("\n2. VERIFYING STANDARD MODE SHAP EXPLANATIONS:")
std_exp = get_all_shap_explanations(cad_model, lad_model, lcx_model, rca_model, df1, is_candidate=False)
for vessel in ['cad', 'lad', 'lcx', 'rca']:
    info = std_exp[vessel]
    print(f"   [{vessel.upper()}] model={info['model_file']} | explainer={info['explainer_type']} | scale={info['scale']}")
    print(f"       target={info['target_class']} | base={info['base_value_display']} | output={info['model_output_display']}")
    print(f"       top feature: {info['top_features'][0]['display_name']} ({info['top_features'][0]['patient_value']}) -> {info['top_features'][0]['display_shap']} [{info['top_features'][0]['direction']}]")
    assert info['available'] == True
    assert len(info['top_features']) == 5
    assert len(info['waterfall_steps']) > 0

print("\n3. VERIFYING EXPERIMENTAL MODE SHAP EXPLANATIONS:")
cand_exp = get_all_shap_explanations(cad_model, lad_model, lcx_model_candidate, rca_model_candidate, df1, is_candidate=True)
for vessel in ['cad', 'lad', 'lcx', 'rca']:
    info = cand_exp[vessel]
    print(f"   [{vessel.upper()}] model={info['model_file']} | explainer={info['explainer_type']} | scale={info['scale']}")
    print(f"       target={info['target_class']} | base={info['base_value_display']} | output={info['model_output_display']}")
    print(f"       top feature: {info['top_features'][0]['display_name']} ({info['top_features'][0]['patient_value']}) -> {info['top_features'][0]['display_shap']} [{info['top_features'][0]['direction']}]")
    assert info['available'] == True
    assert len(info['top_features']) == 5
    if vessel == 'lcx':
        assert info['model_file'] == 'lcx_model_candidate.pkl'
        assert info['is_candidate'] == True
    elif vessel == 'rca':
        assert info['model_file'] == 'rca_model_candidate.pkl'
        assert info['is_candidate'] == True

print("\n4. VERIFYING ADDITIVITY AND SCALE FIDELITY:")
# Tree models: Base probability + sum(shap) == model.predict_proba positive class
lad_prob = lad_model.predict_proba(df1)[0][1]
# compute all shap sum for LAD
lad_full = compute_model_shap('lad', lad_model, df1, 'lad_model.pkl')
# Check last cumulative in waterfall is within precision
lad_last_cum = lad_full['waterfall_steps'][-1]['cumulative']
print(f"   LAD: Model Prob = {lad_prob:.4f}, Waterfall final = {lad_last_cum:.4f}, diff = {abs(lad_prob - lad_last_cum):.4f}")
assert abs(lad_prob - lad_last_cum) < 1e-3

# RCA linear model: Base log-odds + sum(shap) == decision_function
rca_margin = rca_model.decision_function(df1)[0]
rca_full = compute_model_shap('rca', rca_model, df1, 'rca_model.pkl')
rca_last_cum = rca_full['waterfall_steps'][-1]['cumulative']
print(f"   RCA (Std): Decision log-odds = {rca_margin:.4f}, Waterfall final = {rca_last_cum:.4f}, diff = {abs(rca_margin - rca_last_cum):.4f}")
assert abs(rca_margin - rca_last_cum) < 1e-3

# CAD positive class sign check (CAD is class 0)
cad_raw_dec = cad_model.decision_function(df1)[0]
cad_cad_dec = -cad_raw_dec
cad_full = compute_model_shap('cad', cad_model, df1, 'cad_model.pkl')
cad_last_cum = cad_full['waterfall_steps'][-1]['cumulative']
print(f"   CAD (Positive class 'CAD'): Logit = {cad_cad_dec:.4f}, Waterfall final = {cad_last_cum:.4f}, diff = {abs(cad_cad_dec - cad_last_cum):.4f}")
assert abs(cad_cad_dec - cad_last_cum) < 1e-3

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
