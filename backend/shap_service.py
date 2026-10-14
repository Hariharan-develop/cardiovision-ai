"""
CardioVision AI - SHAP Explainability Service
Provides patient-specific SHAP explanations for CAD, LAD, LCX, and RCA models.
Adheres strictly to clinical explainability best practices:
- TreeExplainer for Random Forest models (probability scale)
- LinearExplainer for StandardScaler + LogisticRegression pipelines (log-odds scale)
- Dynamic class index detection via model.classes_
- No fabricated values; graceful error handling
- Research-only statistical interpretation labeling
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
import joblib

logger = logging.getLogger("CardioVision.SHAP")

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logger.warning("SHAP library is not installed. Explanations will be unavailable.")

# In-memory explainer cache to avoid recreating explainers on every query
_EXPLAINER_CACHE = {}

# Clinical feature metadata for user-friendly display
FEATURE_METADATA = {
    'Age': {'name': 'Age', 'unit': 'years', 'category': 'Basic Demographics', 'type': 'num'},
    'Weight': {'name': 'Body Weight', 'unit': 'kg', 'category': 'Basic Demographics', 'type': 'num'},
    'Length': {'name': 'Height / Stature', 'unit': 'cm', 'category': 'Basic Demographics', 'type': 'num'},
    'BMI': {'name': 'Body Mass Index (BMI)', 'unit': 'kg/m²', 'category': 'Basic Demographics', 'type': 'num'},
    'Sex_Male': {'name': 'Biological Sex', 'category': 'Basic Demographics', 'type': 'binary_sex'},
    'DM': {'name': 'Diabetes Mellitus', 'category': 'Medical History', 'type': 'binary'},
    'HTN': {'name': 'Hypertension', 'category': 'Medical History', 'type': 'binary'},
    'Current Smoker': {'name': 'Current Smoker', 'category': 'Medical History', 'type': 'binary'},
    'EX-Smoker': {'name': 'Ex-Smoker', 'category': 'Medical History', 'type': 'binary'},
    'FH': {'name': 'Family History CAD', 'category': 'Medical History', 'type': 'binary'},
    'Obesity_Y': {'name': 'Obesity (BMI ≥ 30)', 'category': 'Medical History', 'type': 'binary'},
    'CRF_Y': {'name': 'Chronic Renal Failure', 'category': 'Medical History', 'type': 'binary'},
    'CVA_Y': {'name': 'Cerebrovascular Accident', 'category': 'Medical History', 'type': 'binary'},
    'Airway disease_Y': {'name': 'Chronic Airway Disease', 'category': 'Medical History', 'type': 'binary'},
    'Thyroid Disease_Y': {'name': 'Thyroid Disease', 'category': 'Medical History', 'type': 'binary'},
    'CHF_Y': {'name': 'Congestive Heart Failure', 'category': 'Medical History', 'type': 'binary'},
    'DLP_Y': {'name': 'Dyslipidemia', 'category': 'Medical History', 'type': 'binary'},
    'Typical Chest Pain': {'name': 'Typical Anginal Chest Pain', 'category': 'Symptoms', 'type': 'binary'},
    'Dyspnea_Y': {'name': 'Dyspnea on Exertion', 'category': 'Symptoms', 'type': 'binary'},
    'Atypical_Y': {'name': 'Atypical Chest Pain', 'category': 'Symptoms', 'type': 'binary'},
    'Nonanginal_Y': {'name': 'Non-Anginal Chest Pain', 'category': 'Symptoms', 'type': 'binary'},
    'LowTH Ang_Y': {'name': 'Low-Threshold Angina', 'category': 'Symptoms', 'type': 'binary'},
    'Poor R Progression_Y': {'name': 'Poor R-Wave Progression', 'category': 'Symptoms', 'type': 'binary'},
    'BP': {'name': 'Resting Systolic BP', 'unit': 'mmHg', 'category': 'Vital Signs', 'type': 'num'},
    'PR': {'name': 'Resting Pulse Rate', 'unit': 'bpm', 'category': 'Vital Signs', 'type': 'num'},
    'EF-TTE': {'name': 'Ejection Fraction (EF-TTE)', 'unit': '%', 'category': 'Vital Signs', 'type': 'num'},
    'FBS': {'name': 'Fasting Blood Sugar', 'unit': 'mg/dL', 'category': 'Biomarkers', 'type': 'num'},
    'CR': {'name': 'Serum Creatinine', 'unit': 'mg/dL', 'category': 'Biomarkers', 'type': 'num'},
    'TG': {'name': 'Triglycerides', 'unit': 'mg/dL', 'category': 'Biomarkers', 'type': 'num'},
    'LDL': {'name': 'LDL Cholesterol', 'unit': 'mg/dL', 'category': 'Biomarkers', 'type': 'num'},
    'HDL': {'name': 'HDL Cholesterol', 'unit': 'mg/dL', 'category': 'Biomarkers', 'type': 'num'},
    'BUN': {'name': 'Blood Urea Nitrogen', 'unit': 'mg/dL', 'category': 'Biomarkers', 'type': 'num'},
    'ESR': {'name': 'Erythrocyte Sed. Rate', 'unit': 'mm/hr', 'category': 'Biomarkers', 'type': 'num'},
    'HB': {'name': 'Hemoglobin', 'unit': 'g/dL', 'category': 'Biomarkers', 'type': 'num'},
    'K': {'name': 'Serum Potassium', 'unit': 'mEq/L', 'category': 'Biomarkers', 'type': 'num'},
    'Na': {'name': 'Serum Sodium', 'unit': 'mEq/L', 'category': 'Biomarkers', 'type': 'num'},
    'WBC': {'name': 'White Blood Cell Count', 'unit': '/µL', 'category': 'Biomarkers', 'type': 'num'},
    'Lymph': {'name': 'Lymphocyte Percentage', 'unit': '%', 'category': 'Biomarkers', 'type': 'num'},
    'Neut': {'name': 'Neutrophil Percentage', 'unit': '%', 'category': 'Biomarkers', 'type': 'num'},
    'PLT': {'name': 'Platelet Count', 'unit': 'x10³/µL', 'category': 'Biomarkers', 'type': 'num'},
    'Q Wave': {'name': 'Pathologic Q-Wave', 'category': 'ECG & Telemetry', 'type': 'binary'},
    'St Elevation': {'name': 'ST Segment Elevation', 'category': 'ECG & Telemetry', 'type': 'binary'},
    'St Depression': {'name': 'ST Segment Depression', 'category': 'ECG & Telemetry', 'type': 'binary'},
    'Tinversion': {'name': 'T-Wave Inversion', 'category': 'ECG & Telemetry', 'type': 'binary'},
    'LVH_Y': {'name': 'Left Ventricular Hypertrophy', 'category': 'ECG & Telemetry', 'type': 'binary'},
    'BBB_N': {'name': 'Normal Conduction (No BBB)', 'category': 'ECG & Telemetry', 'type': 'binary'},
    'BBB_RBBB': {'name': 'Right Bundle Branch Block', 'category': 'ECG & Telemetry', 'type': 'binary'},
    'Region RWMA': {'name': 'Regional Wall Motion Abnormality', 'category': 'Echocardiography', 'type': 'binary'},
    'VHD_N': {'name': 'No Valvular Heart Disease', 'category': 'Valvular Disease', 'type': 'binary'},
    'VHD_Severe': {'name': 'Severe Valvular Disease', 'category': 'Valvular Disease', 'type': 'binary'},
    'VHD_mild': {'name': 'Mild Valvular Disease', 'category': 'Valvular Disease', 'type': 'binary'},
    'Edema': {'name': 'Peripheral Edema', 'category': 'Physical Findings', 'type': 'binary'},
    'Function Class': {'name': 'NYHA Functional Class', 'category': 'Physical Findings', 'type': 'cat'},
    'Weak Peripheral Pulse_Y': {'name': 'Weak Peripheral Pulse', 'category': 'Physical Findings', 'type': 'binary'},
    'Lung rales_Y': {'name': 'Lung Rales / Crackles', 'category': 'Physical Findings', 'type': 'binary'},
    'Systolic Murmur_Y': {'name': 'Systolic Heart Murmur', 'category': 'Physical Findings', 'type': 'binary'},
    'Diastolic Murmur_Y': {'name': 'Diastolic Heart Murmur', 'category': 'Physical Findings', 'type': 'binary'}
}

def format_patient_value(col, val):
    """Formats clinical input value into human-readable representation."""
    meta = FEATURE_METADATA.get(col, {})
    ftype = meta.get('type', 'num')
    unit = meta.get('unit', '')
    
    if ftype == 'binary':
        return 'Present (1)' if float(val) > 0.5 else 'Absent (0)'
    elif ftype == 'binary_sex':
        return 'Male' if float(val) > 0.5 else 'Female'
    elif ftype == 'cat':
        return f'Class {int(round(float(val)))}'
    else:
        v_num = float(val)
        if v_num.is_integer():
            s = f"{int(v_num)}"
        else:
            s = f"{v_num:.1f}"
        return f"{s} {unit}".strip()

def get_explainer_for_model(model_key, model_obj):
    """Retrieves or creates a cached SHAP explainer for a given model."""
    if not SHAP_AVAILABLE:
        return None
    
    cache_key = f"{model_key}_{id(model_obj)}"
    if cache_key in _EXPLAINER_CACHE:
        return _EXPLAINER_CACHE[cache_key]
    
    # Random Forest models -> TreeExplainer
    if hasattr(model_obj, 'estimators_'):
        explainer = shap.TreeExplainer(model_obj)
        _EXPLAINER_CACHE[cache_key] = ('tree', explainer)
        return _EXPLAINER_CACHE[cache_key]
    
    # Sklearn Pipeline (StandardScaler + LogisticRegression) -> LinearExplainer
    if hasattr(model_obj, 'named_steps'):
        scaler = model_obj.named_steps.get('scaler') or model_obj.named_steps.get('standardscaler')
        clf = model_obj.named_steps.get('model') or model_obj.named_steps.get('logisticregression')
        if clf is not None and scaler is not None:
            # Training background in standardized space has mean 0
            n_features = scaler.mean_.shape[0]
            bg_scaled = np.zeros((1, n_features))
            explainer = shap.LinearExplainer(clf, bg_scaled)
            _EXPLAINER_CACHE[cache_key] = ('linear', explainer, scaler, clf)
            return _EXPLAINER_CACHE[cache_key]
            
    return None

def compute_model_shap(model_key, model_obj, X_row, model_file_name, is_candidate=False):
    """
    Computes patient-specific SHAP values for a single model and input vector.
    Returns structured explanation data.
    """
    if not SHAP_AVAILABLE:
        return {
            'available': False,
            'reason': 'Explanation unavailable (SHAP library not installed)',
            'model_key': model_key,
            'model_file': model_file_name
        }
    
    try:
        explainer_tuple = get_explainer_for_model(model_key, model_obj)
        if explainer_tuple is None:
            return {
                'available': False,
                'reason': f'Explanation unavailable for model architecture {type(model_obj).__name__}',
                'model_key': model_key,
                'model_file': model_file_name
            }
        
        feature_names = list(X_row.columns)
        
        # Determine positive target class dynamically via model.classes_
        classes = list(model_obj.classes_)
        if 'CAD' in classes:
            target_class = 'CAD'
            pos_idx = classes.index('CAD')
        elif 'Stenotic' in classes:
            target_class = 'Stenotic'
            pos_idx = classes.index('Stenotic')
        elif 1 in classes:
            target_class = 'Stenotic (Class 1)'
            pos_idx = classes.index(1)
        else:
            pos_idx = 1
            target_class = str(classes[pos_idx])
        
        explainer_kind = explainer_tuple[0]
        
        if explainer_kind == 'tree':
            explainer = explainer_tuple[1]
            sv = explainer(X_row)
            
            # sv.values shape can be (1, 57, 2) or (1, 57)
            if len(sv.values.shape) == 3:
                shap_vals = sv.values[0, :, pos_idx]
                if len(sv.base_values.shape) > 1:
                    base_val = float(sv.base_values[0, pos_idx])
                else:
                    base_val = float(sv.base_values[0])
            else:
                shap_vals = sv.values[0, :]
                base_val = float(sv.base_values[0])
            
            scale = 'probability'
            scale_label = 'Probability scale (Δ probability)'
            scale_unit = 'prob'
            explainer_name = 'TreeExplainer (Tree SHAP)'
            model_output = float(base_val + np.sum(shap_vals))
            
        elif explainer_kind == 'linear':
            # Linear pipeline: StandardScaler + LogisticRegression
            scaler = explainer_tuple[2]
            clf = explainer_tuple[3]
            
            X_scaled = scaler.transform(X_row)
            
            # Identify class index in clf.classes_
            clf_classes = list(clf.classes_)
            clf_pos_idx = clf_classes.index(classes[pos_idx]) if classes[pos_idx] in clf_classes else pos_idx
            
            # In binary logistic regression:
            # If positive class is index 1: logit = w^T x_scaled + b
            # If positive class is index 0: logit = -w^T x_scaled - b
            if clf_pos_idx == 1:
                coef = clf.coef_[0]
                intercept = float(clf.intercept_[0])
            else:
                coef = -clf.coef_[0]
                intercept = -float(clf.intercept_[0])
            
            shap_vals = coef * X_scaled[0]
            base_val = intercept
            scale = 'log-odds'
            scale_label = 'Log-odds scale (Δ log-odds)'
            scale_unit = 'log-odds'
            explainer_name = 'LinearExplainer (Linear SHAP)'
            model_output = float(base_val + np.sum(shap_vals))
            
        else:
            return {
                'available': False,
                'reason': 'Explanation unavailable (Unknown explainer type)',
                'model_key': model_key,
                'model_file': model_file_name
            }
        
        # Build features list and sort by absolute SHAP contribution
        features_list = []
        for i, col in enumerate(feature_names):
            s_val = float(shap_vals[i])
            raw_val = float(X_row.iloc[0, i])
            display_name = FEATURE_METADATA.get(col, {}).get('name', col)
            category = FEATURE_METADATA.get(col, {}).get('category', 'Clinical Finding')
            formatted_val = format_patient_value(col, raw_val)
            
            # Direction relative to positive class output
            if s_val > 0.0001:
                direction = 'increases'
                direction_label = 'Increases Risk'
            elif s_val < -0.0001:
                direction = 'decreases'
                direction_label = 'Decreases Risk'
            else:
                direction = 'neutral'
                direction_label = 'Neutral'
            
            if scale == 'probability':
                display_shap = f"{'+' if s_val >= 0 else ''}{s_val * 100.0:.1f}%"
                num_shap_display = f"{'+' if s_val >= 0 else ''}{s_val:.4f}"
            else:
                display_shap = f"{'+' if s_val >= 0 else ''}{s_val:.3f} log-odds"
                num_shap_display = f"{'+' if s_val >= 0 else ''}{s_val:.3f}"
            
            features_list.append({
                'feature_col': col,
                'display_name': display_name,
                'category': category,
                'patient_value': formatted_val,
                'raw_value': round(raw_val, 2),
                'shap_value': round(s_val, 5),
                'abs_shap': abs(s_val),
                'display_shap': display_shap,
                'num_shap_display': num_shap_display,
                'direction': direction,
                'direction_label': direction_label
            })
        
        # Sort by absolute impact
        features_sorted = sorted(features_list, key=lambda x: x['abs_shap'], reverse=True)
        top5 = features_sorted[:5]
        for rank, item in enumerate(top5, 1):
            item['rank'] = rank
            
        remaining_shap = sum(f['shap_value'] for f in features_sorted[5:])
        
        # Build waterfall breakdown
        waterfall_steps = [{
            'label': 'Baseline (Expected Value E[f(x)])',
            'value': round(base_val, 4),
            'cumulative': round(base_val, 4),
            'type': 'base'
        }]
        
        running_total = base_val
        for item in top5:
            running_total += item['shap_value']
            waterfall_steps.append({
                'label': item['display_name'],
                'patient_val': item['patient_value'],
                'value': round(item['shap_value'], 4),
                'cumulative': round(running_total, 4),
                'direction': item['direction'],
                'type': 'feature'
            })
            
        running_total += remaining_shap
        waterfall_steps.append({
            'label': 'Remaining 52 Clinical Features',
            'value': round(remaining_shap, 4),
            'cumulative': round(running_total, 4),
            'direction': 'increases' if remaining_shap >= 0 else 'decreases',
            'type': 'remaining'
        })
        
        waterfall_steps.append({
            'label': 'Final Patient Model Output f(x)',
            'value': round(model_output, 4),
            'cumulative': round(model_output, 4),
            'type': 'final'
        })
        
        return {
            'available': True,
            'model_key': model_key,
            'model_file': model_file_name,
            'target_class': target_class,
            'explainer_type': explainer_name,
            'scale': scale,
            'scale_label': scale_label,
            'scale_unit': scale_unit,
            'base_value': round(base_val, 4),
            'base_value_display': f"{base_val * 100:.1f}%" if scale == 'probability' else f"{base_val:.3f} log-odds",
            'model_output': round(model_output, 4),
            'model_output_display': f"{model_output * 100:.1f}%" if scale == 'probability' else f"{model_output:.3f} log-odds",
            'top_features': top5,
            'all_features': features_list,
            'waterfall_steps': waterfall_steps,
            'is_candidate': is_candidate
        }
        
    except Exception as e:
        logger.error(f"Error computing SHAP for {model_key}: {e}", exc_info=True)
        return {
            'available': False,
            'reason': f'Explanation unavailable ({type(e).__name__})',
            'model_key': model_key,
            'model_file': model_file_name
        }

def get_all_shap_explanations(cad_m, lad_m, lcx_m, rca_m, X_df, is_candidate=False):
    """
    Computes explanations for all four active models for the given patient input.
    """
    lcx_file = "lcx_model_candidate.pkl" if is_candidate else "lcx_model.pkl"
    rca_file = "rca_model_candidate.pkl" if is_candidate else "rca_model.pkl"
    
    explanations = {
        'cad': compute_model_shap('cad', cad_m, X_df, 'cad_model.pkl', is_candidate=False),
        'lad': compute_model_shap('lad', lad_m, X_df, 'lad_model.pkl', is_candidate=False),
        'lcx': compute_model_shap('lcx', lcx_m, X_df, lcx_file, is_candidate=is_candidate),
        'rca': compute_model_shap('rca', rca_m, X_df, rca_file, is_candidate=is_candidate)
    }
    
    return explanations
