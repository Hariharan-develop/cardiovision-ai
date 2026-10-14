import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Header Subtitle and Export Button
old_header = """        <div>
          <h2>Coronary Artery Risk &amp; Prediction Analysis</h2>
          <p>Multi-vessel model probability assessment and explainable cardiovascular risk visualization.</p>
        </div>
        <button type="button" class="exportReportBtn" onclick="exportClinicalReport()" title="Export formal research evaluation report">
          <svg viewBox="0 0 24 24" style="width:16px;height:16px;" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
          <span>Export Clinical Report</span>
        </button>"""

new_header = """        <div>
          <h2>Coronary Artery Risk &amp; Prediction Analysis</h2>
          <p>Multi-vessel model probability assessment and cardiovascular risk visualization.</p>
        </div>
        <button type="button" class="exportReportBtn" onclick="exportClinicalReport()" title="Export formal research evaluation report">
          <svg viewBox="0 0 24 24" style="width:16px;height:16px;" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
          <span>Export Research Evaluation Report</span>
        </button>"""

assert old_header in text, "old_header not found"
text = text.replace(old_header, new_header, 1)
print("1. Header subtitle and Export button updated.")

# 2. Update Comparison Chart Note
old_chart_note = """        <div class="chartNote">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          <span>Chart displays model-estimated risk probabilities (0–100%) from statistical estimators, not anatomical diameter narrowing percentages.</span>
        </div>"""

new_chart_note = """        <div class="chartNote">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          <span>Probability categories and the 50% reference line are visualization aids only. They are not clinically validated decision thresholds. Clinical probability calibration has not been established.</span>
        </div>"""

assert old_chart_note in text, "old_chart_note not found"
text = text.replace(old_chart_note, new_chart_note, 1)
print("2. Chart note clarification updated.")

# 3. Update Coronary Stenosis Interpretation
old_stenosis = """          <ul style="font-size:13.5px;line-height:1.8;color:#1c3e6b;padding-left:20px;margin-bottom:14px;">
            <li><b>Overall CAD:</b> <span id="resCadVal" style="color:#ff2437;font-weight:750;">{CAD_RISK}%</span> (<span id="resCadLbl">{CAD_LABEL}</span>) — Global coronary tree disease burden</li>
            <li><b>Left Anterior Descending (LAD):</b> <span id="resLadVal" style="color:#2d86ea;font-weight:750;">{LAD_RISK}%</span> (<span id="resLadLbl">{LAD_LABEL}</span>) — Anterior myocardial wall &amp; septal perfusion</li>
            <li><b>Left Circumflex (LCX):</b> <span id="resLcxVal" style="color:#19b77c;font-weight:750;">{LCX_RISK}%</span> (<span id="resLcxLbl">{LCX_LABEL}</span>) — Lateral &amp; posterior left ventricular perfusion</li>
            <li><b>Right Coronary Artery (RCA):</b> <span id="resRcaVal" style="color:#ff9700;font-weight:750;">{RCA_RISK}%</span> (<span id="resRcaLbl">{RCA_LABEL}</span>) — Inferior myocardial wall, right ventricle &amp; nodal perfusion</li>
          </ul>
          <div style="background:#f0f6fc;border:1px solid #d0e2f5;border-radius:8px;padding:10px 14px;font-size:12px;color:#284a7d;line-height:1.45;">
            <b>Interpretation Note:</b> Model stenosis probability represents statistical likelihood derived from clinical input patterns and is not a measurement of percentage luminal diameter narrowing. Model estimates do not constitute confirmed coronary stenosis.
          </div>"""

new_stenosis = """          <ul style="font-size:13.5px;line-height:1.8;color:#1c3e6b;padding-left:20px;margin-bottom:14px;">
            <li><b>Overall CAD:</b> <span id="resCadVal" style="color:#ff2437;font-weight:750;">{CAD_RISK}%</span> (<span id="resCadLbl">{CAD_LABEL}</span>) — Model-estimated likelihood of overall coronary artery disease.</li>
            <li><b>Left Anterior Descending (LAD):</b> <span id="resLadVal" style="color:#2d86ea;font-weight:750;">{LAD_RISK}%</span> (<span id="resLadLbl">{LAD_LABEL}</span>) — Anterior myocardial wall &amp; septal perfusion</li>
            <li><b>Left Circumflex (LCX):</b> <span id="resLcxVal" style="color:#19b77c;font-weight:750;">{LCX_RISK}%</span> (<span id="resLcxLbl">{LCX_LABEL}</span>) — Lateral &amp; posterior left ventricular perfusion</li>
            <li><b>Right Coronary Artery (RCA):</b> <span id="resRcaVal" style="color:#ff9700;font-weight:750;">{RCA_RISK}%</span> (<span id="resRcaLbl">{RCA_LABEL}</span>) — Inferior myocardial wall, right ventricle &amp; nodal perfusion</li>
          </ul>
          <div style="background:#f0f6fc;border:1px solid #d0e2f5;border-radius:8px;padding:10px 14px;font-size:12px;color:#284a7d;line-height:1.45;">
            <b>Interpretation Note:</b> Model-estimated probabilities are statistical outputs, not measured anatomical stenosis percentages, confirmed disease severity, or validated clinical diagnostic findings.
          </div>"""

assert old_stenosis in text, "old_stenosis not found"
text = text.replace(old_stenosis, new_stenosis, 1)
print("3. Coronary Stenosis Interpretation updated.")

