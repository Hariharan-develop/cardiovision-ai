import joblib
import pandas as pd

cad_model = joblib.load("cad_model.pkl")
lad_model = joblib.load("lad_model.pkl")
lcx_model = joblib.load("lcx_model.pkl")
rca_model = joblib.load("rca_model.pkl")
feature_columns = joblib.load("feature_columns.pkl")
numeric_defaults = joblib.load("numeric_defaults.pkl")

def predict_patient(params):
    def get_num(k, default, min_v=None, max_v=None):
        val = float(params.get(k, default))
        if min_v is not None: val = max(float(min_v), val)
        if max_v is not None: val = min(float(max_v), val)
        return val

    def get_int(k, default, min_v=None, max_v=None):
        val = int(float(params.get(k, default)))
        if min_v is not None: val = max(int(min_v), val)
        if max_v is not None: val = min(int(max_v), val)
        return val

    def get_str(k, default, allowed=None):
        val = str(params.get(k, default))
        if allowed and val not in allowed: val = str(default)
        return val

    age = get_num("age", 58.0, 1.0, 120.0)
    length = get_num("length", 170.0, 50.0, 250.0)
    weight = get_num("weight", 72.0, 20.0, 300.0)
    calc_bmi = round(weight / ((length / 100.0) ** 2), 1)
    sex = get_str("sex", "Male", ["Male", "Female"])

    dm = get_int("dm", 0, 0, 1)
    htn = get_int("htn", 1, 0, 1)
    current_smoker = get_int("current_smoker", 0, 0, 1)
    ex_smoker = get_int("ex_smoker", 0, 0, 1)
    fh = get_int("fh", 0, 0, 1)
    obesity = get_str("obesity", "N", ["N", "Y"])
    crf = get_str("crf", "N", ["N", "Y"])
    cva = get_str("cva", "N", ["N", "Y"])

    chest_pain_opt = get_str("chest_pain", "Y", ["Y", "N"])
    chest_pain = 1.0 if chest_pain_opt == "Y" else 0.0
    dyspnea = get_str("dyspnea", "N", ["N", "Y"])
    atypical = get_str("atypical", "N", ["N", "Y"])
    nonanginal = get_str("nonanginal", "N", ["N", "Y"])
    lowth_ang = get_str("lowth_ang", "N", ["N", "Y"])
    poor_r = get_str("poor_r", "N", ["N", "Y"])

    bp = get_num("bp", numeric_defaults["BP"], 50.0, 260.0)
    pr = get_num("pr", numeric_defaults["PR"], 30.0, 220.0)
    ef_tte = get_num("ef_tte", numeric_defaults["EF-TTE"], 10.0, 85.0)

    fbs = get_num("fbs", numeric_defaults["FBS"], 40.0, 600.0)
    cr = get_num("cr", numeric_defaults["CR"], 0.1, 15.0)
    tg = get_num("tg", numeric_defaults["TG"], 20.0, 1000.0)
    ldl = get_num("ldl", numeric_defaults["LDL"], 10.0, 500.0)
    hdl = get_num("hdl", numeric_defaults["HDL"], 5.0, 150.0)
    bun = get_num("bun", numeric_defaults["BUN"], 1.0, 150.0)
    esr = get_num("esr", numeric_defaults["ESR"], 0.0, 150.0)
    hb = get_num("hb", numeric_defaults["HB"], 3.0, 25.0)
    k = get_num("k", numeric_defaults["K"], 1.5, 9.0)
    na = get_num("na", numeric_defaults["Na"], 100.0, 180.0)
    wbc = get_num("wbc", numeric_defaults["WBC"], 1000.0, 50000.0)
    lymph = get_num("lymph", numeric_defaults["Lymph"], 1.0, 99.0)
    neut = get_num("neut", numeric_defaults["Neut"], 1.0, 99.0)
    plt = get_num("plt", numeric_defaults["PLT"], 10.0, 1000.0)

    q_wave = get_int("q_wave", int(numeric_defaults["Q Wave"]), 0, 1)
    st_elevation = get_int("st_elevation", int(numeric_defaults["St Elevation"]), 0, 1)
    st_depression = get_int("st_depression", int(numeric_defaults["St Depression"]), 0, 1)
    tinversion = get_int("tinversion", int(numeric_defaults["Tinversion"]), 0, 1)
    lvh = get_str("lvh", "N", ["N", "Y"])
    bbb = get_str("bbb", "N", ["N", "LBBB", "RBBB"])
    region_rwma = get_num("region_rwma", numeric_defaults["Region RWMA"], 0.0, 4.0)
    vhd = get_str("vhd", "N", ["N", "mild", "Moderate", "Severe"])

    edema = get_int("edema", int(numeric_defaults["Edema"]), 0, 1)
    function_class = get_int("function_class", int(numeric_defaults["Function Class"]), 0, 4)
    airway = get_str("airway", "N", ["N", "Y"])
    thyroid = get_str("thyroid", "N", ["N", "Y"])
    chf = get_str("chf", "N", ["N", "Y"])
    dlp = get_str("dlp", "N", ["N", "Y"])
    weak_pulse = get_str("weak_pulse", "N", ["N", "Y"])
    lung_rales = get_str("lung_rales", "N", ["N", "Y"])
    systolic_murmur = get_str("systolic_murmur", "N", ["N", "Y"])
    diastolic_murmur = get_str("diastolic_murmur", "N", ["N", "Y"])

    patient = pd.DataFrame([[0.0] * len(feature_columns)], columns=feature_columns)
    numeric_values = {
        "Age": age, "Weight": weight, "Length": length, "BMI": calc_bmi,
        "DM": dm, "HTN": htn, "Current Smoker": current_smoker, "EX-Smoker": ex_smoker, "FH": fh,
        "BP": bp, "PR": pr, "Edema": edema, "Typical Chest Pain": chest_pain, "Function Class": function_class,
        "Q Wave": q_wave, "St Elevation": st_elevation, "St Depression": st_depression, "Tinversion": tinversion,
        "FBS": fbs, "CR": cr, "TG": tg, "LDL": ldl, "HDL": hdl, "BUN": bun, "ESR": esr, "HB": hb, "K": k, "Na": na,
        "WBC": wbc, "Lymph": lymph, "Neut": neut, "PLT": plt, "EF-TTE": ef_tte, "Region RWMA": region_rwma,
    }
    for col, value in numeric_values.items():
        patient.loc[0, col] = float(value)

    patient.loc[0, "Sex_Male"] = 1.0 if sex == "Male" else 0.0
    patient.loc[0, "Obesity_Y"] = 1.0 if obesity == "Y" else 0.0
    patient.loc[0, "CRF_Y"] = 1.0 if crf == "Y" else 0.0
    patient.loc[0, "CVA_Y"] = 1.0 if cva == "Y" else 0.0
    patient.loc[0, "Airway disease_Y"] = 1.0 if airway == "Y" else 0.0
    patient.loc[0, "Thyroid Disease_Y"] = 1.0 if thyroid == "Y" else 0.0
    patient.loc[0, "CHF_Y"] = 1.0 if chf == "Y" else 0.0
    patient.loc[0, "DLP_Y"] = 1.0 if dlp == "Y" else 0.0
    patient.loc[0, "Weak Peripheral Pulse_Y"] = 1.0 if weak_pulse == "Y" else 0.0
    patient.loc[0, "Lung rales_Y"] = 1.0 if lung_rales == "Y" else 0.0
    patient.loc[0, "Systolic Murmur_Y"] = 1.0 if systolic_murmur == "Y" else 0.0
    patient.loc[0, "Diastolic Murmur_Y"] = 1.0 if diastolic_murmur == "Y" else 0.0
    patient.loc[0, "Dyspnea_Y"] = 1.0 if dyspnea == "Y" else 0.0
    patient.loc[0, "Atypical_Y"] = 1.0 if atypical == "Y" else 0.0
    patient.loc[0, "Nonanginal_Y"] = 1.0 if nonanginal == "Y" else 0.0
    patient.loc[0, "LowTH Ang_Y"] = 1.0 if lowth_ang == "Y" else 0.0
    patient.loc[0, "LVH_Y"] = 1.0 if lvh == "Y" else 0.0
    patient.loc[0, "Poor R Progression_Y"] = 1.0 if poor_r == "Y" else 0.0
    patient.loc[0, "BBB_N"] = 1.0 if bbb == "N" else 0.0
    patient.loc[0, "BBB_RBBB"] = 1.0 if bbb == "RBBB" else 0.0
    patient.loc[0, "VHD_N"] = 1.0 if vhd == "N" else 0.0
    patient.loc[0, "VHD_mild"] = 1.0 if vhd == "mild" else 0.0
    patient.loc[0, "VHD_Severe"] = 1.0 if vhd == "Severe" else 0.0

    X = patient[feature_columns].astype(float)

    def class_prob(model, target_label):
        classes = list(model.classes_)
        idx = classes.index(target_label)
        return float(model.predict_proba(X)[0][idx] * 100.0)

    def get_tier(prob):
        if prob < 50.0: return "tierLow", "Low Est. Prob (<50%)"
        elif prob < 70.0: return "tierModerate", "Moderate Est. Prob (50–69%)"
        else: return "tierHigh", "High Est. Prob (≥70%)"

    cad_r = class_prob(cad_model, "CAD")
    cad_lbl = str(cad_model.predict(X)[0])
    lad_r = class_prob(lad_model, "Stenotic")
    lad_lbl = str(lad_model.predict(X)[0])
    lcx_r = class_prob(lcx_model, "Stenotic")
    lcx_lbl = str(lcx_model.predict(X)[0])
    rca_r = class_prob(rca_model, "Stenotic")
    rca_lbl = str(rca_model.predict(X)[0])

    cad_tc, cad_tl = get_tier(cad_r)
    lad_tc, lad_tl = get_tier(lad_r)
    lcx_tc, lcx_tl = get_tier(lcx_r)
    rca_tc, rca_tl = get_tier(rca_r)

    return {
        "cad_risk": round(cad_r, 1), "cad_pct": int(round(cad_r)), "cad_label": cad_lbl,
        "cad_tier_class": cad_tc, "cad_tier_label": cad_tl,
        "lad_risk": round(lad_r, 1), "lad_pct": int(round(lad_r)), "lad_label": lad_lbl,
        "lad_tier_class": lad_tc, "lad_tier_label": lad_tl,
        "lcx_risk": round(lcx_r, 1), "lcx_pct": int(round(lcx_r)), "lcx_label": lcx_lbl,
        "lcx_tier_class": lcx_tc, "lcx_tier_label": lcx_tl,
        "rca_risk": round(rca_r, 1), "rca_pct": int(round(rca_r)), "rca_label": rca_lbl,
        "rca_tier_class": rca_tc, "rca_tier_label": rca_tl,
        "bmi": calc_bmi
    }

baseline = predict_patient({})
print("Baseline:", baseline)
custom = predict_patient({"age": 70, "weight": 90, "dm": 1, "bp": 160})
print("Custom:", custom)
