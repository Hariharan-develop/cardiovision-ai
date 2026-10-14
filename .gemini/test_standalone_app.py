import os
import sys

# Test whether app.py template substitution has any errors
try:
    with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
        html = f.read()
    print("HTML read successfully, size:", len(html))
except Exception as e:
    print("Error reading HTML:", e)

# Test shap_service import
try:
    from shap_service import get_all_shap_explanations
    import joblib
    import pandas as pd
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    cad_model = joblib.load(os.path.join(BASE_DIR, "cad_model.pkl"))
    lad_model = joblib.load(os.path.join(BASE_DIR, "lad_model.pkl"))
    lcx_model = joblib.load(os.path.join(BASE_DIR, "lcx_model.pkl"))
    rca_model = joblib.load(os.path.join(BASE_DIR, "rca_model.pkl"))
    lcx_model_candidate = joblib.load(os.path.join(BASE_DIR, "lcx_model_candidate.pkl"))
    rca_model_candidate = joblib.load(os.path.join(BASE_DIR, "rca_model_candidate.pkl"))
    feature_columns = joblib.load(os.path.join(BASE_DIR, "feature_columns.pkl"))
    numeric_defaults = joblib.load(os.path.join(BASE_DIR, "numeric_defaults.pkl"))
    
    models_dict = {
        'cad': cad_model,
        'lad': lad_model,
        'lcx': lcx_model,
        'rca': rca_model
    }
    sample_patient = {col: numeric_defaults.get(col, 0) for col in feature_columns}
    shap_res = get_all_shap_explanations(models_dict, sample_patient, 'standard')
    print("SHAP computed successfully! Keys:", list(shap_res.keys()))
except Exception as e:
    import traceback
    traceback.print_exc()
