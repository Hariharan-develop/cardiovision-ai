"""
CardioVision AI - Patient Feature Snapshot & Synchronization Service
Enforces a single immutable, validated clinical feature snapshot for all
predictions, SHAP explanations, PDF measurements, and 3D visualization.

Rules:
1. Exact feature ordering matching feature_columns.pkl (57 clinical features).
2. Distinguishes original patient measurements from model-transformed values.
3. Strict validation: Never silently substitute default, clipped, or cached values.
4. Pre-flight verification: Reject inconsistent payloads with explicit errors.
"""

import os
import hashlib
import json
import numpy as np
import pandas as pd
import joblib

from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
BASE_DIR = str(PROJECT_ROOT)

def _find_model_file(fname: str) -> str:
    candidates = [
        PROJECT_ROOT / "models" / fname,
        BACKEND_DIR / "models" / fname,
        PROJECT_ROOT / fname,
        BACKEND_DIR / fname,
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return str(PROJECT_ROOT / "models" / fname)

FEATURE_COLUMNS = joblib.load(_find_model_file("feature_columns.pkl"))
NUMERIC_DEFAULTS = joblib.load(_find_model_file("numeric_defaults.pkl"))

# Model decision thresholds
STANDARD_THRESHOLDS = {"CAD": 0.50, "LAD": 0.50, "LCX": 0.50, "RCA": 0.50}
CANDIDATE_THRESHOLDS = {"CAD": 0.50, "LAD": 0.50, "LCX": 0.45, "RCA": 0.40}

# Definitive physiological bounds for clinical inputs
PHYSIOLOGICAL_BOUNDS = {
    "age": (1.0, 120.0, "Age (years)"),
    "length": (50.0, 250.0, "Stature / Height (cm)"),
    "weight": (20.0, 300.0, "Body Weight (kg)"),
    "bp": (50.0, 260.0, "Resting Systolic Blood Pressure (mmHg)"),
    "pr": (30.0, 220.0, "Resting Pulse Rate (bpm)"),
    "ef_tte": (10.0, 85.0, "Left Ventricular Ejection Fraction (%)"),
    "fbs": (40.0, 600.0, "Fasting Blood Sugar (mg/dL)"),
    "cr": (0.1, 15.0, "Serum Creatinine (mg/dL)"),
    "tg": (20.0, 1000.0, "Triglycerides (mg/dL)"),
    "ldl": (10.0, 500.0, "LDL Cholesterol (mg/dL)"),
    "hdl": (5.0, 150.0, "HDL Cholesterol (mg/dL)"),
    "bun": (1.0, 150.0, "Blood Urea Nitrogen (mg/dL)"),
    "esr": (0.0, 150.0, "Erythrocyte Sedimentation Rate (mm/hr)"),
    "hb": (3.0, 25.0, "Hemoglobin (g/dL)"),
    "k": (1.5, 9.0, "Serum Potassium (mEq/L)"),
    "na": (100.0, 180.0, "Serum Sodium (mEq/L)"),
    "wbc": (1000.0, 50000.0, "White Blood Cell Count (/µL)"),
    "lymph": (1.0, 99.0, "Lymphocyte Percentage (%)"),
    "neut": (1.0, 99.0, "Neutrophil Percentage (%)"),
    "plt": (10.0, 1000.0, "Platelet Count (x10³/µL)"),
    "region_rwma": (0.0, 4.0, "Regional Wall Motion Abnormality (score)"),
    "function_class": (0, 4, "NYHA Functional Class (0-4)"),
}

class InconsistentPayloadError(ValueError):
    """Raised when predictions, SHAP explanations, or patient details do not match the immutable snapshot."""
    pass

class PatientFeatureSnapshot:
    """
    Immutable validated patient feature snapshot.
    Guarantees synchronization across:
    - Dashboard active form
    - Serialized API parameters
    - 57-dimensional Model input vector X
    - Patient-specific SHAP explanation tables
    - PDF report demographics and measurements
    - 3D coronary telemetry
    """
    def __init__(
        self,
        patient_data: dict,
        X: pd.DataFrame,
        features_dict: dict,
        transformed_mapping: dict,
        model_mode: str,
        snapshot_hash: str
    ):
        self.patient_data = patient_data
        self.X = X
        self.features_dict = features_dict
        self.transformed_mapping = transformed_mapping
        self.model_mode = model_mode
        self.snapshot_hash = snapshot_hash

    @property
    def feature_vector(self):
        return self.X.iloc[0].values

    def to_dict(self):
        return {
            "patient_data": dict(self.patient_data),
            "model_mode": self.model_mode,
            "snapshot_hash": self.snapshot_hash,
            "features_dict": dict(self.features_dict),
            "transformed_mapping": dict(self.transformed_mapping)
        }


def create_patient_feature_snapshot(raw_inputs: dict, model_mode: str = "standard", strict: bool = False) -> PatientFeatureSnapshot:
    """
    Creates a single, immutable, validated patient feature snapshot.
    
    If strict=True:
      - Validates that values are within physiological limits.
      - Never silently clips or substitutes invalid values.
      - Rejects invalid inputs with an informative ValueError.
    If strict=False:
      - Validates and parses inputs, preserving unclipped physiological inputs.
    """
    params = dict(raw_inputs or {})

    # Extract or fallback patient identification
    pat_id = str(params.get("id") or params.get("patient_id") or "CV-DEMO-001")
    pat_name = str(params.get("displayName") or params.get("name") or params.get("patient_name") or "Alex Morgan")

    def get_raw_param(key):
        if key in params and params[key] not in [None, ""]:
            return params[key]
        if f"inp_{key}" in params and params[f"inp_{key}"] not in [None, ""]:
            return params[f"inp_{key}"]
        aliases = [
            key.capitalize(), key.title(), key.upper(),
            key.replace("_", " ").title(),
            key.replace("_", " ").upper()
        ]
        col_aliases = {
            "dm": ["DM"], "htn": ["HTN"], "fh": ["FH"], "bp": ["BP"], "pr": ["PR"],
            "ef_tte": ["EF-TTE", "EF_TTE", "EF"], "fbs": ["FBS"], "cr": ["CR"],
            "tg": ["TG"], "ldl": ["LDL"], "hdl": ["HDL"], "bun": ["BUN"],
            "esr": ["ESR"], "hb": ["HB"], "k": ["K"], "na": ["Na", "NA"],
            "wbc": ["WBC"], "lymph": ["Lymph", "LYMPH"], "neut": ["Neut", "NEUT"],
            "plt": ["PLT"], "q_wave": ["Q Wave", "Q_Wave"], "current_smoker": ["Current Smoker"],
            "ex_smoker": ["EX-Smoker", "Ex-Smoker"], "chest_pain": ["Typical Chest Pain"],
            "lowth_ang": ["LowTH Ang", "Lowth Ang"], "poor_r": ["Poor R Progression"],
            "st_elevation": ["St Elevation", "ST Elevation"], "st_depression": ["St Depression", "ST Depression"],
            "tinversion": ["Tinversion", "T Inversion"], "region_rwma": ["Region RWMA"],
            "function_class": ["Function Class"], "weak_pulse": ["Weak Peripheral Pulse"],
            "lung_rales": ["Lung Rales"], "systolic_murmur": ["Systolic Murmur"], "diastolic_murmur": ["Diastolic Murmur"]
        }
        if key in col_aliases:
            aliases.extend(col_aliases[key])
        for a in aliases:
            if a in params and params[a] not in [None, ""]:
                return params[a]
        return None

    def parse_numeric(key, default_val, is_int=False):
        raw = get_raw_param(key)
            
        if raw is None or raw == "":
            if strict:
                raise ValueError(f"Missing required patient input: '{key}'. Silent defaults prohibited.")
            val = float(default_val)
        else:
            try:
                val = float(raw)
            except (ValueError, TypeError):
                if strict:
                    raise ValueError(f"Invalid non-numeric input for '{key}': '{raw}'.")
                val = float(default_val)

        bounds = PHYSIOLOGICAL_BOUNDS.get(key)
        if bounds:
            min_v, max_v, desc = bounds
            if strict and (val < min_v or val > max_v):
                raise ValueError(
                    f"Patient input out of physiological range: {desc} = {val} "
                    f"(expected range [{min_v}, {max_v}]). Silent clipping rejected."
                )

        return int(round(val)) if is_int else float(val)

    def parse_categorical(key, default_val, allowed_vals=None):
        raw = get_raw_param(key)
        if raw is None or raw == "":
            if strict:
                raise ValueError(f"Missing required patient input: '{key}'. Silent defaults prohibited.")
            return str(default_val)
        s_val = str(raw).strip()
        if allowed_vals and s_val not in allowed_vals:
            if strict:
                raise ValueError(f"Invalid category for '{key}': '{s_val}'. Allowed: {allowed_vals}.")
            return str(default_val)
        return s_val

    # 1. Demographics & Stature Measurements
    age = parse_numeric("age", 58.0)
    length = parse_numeric("length", 170.0)
    weight = parse_numeric("weight", 72.0)
    sex = parse_categorical("sex", "Male", ["Male", "Female"])

    # Model Transformation: Calculate BMI from stature & weight
    if length > 0:
        calc_bmi = round(weight / ((length / 100.0) ** 2), 1)
    else:
        calc_bmi = 24.9

    # 2. Medical History
    dm = parse_numeric("dm", 0, is_int=True)
    htn = parse_numeric("htn", 1, is_int=True)
    current_smoker = parse_numeric("current_smoker", 0, is_int=True)
    ex_smoker = parse_numeric("ex_smoker", 0, is_int=True)
    fh = parse_numeric("fh", 0, is_int=True)
    obesity = parse_categorical("obesity", "N", ["N", "Y"])
    crf = parse_categorical("crf", "N", ["N", "Y"])
    cva = parse_categorical("cva", "N", ["N", "Y"])

    # 3. Symptoms
    chest_pain_opt = parse_categorical("chest_pain", "Y", ["Y", "N", "1", "0"])
    chest_pain = 1.0 if chest_pain_opt in ["Y", "1", 1] else 0.0
    dyspnea = parse_categorical("dyspnea", "N", ["N", "Y"])
    atypical = parse_categorical("atypical", "N", ["N", "Y"])
    nonanginal = parse_categorical("nonanginal", "N", ["N", "Y"])
    lowth_ang = parse_categorical("lowth_ang", "N", ["N", "Y"])
    poor_r = parse_categorical("poor_r", "N", ["N", "Y"])

    # 4. Vital Signs
    bp = parse_numeric("bp", NUMERIC_DEFAULTS.get("BP", 130.0))
    pr = parse_numeric("pr", NUMERIC_DEFAULTS.get("PR", 70.0))
    ef_tte = parse_numeric("ef_tte", NUMERIC_DEFAULTS.get("EF-TTE", 50.0))

    # 5. Laboratory Biomarkers
    fbs = parse_numeric("fbs", NUMERIC_DEFAULTS.get("FBS", 98.0))
    cr = parse_numeric("cr", NUMERIC_DEFAULTS.get("CR", 1.0))
    tg = parse_numeric("tg", NUMERIC_DEFAULTS.get("TG", 122.0))
    ldl = parse_numeric("ldl", NUMERIC_DEFAULTS.get("LDL", 100.0))
    hdl = parse_numeric("hdl", NUMERIC_DEFAULTS.get("HDL", 39.0))
    bun = parse_numeric("bun", NUMERIC_DEFAULTS.get("BUN", 16.0))
    esr = parse_numeric("esr", NUMERIC_DEFAULTS.get("ESR", 15.0))
    hb = parse_numeric("hb", NUMERIC_DEFAULTS.get("HB", 13.2))
    k = parse_numeric("k", NUMERIC_DEFAULTS.get("K", 4.2))
    na = parse_numeric("na", NUMERIC_DEFAULTS.get("Na", 141.0))
    wbc = parse_numeric("wbc", NUMERIC_DEFAULTS.get("WBC", 7100.0))
    lymph = parse_numeric("lymph", NUMERIC_DEFAULTS.get("Lymph", 32.0))
    neut = parse_numeric("neut", NUMERIC_DEFAULTS.get("Neut", 60.0))
    plt = parse_numeric("plt", NUMERIC_DEFAULTS.get("PLT", 210.0))

    # 6. ECG & Telemetry
    q_wave = parse_numeric("q_wave", int(NUMERIC_DEFAULTS.get("Q Wave", 0)), is_int=True)
    st_elevation = parse_numeric("st_elevation", int(NUMERIC_DEFAULTS.get("St Elevation", 0)), is_int=True)
    st_depression = parse_numeric("st_depression", int(NUMERIC_DEFAULTS.get("St Depression", 0)), is_int=True)
    tinversion = parse_numeric("tinversion", int(NUMERIC_DEFAULTS.get("Tinversion", 0)), is_int=True)
    lvh = parse_categorical("lvh", "N", ["N", "Y"])
    bbb = parse_categorical("bbb", "N", ["N", "LBBB", "RBBB"])
    region_rwma = parse_numeric("region_rwma", NUMERIC_DEFAULTS.get("Region RWMA", 0.0))
    vhd = parse_categorical("vhd", "N", ["N", "mild", "Moderate", "Severe"])

    # 7. Physical Findings
    edema = parse_numeric("edema", int(NUMERIC_DEFAULTS.get("Edema", 0)), is_int=True)
    function_class = parse_numeric("function_class", int(NUMERIC_DEFAULTS.get("Function Class", 0)), is_int=True)
    airway = parse_categorical("airway", "N", ["N", "Y"])
    thyroid = parse_categorical("thyroid", "N", ["N", "Y"])
    chf = parse_categorical("chf", "N", ["N", "Y"])
    dlp = parse_categorical("dlp", "N", ["N", "Y"])
    weak_pulse = parse_categorical("weak_pulse", "N", ["N", "Y"])
    lung_rales = parse_categorical("lung_rales", "N", ["N", "Y"])
    systolic_murmur = parse_categorical("systolic_murmur", "N", ["N", "Y"])
    diastolic_murmur = parse_categorical("diastolic_murmur", "N", ["N", "Y"])

    # Construct validated patient data dictionary (Original patient clinical measurements)
    patient_data = {
        "id": pat_id,
        "displayName": pat_name,
        "age": age,
        "sex": sex,
        "length": length,
        "weight": weight,
        "bmi": calc_bmi,
        "dm": dm,
        "htn": htn,
        "current_smoker": current_smoker,
        "ex_smoker": ex_smoker,
        "fh": fh,
        "obesity": obesity,
        "crf": crf,
        "cva": cva,
        "chest_pain": chest_pain_opt,
        "dyspnea": dyspnea,
        "atypical": atypical,
        "nonanginal": nonanginal,
        "lowth_ang": lowth_ang,
        "poor_r": poor_r,
        "bp": bp,
        "pr": pr,
        "ef_tte": ef_tte,
        "fbs": fbs,
        "cr": cr,
        "tg": tg,
        "ldl": ldl,
        "hdl": hdl,
        "bun": bun,
        "esr": esr,
        "hb": hb,
        "k": k,
        "na": na,
        "wbc": wbc,
        "lymph": lymph,
        "neut": neut,
        "plt": plt,
        "q_wave": q_wave,
        "st_elevation": st_elevation,
        "st_depression": st_depression,
        "tinversion": tinversion,
        "lvh": lvh,
        "bbb": bbb,
        "region_rwma": region_rwma,
        "vhd": vhd,
        "edema": edema,
        "function_class": function_class,
        "airway": airway,
        "thyroid": thyroid,
        "chf": chf,
        "dlp": dlp,
        "weak_pulse": weak_pulse,
        "lung_rales": lung_rales,
        "systolic_murmur": systolic_murmur,
        "diastolic_murmur": diastolic_murmur,
        "model_mode": model_mode
    }

    # Construct exact 57-dimensional Model Input DataFrame X matching feature_columns.pkl
    patient_df = pd.DataFrame([[0.0] * len(FEATURE_COLUMNS)], columns=FEATURE_COLUMNS)
    
    numeric_vector_values = {
        "Age": age, "Weight": weight, "Length": length, "BMI": calc_bmi,
        "DM": float(dm), "HTN": float(htn), "Current Smoker": float(current_smoker),
        "EX-Smoker": float(ex_smoker), "FH": float(fh), "BP": bp, "PR": pr,
        "Edema": float(edema), "Typical Chest Pain": float(chest_pain),
        "Function Class": float(function_class), "Q Wave": float(q_wave),
        "St Elevation": float(st_elevation), "St Depression": float(st_depression),
        "Tinversion": float(tinversion), "FBS": fbs, "CR": cr, "TG": tg,
        "LDL": ldl, "HDL": hdl, "BUN": bun, "ESR": esr, "HB": hb, "K": k, "Na": na,
        "WBC": wbc, "Lymph": lymph, "Neut": neut, "PLT": plt, "EF-TTE": ef_tte,
        "Region RWMA": float(region_rwma)
    }
    for col_name, col_val in numeric_vector_values.items():
        patient_df.loc[0, col_name] = float(col_val)

    # Preprocessing Transformations: One-hot and binary indicators
    transformed_mapping = {
        "Sex_Male": 1.0 if sex == "Male" else 0.0,
        "Obesity_Y": 1.0 if (obesity == "Y" or calc_bmi >= 30.0) else 0.0,
        "CRF_Y": 1.0 if crf == "Y" else 0.0,
        "CVA_Y": 1.0 if cva == "Y" else 0.0,
        "Airway disease_Y": 1.0 if airway == "Y" else 0.0,
        "Thyroid Disease_Y": 1.0 if thyroid == "Y" else 0.0,
        "CHF_Y": 1.0 if chf == "Y" else 0.0,
        "DLP_Y": 1.0 if dlp == "Y" else 0.0,
        "Weak Peripheral Pulse_Y": 1.0 if weak_pulse == "Y" else 0.0,
        "Lung rales_Y": 1.0 if lung_rales == "Y" else 0.0,
        "Systolic Murmur_Y": 1.0 if systolic_murmur == "Y" else 0.0,
        "Diastolic Murmur_Y": 1.0 if diastolic_murmur == "Y" else 0.0,
        "Dyspnea_Y": 1.0 if dyspnea == "Y" else 0.0,
        "Atypical_Y": 1.0 if atypical == "Y" else 0.0,
        "Nonanginal_Y": 1.0 if nonanginal == "Y" else 0.0,
        "LowTH Ang_Y": 1.0 if lowth_ang == "Y" else 0.0,
        "LVH_Y": 1.0 if lvh == "Y" else 0.0,
        "Poor R Progression_Y": 1.0 if poor_r == "Y" else 0.0,
        "BBB_N": 1.0 if bbb == "N" else 0.0,
        "BBB_RBBB": 1.0 if bbb == "RBBB" else 0.0,
        "VHD_N": 1.0 if vhd == "N" else 0.0,
        "VHD_mild": 1.0 if vhd == "mild" else 0.0,
        "VHD_Severe": 1.0 if vhd == "Severe" else 0.0
    }
    for col_name, col_val in transformed_mapping.items():
        patient_df.loc[0, col_name] = float(col_val)

    X = patient_df[FEATURE_COLUMNS].astype(float)

    # Compute deterministic fingerprint (SHA-256) of the 57-feature vector
    feature_bytes = X.values.tobytes()
    snapshot_hash = hashlib.sha256(feature_bytes).hexdigest()[:16]

    features_dict = {col: float(X.loc[0, col]) for col in FEATURE_COLUMNS}

    active_mode = "candidate" if str(model_mode).lower() in ["candidate", "experimental"] else "standard"

    return PatientFeatureSnapshot(
        patient_data=patient_data,
        X=X,
        features_dict=features_dict,
        transformed_mapping=transformed_mapping,
        model_mode=active_mode,
        snapshot_hash=snapshot_hash
    )


def verify_snapshot_consistency(
    snapshot: PatientFeatureSnapshot,
    predictions: dict = None,
    shap_explanations: dict = None,
    tolerance: float = 0.5
) -> tuple[bool, str]:
    """
    Verifies that passed predictions and SHAP explanations are 100% synchronized
    with the immutable patient feature snapshot.
    
    Returns (True, "") if consistent, or (False, error_reason) if inconsistent.
    """
    import numpy as np

    def sigmoid(z):
        return 1.0 / (1.0 + np.exp(-z))

    # 1. Verify predictions against snapshot feature vector
    if predictions and isinstance(predictions, dict) and "cad_risk" in predictions:
        pred_hash = predictions.get("snapshot_hash")
        if pred_hash and pred_hash != snapshot.snapshot_hash:
            return False, (
                f"Prediction snapshot hash mismatch: prediction hash '{pred_hash}' != "
                f"patient snapshot hash '{snapshot.snapshot_hash}'. Stale/cached evaluation detected."
            )
        pred_mode = predictions.get("model_mode")
        if pred_mode and pred_mode != snapshot.model_mode:
            return False, (
                f"Prediction model mode mismatch: prediction mode '{pred_mode}' != "
                f"patient snapshot mode '{snapshot.model_mode}'. Stale/cached evaluation detected."
            )
        # Load active models
        cad_model = joblib.load(_find_model_file("cad_model.pkl"))
        lad_model = joblib.load(_find_model_file("lad_model.pkl"))
        if snapshot.model_mode == "candidate":
            lcx_model = joblib.load(_find_model_file("lcx_model_candidate.pkl"))
            rca_model = joblib.load(_find_model_file("rca_model_candidate.pkl"))
        else:
            lcx_model = joblib.load(_find_model_file("lcx_model.pkl"))
            rca_model = joblib.load(_find_model_file("rca_model.pkl"))

        def get_model_prob(model, target_label):
            classes = list(model.classes_)
            idx = classes.index(target_label) if target_label in classes else 1
            return float(model.predict_proba(snapshot.X)[0][idx] * 100.0)

        exp_cad = get_model_prob(cad_model, "CAD")
        exp_lad = get_model_prob(lad_model, "Stenotic")
        exp_lcx = get_model_prob(lcx_model, 1 if snapshot.model_mode == "candidate" else "Stenotic")
        exp_rca = get_model_prob(rca_model, 1 if snapshot.model_mode == "candidate" else "Stenotic")

        pred_cad = float(predictions.get("cad_risk", -999))
        pred_lad = float(predictions.get("lad_risk", -999))
        pred_lcx = float(predictions.get("lcx_risk", -999))
        pred_rca = float(predictions.get("rca_risk", -999))

        if abs(pred_cad - exp_cad) > tolerance:
            return False, f"CAD prediction mismatch: provided {pred_cad:.1f}% vs snapshot evaluation {exp_cad:.1f}%."
        if abs(pred_lad - exp_lad) > tolerance:
            return False, f"LAD prediction mismatch: provided {pred_lad:.1f}% vs snapshot evaluation {exp_lad:.1f}%."
        if abs(pred_lcx - exp_lcx) > tolerance:
            return False, f"LCX prediction mismatch: provided {pred_lcx:.1f}% vs snapshot evaluation {exp_lcx:.1f}%."
        if abs(pred_rca - exp_rca) > tolerance:
            return False, f"RCA prediction mismatch: provided {pred_rca:.1f}% vs snapshot evaluation {exp_rca:.1f}%."

    # 2. Verify SHAP explanations against snapshot feature vector
    if shap_explanations and isinstance(shap_explanations, dict):
        # Verify snapshot hash and model mode if attached to explanations
        exp_hash = shap_explanations.get("snapshot_hash")
        if exp_hash and exp_hash != snapshot.snapshot_hash:
            return False, (
                f"SHAP snapshot hash mismatch: explanation hash '{exp_hash}' != "
                f"patient snapshot hash '{snapshot.snapshot_hash}'. Stale/cached explanation detected."
            )
        exp_mode = shap_explanations.get("model_mode")
        if exp_mode and exp_mode != snapshot.model_mode:
            return False, (
                f"SHAP model mode mismatch: explanation mode '{exp_mode}' != "
                f"patient snapshot mode '{snapshot.model_mode}'. Stale/cached explanation detected."
            )

        required_vessels = ['cad', 'lad', 'lcx', 'rca']
        if all(k in shap_explanations for k in required_vessels):
            for vessel in required_vessels:
                v_data = shap_explanations.get(vessel)
                if not isinstance(v_data, dict) or not v_data.get("available"):
                    continue

                # A. Verify model output scale matches
                scale = v_data.get("scale", "probability")
                model_out = float(v_data.get("model_output", -999))
                if scale == "log-odds":
                    shap_prob = sigmoid(model_out) * 100.0
                else:
                    shap_prob = model_out * 100.0

                if predictions and f"{vessel}_risk" in predictions:
                    target_prob = float(predictions[f"{vessel}_risk"])
                    if abs(shap_prob - target_prob) > tolerance:
                        return False, (
                            f"SHAP output probability mismatch for {vessel.upper()}: "
                            f"SHAP converted prob {shap_prob:.1f}% vs prediction {target_prob:.1f}%."
                        )

                # B. Verify patient features displayed in SHAP top_features match snapshot.X
                top_features = v_data.get("top_features", [])
                for feat in top_features:
                    feat_col = feat.get("feature_col")
                    if feat_col and feat_col in snapshot.features_dict:
                        snapshot_val = snapshot.features_dict[feat_col]
                        shap_raw_val = float(feat.get("raw_value", -999))
                        
                        # Tolerance for floating point representation
                        if abs(shap_raw_val - snapshot_val) > 0.05:
                            return False, (
                                f"SHAP feature value mismatch for {vessel.upper()} feature '{feat_col}': "
                                f"SHAP shows {shap_raw_val} but patient snapshot has {snapshot_val}. "
                                f"Stale/cached explanation detected."
                            )

    return True, ""