# 4. Update Understanding the Prediction
old_explain = """            <div class="explainBox">
              <b>Utilized Clinical Inputs:</b>
              <div>The models evaluate a standardized 57-dimensional feature space derived from the patient profile across 7 physiological categories:</div>
              <ul>
                <li><b>Demographics &amp; Biometrics (5):</b> Age, Biological Sex, Height, Weight, and Body Mass Index (BMI).</li>
                <li><b>Vital Signs (3):</b> Resting Systolic Blood Pressure (BP), Pulse Rate (PR), and Left Ventricular Ejection Fraction (EF-TTE).</li>
                <li><b>Medical History (8):</b> Diabetes, Hypertension, Smoking Status (Current &amp; Former), Family History, Obesity, CRF, CVA.</li>
                <li><b>Symptoms &amp; ECG Findings (14):</b> Typical/Atypical Angina, Dyspnea, Q Waves, ST Deviation, T Inversion, LVH, BBB.</li>
                <li><b>Biomarkers &amp; Findings (27):</b> FBS, CR, TG, LDL, HDL, BUN, ESR, HB, Electrolytes, Complete Blood Count, RWMA, VHD, Edema, Murmurs.</li>
              </ul>
            </div>
          </div>
          <div class="explainCol">
            <div class="explainStatusBox">
              <div class="explainStatusTitle">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
                <span>Patient-Specific Feature Attribution</span>
              </div>
              <div class="explainStatusDesc">
                <b>Explanation not available</b> for the current heterogeneous model pipeline. Local attribution methods (such as patient-specific SHAP values) are not computed in the active evaluation environment.
              </div>"""

new_explain = """            <div class="explainBox">
              <b>Utilized Clinical Inputs:</b>
              <div style="margin:4px 0 8px;color:#3b5a82;font-size:12px;">The models evaluate an exact <b>57 model input feature vector</b> (34 numeric and 23 one-hot encoded features) derived from <b>54 clinical attributes</b> structured across 7 clinical categories:</div>
              <ul style="margin:0;padding-left:18px;display:flex;flex-direction:column;gap:5px;font-size:12px;color:#284a7d;">
                <li><b>1. Basic Information (5 features — 4 numeric, 1 encoded):</b> Age, Height, Weight, BMI, Biological Sex (Male).</li>
                <li><b>2. Medical History (8 features — 5 numeric, 3 encoded):</b> Diabetes Mellitus, Hypertension, Current Smoker, Ex-Smoker, Family History, Obesity, CRF, CVA.</li>
                <li><b>3. Symptoms (6 features — 1 numeric, 5 encoded):</b> Typical Chest Pain, Dyspnea, Atypical Angina, Non-Anginal Pain, Low-Threshold Angina, Poor R-Wave Progression.</li>
                <li><b>4. Vital Signs (3 features — 3 numeric):</b> Resting Systolic BP, Resting Pulse Rate, Left Ventricular Ejection Fraction (EF-TTE).</li>
                <li><b>5. Laboratory Results (14 features — 14 numeric):</b> Fasting Blood Sugar, Creatinine, Triglycerides, LDL, HDL, BUN, ESR, Hemoglobin, Potassium, Sodium, WBC, Lymphocytes, Neutrophils, Platelets.</li>
                <li><b>6. ECG &amp; Cardiac Findings (11 features — 5 numeric, 6 encoded):</b> Pathologic Q Wave, ST Elevation, ST Depression, T-Wave Inversion, RWMA, LVH, Bundle Branch Block (None, RBBB), Valvular Heart Disease (None, Mild, Severe).</li>
                <li><b>7. Additional Clinical Findings (10 features — 2 numeric, 8 encoded):</b> Peripheral Edema, NYHA Functional Class, Airway Disease, Thyroid Disease, CHF, Dyslipidemia, Weak Peripheral Pulse, Lung Rales, Systolic Murmur, Diastolic Murmur.</li>
              </ul>
            </div>
          </div>
          <div class="explainCol">
            <div class="explainStatusBox">
              <div class="explainStatusTitle">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
                <span>Patient-Specific Feature Attribution</span>
              </div>
              <div class="explainStatusDesc">
                Patient-specific feature attribution is not currently available. SHAP or other local explanation methods have not been computed.
              </div>"""

assert old_explain in text, "old_explain not found"
text = text.replace(old_explain, new_explain, 1)
print("4. Understanding the Prediction (all 7 categories & explainability notice) updated.")

# 5. Update Report Export Disclaimer
old_disclaimer = """<div class="disclaimer">
  <b>RESEARCH PROTOTYPE DISCLAIMER — NOT A MEDICAL DEVICE:</b><br>
  This report was generated by the CardioVision AI research prototype for educational and decision-support demonstration purposes only. The application is not certified for independent diagnostic use, treatment decision-making, or medication prescription. Model probabilities and classifications do not substitute for formal diagnostic coronary imaging, physician examination, or qualified medical judgment.
</div>"""

new_disclaimer = """<div class="disclaimer">
  <b>RESEARCH PROTOTYPE DISCLAIMER — NOT A MEDICAL DEVICE:</b><br>
  Research prototype only. Not a validated medical device. Predictions are intended for educational and research demonstration purposes and must not independently guide clinical decisions.
</div>"""

assert old_disclaimer in text, "old_disclaimer not found"
text = text.replace(old_disclaimer, new_disclaimer, 1)
print("5. Report export disclaimer updated.")

with open('cardiovision_exact_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("\nAll 5 updates successfully applied to cardiovision_exact_dashboard.html.")
