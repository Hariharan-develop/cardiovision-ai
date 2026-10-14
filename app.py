import os
import sys
import html
import json
import socket
import joblib
import subprocess
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

try:
    from shap_service import get_all_shap_explanations
except ImportError:
    get_all_shap_explanations = None

def ensure_local_api():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', 8502)) != 0:
                script_path = os.path.join(os.path.dirname(__file__), "api_server.py")
                if os.path.exists(script_path):
                    subprocess.Popen([sys.executable, script_path], cwd=os.path.dirname(__file__))
    except Exception:
        pass

ensure_local_api()

# -----------------------------------------------------------------------------
# 1. Page Configuration (Wide Layout, Collapsed Default Sidebar) - Report Footer Aligned
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CardioVision AI - Cardiovascular Risk Prediction",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# 2. Hide Streamlit Chrome to Render Exact Pixel-Perfect Fullscreen Dashboard
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    #MainMenu, header, footer, section[data-testid="stSidebar"], [data-testid="collapsedControl"],
    [data-testid="stHeader"], .stAppHeader, [data-testid="stDecoration"], [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        min-height: 0 !important;
        max-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    .stHtml {
        display: none !important;
        height: 0 !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        visibility: hidden !important;
    }
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"], .main, .block-container {
        padding: 0 !important;
        padding-top: 0 !important;
        margin: 0 !important;
        margin-top: 0 !important;
        max-width: 100% !important;
        width: 100vw !important;
        height: 100vh !important;
        max-height: 100vh !important;
        overflow: hidden !important;
        top: 0 !important;
    }
    iframe {
        border: none !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        max-height: 100vh !important;
        margin: 0 !important;
        padding: 0 !important;
        display: block !important;
        z-index: 999999 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.html(
    """
    <script>
    (function() {
        // Immediately clean address bar if any patient parameters exist in URL
        if (window.location.search) {
            try {
                window.history.replaceState({}, document.title, window.location.pathname);
            } catch(e) {}
        }

        function doNavigate(search) {
            if (!search) return;
            var s = search.startsWith('?') ? search : ('?' + search);
            window.location.href = window.location.pathname + s;
        }
        function doReset() {
            if (window.location.search) {
                window.location.search = '';
            } else {
                window.location.href = window.location.origin + window.location.pathname;
            }
        }

        window.cardiovisionNavigate = function(search) {
            setTimeout(function() { doNavigate(search); }, 10);
        };
        window.cardiovisionReset = function() {
            setTimeout(function() { doReset(); }, 10);
        };

        if (!window.__cardiovision_bridge_active) {
            window.__cardiovision_bridge_active = true;
            window.addEventListener('message', function(ev) {
                if (!ev || !ev.data || typeof ev.data !== 'object') return;
                if (ev.data.type === 'cardiovision_navigate' && ev.data.search) {
                    doNavigate(ev.data.search);
                } else if (ev.data.type === 'cardiovision_reset') {
                    doReset();
                }
            });
        }
    })();
    </script>
    """,
    unsafe_allow_javascript=True,
)


# -----------------------------------------------------------------------------
# 3. Load Trained Machine Learning Models & Feature Metadata
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

def get_model_path(fname):
    for d in [MODELS_DIR, BASE_DIR]:
        p = os.path.join(d, fname)
        if os.path.exists(p):
            return p
    return os.path.join(MODELS_DIR, fname)

cad_model = joblib.load(get_model_path("cad_model.pkl"))
lad_model = joblib.load(get_model_path("lad_model.pkl"))
lcx_model = joblib.load(get_model_path("lcx_model.pkl"))
rca_model = joblib.load(get_model_path("rca_model.pkl"))

# Candidate models (experimental mode) and calibrated thresholds
lcx_model_candidate = joblib.load(get_model_path("lcx_model_candidate.pkl"))
rca_model_candidate = joblib.load(get_model_path("rca_model_candidate.pkl"))

candidate_thresholds = {"LCX": 0.45, "RCA": 0.40}
cand_thresh_file = get_model_path("candidate_thresholds.json")
if os.path.exists(cand_thresh_file):
    try:
        with open(cand_thresh_file, "r", encoding="utf-8") as _cf:
            candidate_thresholds = json.load(_cf)
    except Exception:
        pass

CANDIDATE_LCX_THRESH = float(candidate_thresholds.get("LCX", 0.45))
CANDIDATE_RCA_THRESH = float(candidate_thresholds.get("RCA", 0.40))
CANDIDATE_LCX_THRESH_PCT = f"{CANDIDATE_LCX_THRESH * 100.0:.1f}"
CANDIDATE_RCA_THRESH_PCT = f"{CANDIDATE_RCA_THRESH * 100.0:.1f}"

feature_columns = joblib.load(get_model_path("feature_columns.pkl"))
numeric_defaults = joblib.load(get_model_path("numeric_defaults.pkl"))

# -----------------------------------------------------------------------------
# 4. Extract Query Parameters (Interactive Form Sync from Dashboard UI)
# -----------------------------------------------------------------------------
params = st.query_params
if len(st.query_params) > 0:
    st.query_params.clear()

def parse_float(key, default, min_v=None, max_v=None):
    raw = params.get(key)
    if raw is None or raw == "":
        val = float(default)
    else:
        try:
            val = float(raw)
        except (ValueError, TypeError):
            val = float(default)
    if min_v is not None:
        val = max(float(min_v), val)
    if max_v is not None:
        val = min(float(max_v), val)
    return val

def parse_int(key, default, min_v=None, max_v=None):
    raw = params.get(key)
    if raw is None or raw == "":
        val = int(default)
    else:
        try:
            val = int(float(raw))
        except (ValueError, TypeError):
            val = int(default)
    if min_v is not None:
        val = max(int(min_v), val)
    if max_v is not None:
        val = min(int(max_v), val)
    return val

def parse_str(key, default, allowed=None):
    raw = params.get(key)
    if raw is None or raw == "":
        val = str(default)
    else:
        val = str(raw)
    if allowed and val not in allowed:
        val = str(default)
    return val

# Configurable Model Mode: Standard (Production) vs Experimental (Candidate LCX/RCA)
model_mode = parse_str("model_mode", "standard", allowed=["standard", "candidate", "experimental"])
is_candidate_mode = model_mode in ["candidate", "experimental"] or parse_str("experimental", "0", allowed=["0", "1", "true", "false"]) in ["1", "true"]

# Basic Information (with physiological bounds validation)
age = parse_float("age", 58.0, min_v=1.0, max_v=120.0)
length = parse_float("length", 170.0, min_v=50.0, max_v=250.0)
weight = parse_float("weight", 72.0, min_v=20.0, max_v=300.0)
calc_bmi = round(weight / ((length / 100.0) ** 2), 1)
sex = parse_str("sex", "Male", allowed=["Male", "Female"])

# Medical History
dm = parse_int("dm", 0, min_v=0, max_v=1)
htn = parse_int("htn", 1, min_v=0, max_v=1)
current_smoker = parse_int("current_smoker", 0, min_v=0, max_v=1)
ex_smoker = parse_int("ex_smoker", 0, min_v=0, max_v=1)
fh = parse_int("fh", 0, min_v=0, max_v=1)
obesity = parse_str("obesity", "N", allowed=["N", "Y"])
crf = parse_str("crf", "N", allowed=["N", "Y"])
cva = parse_str("cva", "N", allowed=["N", "Y"])

# Symptoms
chest_pain_opt = parse_str("chest_pain", "Y", allowed=["Y", "N"])
chest_pain = 1.0 if chest_pain_opt == "Y" else 0.0
dyspnea = parse_str("dyspnea", "N", allowed=["N", "Y"])
atypical = parse_str("atypical", "N", allowed=["N", "Y"])
nonanginal = parse_str("nonanginal", "N", allowed=["N", "Y"])
lowth_ang = parse_str("lowth_ang", "N", allowed=["N", "Y"])
poor_r = parse_str("poor_r", "N", allowed=["N", "Y"])

# Vital Signs
bp = parse_float("bp", numeric_defaults["BP"], min_v=50.0, max_v=260.0)
pr = parse_float("pr", numeric_defaults["PR"], min_v=30.0, max_v=220.0)
ef_tte = parse_float("ef_tte", numeric_defaults["EF-TTE"], min_v=10.0, max_v=85.0)

# Laboratory Biomarkers
fbs = parse_float("fbs", numeric_defaults["FBS"], min_v=40.0, max_v=600.0)
cr = parse_float("cr", numeric_defaults["CR"], min_v=0.1, max_v=15.0)
tg = parse_float("tg", numeric_defaults["TG"], min_v=20.0, max_v=1000.0)
ldl = parse_float("ldl", numeric_defaults["LDL"], min_v=10.0, max_v=500.0)
hdl = parse_float("hdl", numeric_defaults["HDL"], min_v=5.0, max_v=150.0)
bun = parse_float("bun", numeric_defaults["BUN"], min_v=1.0, max_v=150.0)
esr = parse_float("esr", numeric_defaults["ESR"], min_v=0.0, max_v=150.0)
hb = parse_float("hb", numeric_defaults["HB"], min_v=3.0, max_v=25.0)
k = parse_float("k", numeric_defaults["K"], min_v=1.5, max_v=9.0)
na = parse_float("na", numeric_defaults["Na"], min_v=100.0, max_v=180.0)
wbc = parse_float("wbc", numeric_defaults["WBC"], min_v=1000.0, max_v=50000.0)
lymph = parse_float("lymph", numeric_defaults["Lymph"], min_v=1.0, max_v=99.0)
neut = parse_float("neut", numeric_defaults["Neut"], min_v=1.0, max_v=99.0)
plt = parse_float("plt", numeric_defaults["PLT"], min_v=10.0, max_v=1000.0)

# ECG & Cardiac Telemetry
q_wave = parse_int("q_wave", int(numeric_defaults["Q Wave"]), min_v=0, max_v=1)
st_elevation = parse_int("st_elevation", int(numeric_defaults["St Elevation"]), min_v=0, max_v=1)
st_depression = parse_int("st_depression", int(numeric_defaults["St Depression"]), min_v=0, max_v=1)
tinversion = parse_int("tinversion", int(numeric_defaults["Tinversion"]), min_v=0, max_v=1)
lvh = parse_str("lvh", "N", allowed=["N", "Y"])
bbb = parse_str("bbb", "N", allowed=["N", "LBBB", "RBBB"])
region_rwma = parse_float("region_rwma", numeric_defaults["Region RWMA"], min_v=0.0, max_v=4.0)
vhd = parse_str("vhd", "N", allowed=["N", "mild", "Moderate", "Severe"])

# Additional Clinical Findings
edema = parse_int("edema", int(numeric_defaults["Edema"]), min_v=0, max_v=1)
function_class = parse_int("function_class", int(numeric_defaults["Function Class"]), min_v=0, max_v=4)
airway = parse_str("airway", "N", allowed=["N", "Y"])
thyroid = parse_str("thyroid", "N", allowed=["N", "Y"])
chf = parse_str("chf", "N", allowed=["N", "Y"])
dlp = parse_str("dlp", "N", allowed=["N", "Y"])
weak_pulse = parse_str("weak_pulse", "N", allowed=["N", "Y"])
lung_rales = parse_str("lung_rales", "N", allowed=["N", "Y"])
systolic_murmur = parse_str("systolic_murmur", "N", allowed=["N", "Y"])
diastolic_murmur = parse_str("diastolic_murmur", "N", allowed=["N", "Y"])

# -----------------------------------------------------------------------------
# 5. Build 57-Dimensional Patient Vector
# -----------------------------------------------------------------------------
def create_model_input():
    patient = pd.DataFrame([[0.0] * len(feature_columns)], columns=feature_columns)

    numeric_values = {
        "Age": age,
        "Weight": weight,
        "Length": length,
        "BMI": calc_bmi,
        "DM": dm,
        "HTN": htn,
        "Current Smoker": current_smoker,
        "EX-Smoker": ex_smoker,
        "FH": fh,
        "BP": bp,
        "PR": pr,
        "Edema": edema,
        "Typical Chest Pain": chest_pain,
        "Function Class": function_class,
        "Q Wave": q_wave,
        "St Elevation": st_elevation,
        "St Depression": st_depression,
        "Tinversion": tinversion,
        "FBS": fbs,
        "CR": cr,
        "TG": tg,
        "LDL": ldl,
        "HDL": hdl,
        "BUN": bun,
        "ESR": esr,
        "HB": hb,
        "K": k,
        "Na": na,
        "WBC": wbc,
        "Lymph": lymph,
        "Neut": neut,
        "PLT": plt,
        "EF-TTE": ef_tte,
        "Region RWMA": region_rwma,
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

    return patient[feature_columns].astype(float)

patient_input = create_model_input()

# -----------------------------------------------------------------------------
# 6. Four-Model Risk Predictions (Verified Directly Against .pkl Models)
# -----------------------------------------------------------------------------
def class_probability(model, X, target_label):
    classes = list(model.classes_)
    idx = classes.index(target_label)
    prob_array = model.predict_proba(X)[0]
    return float(prob_array[idx] * 100.0)

# True predictions evaluated strictly from the loaded models - never hardcoded!
# 1. Preserve the original CAD and LAD models
cad_risk = class_probability(cad_model, patient_input, "CAD")
cad_label = str(cad_model.predict(patient_input)[0])

lad_risk = class_probability(lad_model, patient_input, "Stenotic")
lad_label = str(lad_model.predict(patient_input)[0])

# 2. Configurable experimental mode for LCX and RCA candidate models
if is_candidate_mode:
    # Candidate models use numeric classes: 0 = Normal, 1 = Stenotic.
    # Retrieve the probability for class 1 using model.classes_, not a hardcoded index.
    lcx_risk = class_probability(lcx_model_candidate, patient_input, 1)
    rca_risk = class_probability(rca_model_candidate, patient_input, 1)

    lcx_thresh = CANDIDATE_LCX_THRESH
    rca_thresh = CANDIDATE_RCA_THRESH

    # Apply the LCX and RCA thresholds only to Normal/Stenotic classification
    # Keep the raw predicted probabilities unchanged for the dashboard and 3D coronary risk overlay
    lcx_label = "Stenotic" if (lcx_risk / 100.0) >= lcx_thresh else "Normal"
    rca_label = "Stenotic" if (rca_risk / 100.0) >= rca_thresh else "Normal"

    lcx_model_file = "lcx_model_candidate.pkl"
    rca_model_file = "rca_model_candidate.pkl"
else:
    # Preserve the original LCX and RCA models as backups / baseline
    lcx_risk = class_probability(lcx_model, patient_input, "Stenotic")
    lcx_label = str(lcx_model.predict(patient_input)[0])

    rca_risk = class_probability(rca_model, patient_input, "Stenotic")
    rca_label = str(rca_model.predict(patient_input)[0])

    lcx_thresh = 0.5
    rca_thresh = 0.5
    lcx_model_file = "lcx_model.pkl"
    rca_model_file = "rca_model.pkl"

cad_pct = int(round(cad_risk))
lad_pct = int(round(lad_risk))
lcx_pct = int(round(lcx_risk))
rca_pct = int(round(rca_risk))

# Probability Level Indicators (Clinical visualization tiers, not diagnostic thresholds)
def get_prob_tier(prob):
    if prob < 50.0:
        return "tierLow", "Low Est. Prob (<50%)"
    elif prob < 70.0:
        return "tierModerate", "Moderate Est. Prob (50–69%)"
    else:
        return "tierHigh", "High Est. Prob (≥70%)"

cad_tier_class, cad_tier_label = get_prob_tier(cad_risk)
lad_tier_class, lad_tier_label = get_prob_tier(lad_risk)
lcx_tier_class, lcx_tier_label = get_prob_tier(lcx_risk)
rca_tier_class, rca_tier_label = get_prob_tier(rca_risk)

has_custom_inputs = len(params) > 0

# Compute patient-specific SHAP explanations
active_lcx_model = lcx_model_candidate if is_candidate_mode else lcx_model
active_rca_model = rca_model_candidate if is_candidate_mode else rca_model

shap_data = {}
if get_all_shap_explanations is not None:
    try:
        shap_data = get_all_shap_explanations(
            cad_model, lad_model, active_lcx_model, active_rca_model, patient_input, is_candidate=is_candidate_mode
        )
    except Exception as _e:
        shap_data = {"error": str(_e), "available": False}

# Experimental vs Standard performance table values
if is_candidate_mode:
    perf_table_subtitle = "Exploratory nested threshold cross-validation — not independent external clinical validation."
    perf_caution_text = "<b>Candidate Cross-Validation Notice:</b> LCX and RCA candidate models report exploratory nested threshold cross-validation metrics (LCX Macro F1: 0.689, Stenotic Recall: 0.597, Precision: 0.634, Balanced Accuracy: 0.687; RCA Macro F1: 0.651, Stenotic Recall: 0.632, Precision: 0.545, Balanced Accuracy: 0.657). Accuracy and ROC-AUC were not evaluated. These are exploratory findings, not independent external clinical validation."
    lcx_perf_acc = "<i>Not evaluated</i>"
    lcx_perf_f1 = '<b>0.689</b> <span style="font-size:11px;color:#0284c7;">(Macro F1)</span>'
    lcx_perf_auc = "<i>Not evaluated</i>"
    rca_perf_acc = "<i>Not evaluated</i>"
    rca_perf_f1 = '<b>0.651</b> <span style="font-size:11px;color:#0284c7;">(Macro F1)</span>'
    rca_perf_auc = "<i>Not evaluated</i>"
else:
    perf_table_subtitle = "Previously recorded validation metrics from model development on retrospective test cohorts. Not independently verified prospective clinical trial performance."
    perf_caution_text = "<b>Model Reliability Notice:</b> LCX and RCA models have limited predictive discrimination in current validation results (ROC-AUC 0.584 and 0.652). Predictions should be interpreted cautiously and must not guide clinical care independently."
    lcx_perf_acc = "<b>57.4%</b>"
    lcx_perf_f1 = "53.6%"
    lcx_perf_auc = "0.584"
    rca_perf_acc = "<b>60.7%</b>"
    rca_perf_f1 = "50.0%"
    rca_perf_auc = "0.652"

# -----------------------------------------------------------------------------
# 7. Render 3D WebGL Coronary Viewer Content for 3D Tab
# -----------------------------------------------------------------------------
heart_viewer_path = os.path.join(os.path.dirname(__file__), "frontend", "components", "heart_viewer.html")
if not os.path.exists(heart_viewer_path):
    heart_viewer_path = os.path.join(os.path.dirname(__file__), "components", "heart_viewer.html")
if os.path.exists(heart_viewer_path):
    with open(heart_viewer_path, "r", encoding="utf-8") as _hf:
        viewer_raw = _hf.read()
    viewer_ready = (
        viewer_raw
        .replace("{{CAD_RISK}}", f"{cad_risk:.1f}")
        .replace("{{LAD_RISK}}", f"{lad_risk:.1f}")
        .replace("{{LCX_RISK}}", f"{lcx_risk:.1f}")
        .replace("{{RCA_RISK}}", f"{rca_risk:.1f}")
        .replace("{{CAD_LABEL}}", str(cad_label))
        .replace("{{LAD_LABEL}}", str(lad_label))
        .replace("{{LCX_LABEL}}", str(lcx_label))
        .replace("{{RCA_LABEL}}", str(rca_label))
        .replace("{{IS_CUSTOM_PRED}}", "true" if has_custom_inputs else "false")
    )
    viewer_srcdoc = html.escape(viewer_ready)
else:
    viewer_srcdoc = "3D Viewer File Not Found"

# -----------------------------------------------------------------------------
# 8. Load Exact UI Template & Inject Dynamic Values
# -----------------------------------------------------------------------------
template_path = os.path.join(os.path.dirname(__file__), "frontend", "cardiovision_exact_dashboard.html")
if not os.path.exists(template_path):
    template_path = os.path.join(os.path.dirname(__file__), "cardiovision_exact_dashboard.html")
with open(template_path, "r", encoding="utf-8") as _tf:
    html_page = _tf.read()

replacements = {
    # Basic Information
    "{{AGE}}": str(int(age)),
    "{{LENGTH}}": str(int(length)),
    "{{WEIGHT}}": str(int(weight)),
    "{{BMI}}": f"{calc_bmi:.1f}",
    "{{SEX_MALE_SEL}}": "selected" if sex == "Male" else "",
    "{{SEX_FEMALE_SEL}}": "selected" if sex == "Female" else "",
    "{{SEX_VAL}}": sex,

    # Medical History
    "{{DM_0_SEL}}": "selected" if dm == 0 else "",
    "{{DM_1_SEL}}": "selected" if dm == 1 else "",
    "{{DM_VAL}}": str(dm),
    "{{HTN_1_SEL}}": "selected" if htn == 1 else "",
    "{{HTN_0_SEL}}": "selected" if htn == 0 else "",
    "{{HTN_VAL}}": str(htn),
    "{{CS_0_SEL}}": "selected" if current_smoker == 0 else "",
    "{{CS_1_SEL}}": "selected" if current_smoker == 1 else "",
    "{{CS_VAL}}": str(current_smoker),
    "{{ES_0_SEL}}": "selected" if ex_smoker == 0 else "",
    "{{ES_1_SEL}}": "selected" if ex_smoker == 1 else "",
    "{{ES_VAL}}": str(ex_smoker),
    "{{FH_0_SEL}}": "selected" if fh == 0 else "",
    "{{FH_1_SEL}}": "selected" if fh == 1 else "",
    "{{OB_N_SEL}}": "selected" if obesity == "N" else "",
    "{{OB_Y_SEL}}": "selected" if obesity == "Y" else "",
    "{{CRF_N_SEL}}": "selected" if crf == "N" else "",
    "{{CRF_Y_SEL}}": "selected" if crf == "Y" else "",
    "{{CVA_N_SEL}}": "selected" if cva == "N" else "",
    "{{CVA_Y_SEL}}": "selected" if cva == "Y" else "",

    # Symptoms
    "{{CP_Y_SEL}}": "selected" if chest_pain_opt == "Y" else "",
    "{{CP_N_SEL}}": "selected" if chest_pain_opt == "N" else "",
    "{{DYS_N_SEL}}": "selected" if dyspnea == "N" else "",
    "{{DYS_Y_SEL}}": "selected" if dyspnea == "Y" else "",
    "{{ATYP_N_SEL}}": "selected" if atypical == "N" else "",
    "{{ATYP_Y_SEL}}": "selected" if atypical == "Y" else "",
    "{{NON_N_SEL}}": "selected" if nonanginal == "N" else "",
    "{{NON_Y_SEL}}": "selected" if nonanginal == "Y" else "",
    "{{LOW_N_SEL}}": "selected" if lowth_ang == "N" else "",
    "{{LOW_Y_SEL}}": "selected" if lowth_ang == "Y" else "",
    "{{PR_N_SEL}}": "selected" if poor_r == "N" else "",
    "{{PR_Y_SEL}}": "selected" if poor_r == "Y" else "",

    # Vital Signs
    "{{BP}}": f"{bp:.1f}",
    "{{PR}}": f"{pr:.1f}",
    "{{EF_TTE}}": f"{ef_tte:.1f}",

    # Laboratory Biomarkers
    "{{FBS}}": f"{fbs:.1f}",
    "{{CR}}": f"{cr:.1f}",
    "{{TG}}": f"{tg:.1f}",
    "{{LDL}}": f"{ldl:.1f}",
    "{{HDL}}": f"{hdl:.1f}",
    "{{BUN}}": f"{bun:.1f}",
    "{{ESR}}": f"{esr:.1f}",
    "{{HB}}": f"{hb:.1f}",
    "{{K}}": f"{k:.1f}",
    "{{NA}}": f"{na:.1f}",
    "{{WBC}}": f"{wbc:.1f}",
    "{{LYMPH}}": f"{lymph:.1f}",
    "{{NEUT}}": f"{neut:.1f}",
    "{{PLT}}": f"{plt:.1f}",

    # ECG & Cardiac
    "{{QW_0_SEL}}": "selected" if q_wave == 0 else "",
    "{{QW_1_SEL}}": "selected" if q_wave == 1 else "",
    "{{QW_VAL}}": str(q_wave),
    "{{STE_0_SEL}}": "selected" if st_elevation == 0 else "",
    "{{STE_1_SEL}}": "selected" if st_elevation == 1 else "",
    "{{STE_VAL}}": str(st_elevation),
    "{{STD_0_SEL}}": "selected" if st_depression == 0 else "",
    "{{STD_1_SEL}}": "selected" if st_depression == 1 else "",
    "{{STD_VAL}}": str(st_depression),
    "{{TINV_0_SEL}}": "selected" if tinversion == 0 else "",
    "{{TINV_1_SEL}}": "selected" if tinversion == 1 else "",
    "{{TINV_VAL}}": str(tinversion),
    "{{LVH_N_SEL}}": "selected" if lvh == "N" else "",
    "{{LVH_Y_SEL}}": "selected" if lvh == "Y" else "",
    "{{BBB_N_SEL}}": "selected" if bbb == "N" else "",
    "{{BBB_LBBB_SEL}}": "selected" if bbb == "LBBB" else "",
    "{{BBB_RBBB_SEL}}": "selected" if bbb == "RBBB" else "",
    "{{REGION_RWMA}}": f"{region_rwma:.1f}",
    "{{VHD_N_SEL}}": "selected" if vhd == "N" else "",
    "{{VHD_MILD_SEL}}": "selected" if vhd == "mild" else "",
    "{{VHD_MOD_SEL}}": "selected" if vhd == "Moderate" else "",
    "{{VHD_SEV_SEL}}": "selected" if vhd == "Severe" else "",

    # Additional Findings
    "{{EDEMA_0_SEL}}": "selected" if edema == 0 else "",
    "{{EDEMA_1_SEL}}": "selected" if edema == 1 else "",
    "{{FUNCTION_CLASS}}": str(function_class),
    "{{AIR_N_SEL}}": "selected" if airway == "N" else "",
    "{{AIR_Y_SEL}}": "selected" if airway == "Y" else "",
    "{{THY_N_SEL}}": "selected" if thyroid == "N" else "",
    "{{THY_Y_SEL}}": "selected" if thyroid == "Y" else "",
    "{{CHF_N_SEL}}": "selected" if chf == "N" else "",
    "{{CHF_Y_SEL}}": "selected" if chf == "Y" else "",
    "{{DLP_N_SEL}}": "selected" if dlp == "N" else "",
    "{{DLP_Y_SEL}}": "selected" if dlp == "Y" else "",
    "{{WEAK_N_SEL}}": "selected" if weak_pulse == "N" else "",
    "{{WEAK_Y_SEL}}": "selected" if weak_pulse == "Y" else "",
    "{{RALES_N_SEL}}": "selected" if lung_rales == "N" else "",
    "{{RALES_Y_SEL}}": "selected" if lung_rales == "Y" else "",
    "{{SYSMUR_N_SEL}}": "selected" if systolic_murmur == "N" else "",
    "{{SYSMUR_Y_SEL}}": "selected" if systolic_murmur == "Y" else "",
    "{{DIAMUR_N_SEL}}": "selected" if diastolic_murmur == "N" else "",
    "{{DIAMUR_Y_SEL}}": "selected" if diastolic_murmur == "Y" else "",

    # Model Risk Outputs & Donut Gauges
    "{{CAD_RISK}}": f"{cad_risk:.1f}",
    "{{LAD_RISK}}": f"{lad_risk:.1f}",
    "{{LCX_RISK}}": f"{lcx_risk:.1f}",
    "{{RCA_RISK}}": f"{rca_risk:.1f}",
    "{{CAD_PCT}}": str(cad_pct),
    "{{LAD_PCT}}": str(lad_pct),
    "{{LCX_PCT}}": str(lcx_pct),
    "{{RCA_PCT}}": str(rca_pct),
    "{{CAD_LABEL}}": cad_label,
    "{{LAD_LABEL}}": lad_label,
    "{{LCX_LABEL}}": lcx_label,
    "{{RCA_LABEL}}": rca_label,

    # 3D Viewer Iframe Source
    "{{HEART_VIEWER_SRCDOC}}": viewer_srcdoc,

    # Clinical Probability Tiers & Status
    "{{CAD_TIER_CLASS}}": cad_tier_class,
    "{{CAD_TIER_LABEL}}": cad_tier_label,
    "{{LAD_TIER_CLASS}}": lad_tier_class,
    "{{LAD_TIER_LABEL}}": lad_tier_label,
    "{{LCX_TIER_CLASS}}": lcx_tier_class,
    "{{LCX_TIER_LABEL}}": lcx_tier_label,
    "{{RCA_TIER_CLASS}}": rca_tier_class,
    "{{RCA_TIER_LABEL}}": rca_tier_label,
    "{{IS_CUSTOM_PRED}}": "true" if has_custom_inputs else "false",

    # Configurable Model Mode & Candidate Metadata
    "{{MODEL_MODE}}": "candidate" if is_candidate_mode else "standard",
    "{{IS_CANDIDATE_MODE}}": "true" if is_candidate_mode else "false",
    "{{IS_CANDIDATE_MODE_BLOCK}}": "flex" if is_candidate_mode else "none",
    "{{IS_CANDIDATE_MODE_INLINE}}": "inline-flex" if is_candidate_mode else "none",
    "{{MODE_STD_ACTIVE}}": "" if is_candidate_mode else "active",
    "{{MODE_CAND_ACTIVE}}": "active" if is_candidate_mode else "",
    "{{MODE_STATUS_DESC}}": "Experimental LCX & RCA candidates active (Research-Only)" if is_candidate_mode else "Standard baseline CAD, LAD, LCX & RCA models active",
    "{{LCX_MODEL_FILE}}": lcx_model_file,
    "{{RCA_MODEL_FILE}}": rca_model_file,
    "{{LCX_THRESH_PCT}}": CANDIDATE_LCX_THRESH_PCT,
    "{{RCA_THRESH_PCT}}": CANDIDATE_RCA_THRESH_PCT,
    "{{CANDIDATE_LCX_THRESH_PCT}}": CANDIDATE_LCX_THRESH_PCT,
    "{{CANDIDATE_RCA_THRESH_PCT}}": CANDIDATE_RCA_THRESH_PCT,
    "{{LCX_THRESH_RATIO}}": f"{CANDIDATE_LCX_THRESH:.2f}",
    "{{RCA_THRESH_RATIO}}": f"{CANDIDATE_RCA_THRESH:.2f}",
    "{{ACTIVE_LCX_THRESH_PCT}}": f"{lcx_thresh * 100.0:.1f}",
    "{{ACTIVE_RCA_THRESH_PCT}}": f"{rca_thresh * 100.0:.1f}",
    "{{MODE_LABEL}}": "Experimental Candidate Mode" if is_candidate_mode else "Standard Production Mode",

    # AI Explainability SHAP Data
    "{{SHAP_DATA_JSON}}": json.dumps(shap_data, ensure_ascii=False),

    # Model Performance & Reliability Table
    "{{PERF_TABLE_SUBTITLE}}": perf_table_subtitle,
    "{{PERF_CAUTION_TEXT}}": perf_caution_text,
    "{{LCX_PERF_ACC}}": lcx_perf_acc,
    "{{LCX_PERF_F1}}": lcx_perf_f1,
    "{{LCX_PERF_AUC}}": lcx_perf_auc,
    "{{RCA_PERF_ACC}}": rca_perf_acc,
    "{{RCA_PERF_F1}}": rca_perf_f1,
    "{{RCA_PERF_AUC}}": rca_perf_auc,
}

for k, v in replacements.items():
    clean_k = k.strip("{}")
    html_page = html_page.replace(f"{{{clean_k}}}", str(v))
    html_page = html_page.replace(f"{{{{{clean_k}}}}}", str(v))

# -----------------------------------------------------------------------------
# 9. Embed Fullscreen Dashboard in Streamlit
# -----------------------------------------------------------------------------
if hasattr(st, "iframe"):
    st.iframe(html_page, height=960, width="stretch")
else:
    components.html(html_page, height=960, scrolling=False)
# Results & Analysis screen: Final PDF Report Refinements — dynamic creatinine status, held-out evaluation terminology, optimized A4 space utilization.

# Updated 1791735015.3221169
# Sync 1791735717.0670254