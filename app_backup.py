
import streamlit as st
import pandas as pd
import joblib
import altair as alt

st.set_page_config(
    page_title="CardioVision AI",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Load trained models + metadata
# -----------------------------
cad_model = joblib.load("cad_model.pkl")
lad_model = joblib.load("lad_model.pkl")
lcx_model = joblib.load("lcx_model.pkl")
rca_model = joblib.load("rca_model.pkl")

feature_columns = joblib.load("feature_columns.pkl")
numeric_defaults = joblib.load("numeric_defaults.pkl")

# -----------------------------
# Global styling
# -----------------------------
st.markdown(
    """
    <style>
    :root{
        --navy:#10294f;
        --blue:#1976ed;
        --muted:#617492;
        --line:#dce7f4;
        --panel:#ffffff;
        --page:#f6faff;
    }

    #MainMenu {visibility:hidden;}
    footer {visibility:hidden;}
    header {visibility:hidden;}

    .stApp{
        background:
            radial-gradient(circle at 70% 0%, rgba(216,234,255,.72), transparent 31%),
            radial-gradient(circle at 98% 0%, rgba(255,223,229,.8), transparent 24%),
            var(--page);
    }

    .block-container{
        max-width: 1540px;
        padding-top: 14px;
        padding-bottom: 28px;
        padding-left: 18px;
        padding-right: 18px;
    }

    section[data-testid="stSidebar"]{
        width:235px !important;
        min-width:235px !important;
        background:linear-gradient(180deg,#f3f9ff 0%,#ffffff 100%);
        border-right:1px solid #dbe7f4;
    }

    section[data-testid="stSidebar"] > div{
        padding:18px 12px 16px 12px;
    }

    .side-brand{
        text-align:center;
        padding:2px 4px 22px;
    }
    .side-heart{
        font-size:48px;
        line-height:1;
        filter:drop-shadow(0 6px 12px rgba(255,70,85,.16));
    }
    .side-title{
        color:#112b50;
        font-size:23px;
        font-weight:850;
        margin-top:8px;
    }
    .side-title span{color:#3c72c5;}
    .side-sub{
        color:#667b9b;
        font-size:11px;
        margin-top:3px;
    }
    .side-item{
        border-radius:10px;
        padding:12px 13px;
        margin:5px 0;
        color:#496487;
        font-size:14px;
        font-weight:600;
    }
    .side-item.active{
        background:#e5f1ff;
        color:#0a72e8;
        border-left:3px solid #1681f6;
    }
    .side-note{
        margin-top:250px;
        border:1px solid #dce8f5;
        border-radius:14px;
        padding:14px;
        background:#fafdff;
        color:#536a8b;
        line-height:1.55;
        font-size:12px;
    }

    .hero-shell{
        background:
            linear-gradient(110deg,rgba(255,255,255,.95),rgba(228,241,255,.86),rgba(255,228,234,.83));
        border:1px solid #dfeaf6;
        border-radius:20px;
        box-shadow:0 8px 28px rgba(36,79,130,.06);
        padding:16px 18px 12px;
        margin-bottom:12px;
    }
    .hero-brand{
        display:flex;
        align-items:flex-start;
        gap:13px;
    }
    .hero-logo{
        width:72px;height:72px;border-radius:24px;
        display:flex;align-items:center;justify-content:center;
        font-size:42px;
        background:linear-gradient(145deg,#ff535b,#e93443);
        box-shadow:0 10px 23px rgba(238,52,67,.18);
        flex:0 0 auto;
    }
    .hero-title{
        color:#112a50;
        font-size:42px;
        font-weight:900;
        letter-spacing:-1.3px;
        line-height:1.02;
    }
    .hero-title span{color:#2c76df;}
    .hero-subtitle{
        color:#13294c;
        font-size:18px;
        font-weight:800;
        margin-top:7px;
    }
    .hero-desc{
        color:#5b7190;
        font-size:13px;
        margin-top:5px;
        line-height:1.45;
    }

    .stat-card{
        border:1px solid #d9e7f5;
        border-radius:13px;
        background:rgba(255,255,255,.78);
        padding:10px 12px;
        min-height:72px;
    }
    .stat-top{
        color:#637894;
        font-size:10px;
        text-transform:uppercase;
        letter-spacing:.45px;
    }
    .stat-value{
        color:#1675eb;
        font-size:24px;
        font-weight:850;
        line-height:1.1;
        margin-top:3px;
    }
    .stat-ok{
        color:#173457;
        font-size:13px;
        font-weight:750;
        margin-top:7px;
    }
    .stat-foot{
        color:#6b809d;
        font-size:10px;
        margin-top:1px;
    }

    .panel-title{
        color:#11294b;
        font-size:20px;
        font-weight:850;
        line-height:1.15;
    }
    .panel-sub{
        color:#6a7d98;
        font-size:11px;
        margin-top:2px;
    }

    .section-head{
        border-radius:9px 9px 0 0;
        padding:5px 10px;
        font-weight:800;
        font-size:13px;
        margin:-4px -4px 8px -4px;
    }
    .blue-head{background:#edf6ff;color:#086de2;}
    .red-head{background:#fff0f1;color:#d93645;}
    .green-head{background:#ecfaf4;color:#15945e;}
    .amber-head{background:#fff7e5;color:#b97900;}
    .purple-head{background:#f3edff;color:#723be1;}
    .rose-head{background:#fff0f4;color:#e33e62;}

    div[data-testid="stVerticalBlockBorderWrapper"]{
        border-color:#dfe8f3 !important;
        border-radius:13px !important;
        background:rgba(255,255,255,.80);
        box-shadow:0 3px 12px rgba(31,74,124,.035);
    }

    div[data-testid="stNumberInput"] label,
    div[data-testid="stSelectbox"] label{
        font-size:10px !important;
        color:#283b58 !important;
        font-weight:600 !important;
    }

    div[data-baseweb="input"],
    div[data-baseweb="select"] > div{
        min-height:32px !important;
        border-radius:7px !important;
        background:#fbfdff !important;
        border-color:#d8e3ef !important;
    }

    div[data-baseweb="input"] input{
        font-size:11px !important;
        padding-top:5px !important;
        padding-bottom:5px !important;
    }

    div[data-testid="stSelectbox"]{
        margin-bottom:-7px;
    }
    div[data-testid="stNumberInput"]{
        margin-bottom:-7px;
    }

    .risk-card{
        border-radius:13px;
        padding:13px 14px;
        border:1px solid;
        min-height:124px;
        box-sizing:border-box;
    }
    .risk-red{background:#fff6f6;border-color:#ffdfe1;}
    .risk-blue{background:#f4f9ff;border-color:#dcecff;}
    .risk-green{background:#f1fbf7;border-color:#d8f2e6;}
    .risk-amber{background:#fff9ed;border-color:#f7e8c4;}
    .risk-name{
        color:#182f52;
        font-size:12px;
        font-weight:800;
    }
    .risk-row{
        display:flex;
        align-items:center;
        justify-content:space-between;
        margin-top:8px;
    }
    .risk-pct{
        color:#132b50;
        font-size:31px;
        font-weight:900;
        line-height:1;
    }
    .pill{
        display:inline-block;
        margin-top:8px;
        border-radius:999px;
        padding:4px 9px;
        font-size:10px;
        font-weight:750;
    }
    .pill-red{background:#ffdddd;color:#c9303f;}
    .pill-blue{background:#dbeaff;color:#1266d6;}
    .pill-green{background:#d9f4e8;color:#167b54;}
    .pill-amber{background:#ffedc7;color:#a76a00;}
    .ring{
        width:66px;height:66px;border-radius:50%;
        display:flex;align-items:center;justify-content:center;
        position:relative;
        flex:0 0 auto;
    }
    .ring:after{
        content:"";
        width:48px;height:48px;border-radius:50%;
        background:#fff;
        position:absolute;
    }
    .ring span{
        position:relative;
        z-index:2;
        font-size:13px;
        font-weight:850;
    }

    .ready-box{
        border:1px solid #ccebdc;
        border-radius:10px;
        background:#ebfaf3;
        color:#206c4d;
        padding:10px 12px;
        font-size:11px;
        font-weight:650;
        margin-top:10px;
    }

    div.stButton > button[kind="primary"]{
        border:none !important;
        border-radius:10px !important;
        min-height:48px !important;
        font-size:14px !important;
        font-weight:800 !important;
        color:white !important;
        background:linear-gradient(90deg,#ff4b50 0%,#eb3d8b 49%,#5145e5 100%) !important;
        box-shadow:0 8px 20px rgba(104,62,219,.18);
    }

    div.stButton > button[kind="secondary"]{
        border-radius:9px !important;
        min-height:34px !important;
    }

    [data-testid="stAlert"]{
        border-radius:10px;
        font-size:11px;
    }

    @media(max-width:1100px){
        .hero-title{font-size:32px;}
        .hero-logo{width:60px;height:60px;font-size:34px;}
        .side-note{margin-top:80px;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown(
        "<div class='side-brand'><div class='side-heart'>❤️</div>"
        "<div class='side-title'>Cardio<span>Vision AI</span></div>"
        "<div class='side-sub'>Cardiovascular Risk Prediction</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='side-item active'>⌂ &nbsp;&nbsp; Predict Risk</div>", unsafe_allow_html=True)
    st.markdown("<div class='side-item'>▣ &nbsp;&nbsp; Patient Information</div>", unsafe_allow_html=True)
    st.markdown("<div class='side-item'>↗ &nbsp;&nbsp; Results &amp; Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='side-item'>◇ &nbsp;&nbsp; 3D Visualization</div>", unsafe_allow_html=True)
    st.markdown("<div class='side-item'>ⓘ &nbsp;&nbsp; About the Project</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='side-note'><b>🛡 Research Prototype</b><br><br>"
        "Predictions are for research and educational purposes only and should not be used "
        "as a substitute for professional medical diagnosis.</div>",
        unsafe_allow_html=True,
    )

# -----------------------------
# Header / hero
# -----------------------------
with st.container(border=True):
    hero_left, hero_right = st.columns([2.25, 1.0], gap="small")

    with hero_left:
        st.markdown(
            "<div class='hero-brand'>"
            "<div class='hero-logo'>♥</div>"
            "<div>"
            "<div class='hero-title'>Cardio<span>Vision AI</span></div>"
            "<div class='hero-subtitle'>Cardiovascular Risk &amp; Coronary Stenosis Prediction</div>"
            "<div class='hero-desc'>Enter patient clinical information to estimate overall CAD risk "
            "and stenosis probability for LAD, LCX and RCA coronary arteries.</div>"
            "</div></div>",
            unsafe_allow_html=True,
        )

        st.write("")
        s1, s2, s3 = st.columns(3, gap="small")
        with s1:
            st.markdown(
                "<div class='stat-card'><div class='stat-top'>Models</div>"
                "<div class='stat-ok'>✓ Loaded Successfully</div></div>",
                unsafe_allow_html=True,
            )
        with s2:
            st.markdown(
                f"<div class='stat-card'><div class='stat-top'>Model Input Features</div>"
                f"<div class='stat-value'>{len(feature_columns)}</div>"
                "<div class='stat-foot'>clinical / encoded features</div></div>",
                unsafe_allow_html=True,
            )
        with s3:
            st.markdown(
                f"<div class='stat-card'><div class='stat-top'>Numeric Features</div>"
                f"<div class='stat-value'>{len(numeric_defaults)}</div>"
                "<div class='stat-foot'>clinical measurements</div></div>",
                unsafe_allow_html=True,
            )

    with hero_right:
        try:
            st.image("cardio_heart_crop.jpg", use_container_width=True)
        except Exception:
            st.markdown(
                "<div style='height:210px;border-radius:16px;background:linear-gradient(120deg,#e8f3ff,#ffe6eb);"
                "display:flex;align-items:center;justify-content:center;font-size:82px;'>🫀</div>",
                unsafe_allow_html=True,
            )

# -----------------------------
# Reset helper
# -----------------------------
def reset_inputs():
    for key in list(st.session_state.keys()):
        if key.startswith("inp_") or key == "prediction_results":
            del st.session_state[key]

# -----------------------------
# Main dashboard
# -----------------------------
left, right = st.columns([1.62, 1.0], gap="small")

with left:
    with st.container(border=True):
        title_col, reset_col = st.columns([4.5, 1.0])
        with title_col:
            st.markdown("<div class='panel-title'>👤 &nbsp; Patient Clinical Information</div>", unsafe_allow_html=True)
            st.markdown("<div class='panel-sub'>Fill in the patient’s clinical details below.</div>", unsafe_allow_html=True)
        with reset_col:
            if st.button("↻ Reset All", key="reset_btn", use_container_width=True):
                reset_inputs()
                st.rerun()

        # Basic Information
        with st.container(border=True):
            st.markdown("<div class='section-head blue-head'>👤 &nbsp; Basic Information</div>", unsafe_allow_html=True)
            b1, b2, b3, b4, b5 = st.columns(5, gap="small")
            with b1:
                age = st.number_input("Age (years)", 1.0, 120.0, float(numeric_defaults["Age"]), key="inp_age")
            with b2:
                length = st.number_input("Height (cm)", 100.0, 220.0, float(numeric_defaults["Length"]), key="inp_length")
            with b3:
                weight = st.number_input("Weight (kg)", 20.0, 250.0, float(numeric_defaults["Weight"]), key="inp_weight")
            with b4:
                bmi = st.number_input("BMI", 10.0, 60.0, float(numeric_defaults["BMI"]), key="inp_bmi")
            with b5:
                sex = st.selectbox("Sex", ["Male", "Female"], key="inp_sex")

        # Medical History
        with st.container(border=True):
            st.markdown("<div class='section-head red-head'>♥ &nbsp; Medical History</div>", unsafe_allow_html=True)
            m1, m2, m3, m4, m5 = st.columns(5, gap="small")
            with m1:
                dm = st.selectbox("Diabetes (DM)", [0, 1], index=int(numeric_defaults["DM"]), key="inp_dm")
            with m2:
                htn = st.selectbox("Hypertension (HTN)", [0, 1], index=int(numeric_defaults["HTN"]), key="inp_htn")
            with m3:
                current_smoker = st.selectbox("Current Smoker", [0, 1], index=int(numeric_defaults["Current Smoker"]), key="inp_current_smoker")
            with m4:
                ex_smoker = st.selectbox("Ex-Smoker", [0, 1], index=int(numeric_defaults["EX-Smoker"]), key="inp_ex_smoker")
            with m5:
                fh = st.selectbox("Family History (FH)", [0, 1], index=int(numeric_defaults["FH"]), key="inp_fh")

            m6, m7, m8, _, _ = st.columns(5, gap="small")
            with m6:
                obesity = st.selectbox("Obesity", ["N", "Y"], key="inp_obesity")
            with m7:
                crf = st.selectbox("CRF", ["N", "Y"], key="inp_crf")
            with m8:
                cva = st.selectbox("CVA", ["N", "Y"], key="inp_cva")

        # Symptoms
        with st.container(border=True):
            st.markdown("<div class='section-head green-head'>▣ &nbsp; Symptoms</div>", unsafe_allow_html=True)
            sy1, sy2, sy3, sy4, sy5, sy6 = st.columns(6, gap="small")
            with sy1:
                chest_pain = st.selectbox("Typical Chest Pain", [0, 1], index=int(numeric_defaults["Typical Chest Pain"]), key="inp_chest")
            with sy2:
                dyspnea = st.selectbox("Dyspnea", ["N", "Y"], key="inp_dyspnea")
            with sy3:
                atypical = st.selectbox("Atypical", ["N", "Y"], key="inp_atypical")
            with sy4:
                nonanginal = st.selectbox("Nonanginal", ["N", "Y"], key="inp_nonanginal")
            with sy5:
                lowth_ang = st.selectbox("LowTH Ang", ["N", "Y"], key="inp_lowth")
            with sy6:
                poor_r = st.selectbox("Poor R Progression", ["N", "Y"], key="inp_poor_r")

        lower_left, lower_right = st.columns([1.45, 1.0], gap="small")

        with lower_left:
            with st.container(border=True):
                st.markdown("<div class='section-head amber-head'>〽 &nbsp; Vital Signs</div>", unsafe_allow_html=True)
                v1, v2, v3 = st.columns(3, gap="small")
                with v1:
                    bp = st.number_input("Blood Pressure", value=float(numeric_defaults["BP"]), key="inp_bp")
                with v2:
                    pr = st.number_input("Pulse Rate", value=float(numeric_defaults["PR"]), key="inp_pr")
                with v3:
                    ef_tte = st.number_input("EF-TTE", value=float(numeric_defaults["EF-TTE"]), key="inp_ef")

            with st.container(border=True):
                st.markdown("<div class='section-head blue-head'>⚗ &nbsp; Laboratory Results</div>", unsafe_allow_html=True)
                l1, l2, l3, l4 = st.columns(4, gap="small")
                with l1:
                    fbs = st.number_input("FBS", value=float(numeric_defaults["FBS"]), key="inp_fbs")
                with l2:
                    cr = st.number_input("Creatinine", value=float(numeric_defaults["CR"]), key="inp_cr")
                with l3:
                    tg = st.number_input("TG", value=float(numeric_defaults["TG"]), key="inp_tg")
                with l4:
                    ldl = st.number_input("LDL", value=float(numeric_defaults["LDL"]), key="inp_ldl")

                l5, l6, l7, l8 = st.columns(4, gap="small")
                with l5:
                    hdl = st.number_input("HDL", value=float(numeric_defaults["HDL"]), key="inp_hdl")
                with l6:
                    bun = st.number_input("BUN", value=float(numeric_defaults["BUN"]), key="inp_bun")
                with l7:
                    esr = st.number_input("ESR", value=float(numeric_defaults["ESR"]), key="inp_esr")
                with l8:
                    hb = st.number_input("Hemoglobin", value=float(numeric_defaults["HB"]), key="inp_hb")

                l9, l10, l11, l12 = st.columns(4, gap="small")
                with l9:
                    k = st.number_input("Potassium (K)", value=float(numeric_defaults["K"]), key="inp_k")
                with l10:
                    na = st.number_input("Sodium (Na)", value=float(numeric_defaults["Na"]), key="inp_na")
                with l11:
                    wbc = st.number_input("WBC", value=float(numeric_defaults["WBC"]), key="inp_wbc")
                with l12:
                    lymph = st.number_input("Lymphocytes", value=float(numeric_defaults["Lymph"]), key="inp_lymph")

                l13, l14, _, _ = st.columns(4, gap="small")
                with l13:
                    neut = st.number_input("Neutrophils", value=float(numeric_defaults["Neut"]), key="inp_neut")
                with l14:
                    plt = st.number_input("Platelets (PLT)", value=float(numeric_defaults["PLT"]), key="inp_plt")

        with lower_right:
            with st.container(border=True):
                st.markdown("<div class='section-head purple-head'>〽 &nbsp; ECG & Cardiac Findings</div>", unsafe_allow_html=True)
                e1, e2, e3 = st.columns(3, gap="small")
                with e1:
                    q_wave = st.selectbox("Q Wave", [0, 1], index=int(numeric_defaults["Q Wave"]), key="inp_q")
                with e2:
                    st_elevation = st.selectbox("ST Elevation", [0, 1], index=int(numeric_defaults["St Elevation"]), key="inp_ste")
                with e3:
                    st_depression = st.selectbox("ST Depression", [0, 1], index=int(numeric_defaults["St Depression"]), key="inp_std")

                e4, e5, e6 = st.columns(3, gap="small")
                with e4:
                    tinversion = st.selectbox("T Inversion", [0, 1], index=int(numeric_defaults["Tinversion"]), key="inp_tinv")
                with e5:
                    lvh = st.selectbox("LVH", ["N", "Y"], key="inp_lvh")
                with e6:
                    bbb = st.selectbox("BBB", ["N", "LBBB", "RBBB"], key="inp_bbb")

                e7, e8 = st.columns(2, gap="small")
                with e7:
                    region_rwma = st.number_input("Region RWMA", value=float(numeric_defaults["Region RWMA"]), key="inp_rwma")
                with e8:
                    vhd = st.selectbox("VHD", ["N", "mild", "Moderate", "Severe"], key="inp_vhd")

            with st.container(border=True):
                st.markdown("<div class='section-head rose-head'>🩺 &nbsp; Additional Clinical Findings</div>", unsafe_allow_html=True)
                a1, a2, a3, a4, a5 = st.columns(5, gap="small")
                with a1:
                    edema = st.selectbox("Edema", [0, 1], index=int(numeric_defaults["Edema"]), key="inp_edema")
                with a2:
                    function_class = st.number_input("Function Class", 0, 4, int(numeric_defaults["Function Class"]), 1, key="inp_fc")
                with a3:
                    airway = st.selectbox("Airway Disease", ["N", "Y"], key="inp_airway")
                with a4:
                    thyroid = st.selectbox("Thyroid Disease", ["N", "Y"], key="inp_thyroid")
                with a5:
                    chf = st.selectbox("CHF", ["N", "Y"], key="inp_chf")

                a6, a7, a8, a9, a10 = st.columns(5, gap="small")
                with a6:
                    dlp = st.selectbox("DLP", ["N", "Y"], key="inp_dlp")
                with a7:
                    weak_pulse = st.selectbox("Weak Pulse", ["N", "Y"], key="inp_weak")
                with a8:
                    lung_rales = st.selectbox("Lung Rales", ["N", "Y"], key="inp_rales")
                with a9:
                    systolic_murmur = st.selectbox("Systolic Murmur", ["N", "Y"], key="inp_sysmur")
                with a10:
                    diastolic_murmur = st.selectbox("Diastolic Murmur", ["N", "Y"], key="inp_diamur")

                exertional_cp = "N"

# -----------------------------
# Exact 57-feature conversion
# -----------------------------
def create_model_input():
    patient = pd.DataFrame([[0.0] * len(feature_columns)], columns=feature_columns)

    numeric_values = {
        "Age": age,
        "Weight": weight,
        "Length": length,
        "BMI": bmi,
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

# -----------------------------
# Prediction helpers
# -----------------------------
def class_probability(model, X, target_label):
    classes = list(model.classes_)
    idx = classes.index(target_label)
    return float(model.predict_proba(X)[0][idx] * 100)

def run_prediction():
    return {
        "CAD": {
            "risk": class_probability(cad_model, patient_input, "CAD"),
            "label": str(cad_model.predict(patient_input)[0]),
        },
        "LAD": {
            "risk": class_probability(lad_model, patient_input, "Stenotic"),
            "label": str(lad_model.predict(patient_input)[0]),
        },
        "LCX": {
            "risk": class_probability(lcx_model, patient_input, "Stenotic"),
            "label": str(lcx_model.predict(patient_input)[0]),
        },
        "RCA": {
            "risk": class_probability(rca_model, patient_input, "Stenotic"),
            "label": str(rca_model.predict(patient_input)[0]),
        },
    }

def risk_card(title, result, tone):
    risk = result["risk"]
    label = result["label"]
    colors = {
        "red": ("#ff5059", "#cf3140"),
        "blue": ("#3184ef", "#1667cf"),
        "green": ("#36b779", "#157a53"),
        "amber": ("#f4ad1d", "#aa6b00"),
    }
    color, text_color = colors[tone]
    deg = max(0, min(100, risk)) * 3.6

    return (
        f"<div class='risk-card risk-{tone}'>"
        f"<div class='risk-name'>{title}</div>"
        f"<div class='risk-row'>"
        f"<div><div class='risk-pct'>{risk:.1f}%</div>"
        f"<div class='pill pill-{tone}'>↑ {label}</div></div>"
        f"<div class='ring' style='background:conic-gradient({color} {deg:.1f}deg,#e8edf4 0deg);'>"
        f"<span style='color:{text_color}'>{risk:.0f}%</span></div>"
        f"</div></div>"
    )

# -----------------------------
# Right-side prediction panel
# -----------------------------
with right:
    with st.container(border=True):
        st.markdown("<div class='panel-title'>▥ &nbsp; Prediction Results</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='panel-sub'>Model-estimated probabilities for CAD and coronary artery stenosis.</div>",
            unsafe_allow_html=True,
        )

        results = st.session_state.get("prediction_results")

        if results is None:
            results = {
                "CAD": {"risk": 0.0, "label": "Awaiting"},
                "LAD": {"risk": 0.0, "label": "Awaiting"},
                "LCX": {"risk": 0.0, "label": "Awaiting"},
                "RCA": {"risk": 0.0, "label": "Awaiting"},
            }

        st.write("")
        r1, r2 = st.columns(2, gap="small")
        with r1:
            st.markdown(risk_card("♥ &nbsp; Overall CAD Risk", results["CAD"], "red"), unsafe_allow_html=True)
        with r2:
            st.markdown(risk_card("▣ &nbsp; LAD Stenosis Risk", results["LAD"], "blue"), unsafe_allow_html=True)

        r3, r4 = st.columns(2, gap="small")
        with r3:
            st.markdown(risk_card("▣ &nbsp; LCX Stenosis Risk", results["LCX"], "green"), unsafe_allow_html=True)
        with r4:
            st.markdown(risk_card("◆ &nbsp; RCA Stenosis Risk", results["RCA"], "amber"), unsafe_allow_html=True)

        st.write("")
        with st.container(border=True):
            st.markdown(
                "<div style='font-size:12px;font-weight:800;color:#173151;margin-bottom:4px;'>▥ &nbsp; Coronary Vessel Risk Comparison</div>",
                unsafe_allow_html=True,
            )

            chart_df = pd.DataFrame(
                {
                    "Vessel": ["Overall CAD", "LAD", "LCX", "RCA"],
                    "Risk": [
                        results["CAD"]["risk"],
                        results["LAD"]["risk"],
                        results["LCX"]["risk"],
                        results["RCA"]["risk"],
                    ],
                }
            )

            chart = (
                alt.Chart(chart_df)
                .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=40)
                .encode(
                    x=alt.X("Vessel:N", title=None, sort=["Overall CAD", "LAD", "LCX", "RCA"]),
                    y=alt.Y("Risk:Q", title="Risk Probability (%)", scale=alt.Scale(domain=[0, 100])),
                    color=alt.Color(
                        "Vessel:N",
                        scale=alt.Scale(
                            domain=["Overall CAD", "LAD", "LCX", "RCA"],
                            range=["#ff595f", "#3f8ff0", "#42b97c", "#f3af20"],
                        ),
                        legend=None,
                    ),
                    tooltip=["Vessel", alt.Tooltip("Risk:Q", format=".1f")],
                )
                .properties(height=190)
            )
            st.altair_chart(chart, use_container_width=True)

        if st.button(
            "▶  Predict Cardiovascular Risk",
            type="primary",
            use_container_width=True,
            key="predict_btn",
        ):
            st.session_state["prediction_results"] = run_prediction()
            st.rerun()

        st.markdown(
            f"<div class='ready-box'>✓ &nbsp; Model input ready: "
            f"{patient_input.shape[1]} clinical/encoded features</div>",
            unsafe_allow_html=True,
        )

        st.caption(
            "Research prototype only. Model outputs are not a substitute for professional "
            "medical assessment or diagnostic imaging."
        )
