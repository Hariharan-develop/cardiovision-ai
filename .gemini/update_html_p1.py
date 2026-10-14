import sys
import re

with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Results View Performance Table
old_perf_table = '''      <!-- Model Performance & Reliability Panel -->
      <div class="tableCard perfTableCard">
        <h3 class="resSectionTitle">Model Performance &amp; Reliability</h3>
        <p class="resSectionSub">Previously recorded validation metrics from model development on retrospective test cohorts. Not independently verified prospective clinical trial performance.</p>
        
        <table class="perfTable">
          <thead>
            <tr>
              <th style="width:20%;">Model</th>
              <th style="width:35%;">Target Anatomical Outcome</th>
              <th style="width:15%;">Accuracy</th>
              <th style="width:15%;">F1 Score</th>
              <th style="width:15%;">ROC-AUC</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><b>CAD Model</b> (<code>cad_model.pkl</code>)</td>
              <td>Overall Coronary Artery Disease</td>
              <td><b>85.2%</b></td>
              <td>89.7%</td>
              <td>0.917</td>
            </tr>
            <tr>
              <td><b>LAD Model</b> (<code>lad_model.pkl</code>)</td>
              <td>Left Anterior Descending Stenosis</td>
              <td><b>65.6%</b></td>
              <td>67.7%</td>
              <td>0.756</td>
            </tr>
            <tr>
              <td><b>LCX Model</b> (<code id="tableLcxModelCode">{LCX_MODEL_FILE}</code>) <span id="tableLcxModeBadge" class="tableCandBadge" style="display:{IS_CANDIDATE_MODE_INLINE};">LCX Candidate ({LCX_THRESH_PCT}%)</span></td>
              <td>Left Circumflex Stenosis</td>
              <td><b>57.4%</b></td>
              <td>53.6%</td>
              <td>0.584</td>
            </tr>
            <tr>
              <td><b>RCA Model</b> (<code id="tableRcaModelCode">{RCA_MODEL_FILE}</code>) <span id="tableRcaModeBadge" class="tableCandBadge" style="display:{IS_CANDIDATE_MODE_INLINE};">RCA Candidate ({RCA_THRESH_PCT}%)</span></td>
              <td>Right Coronary Artery Stenosis</td>
              <td><b>60.7%</b></td>
              <td>50.0%</td>
              <td>0.652</td>
            </tr>
          </tbody>
        </table>

        <div class="cautionNotice">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          <div>
            <b>Model Reliability Notice:</b> LCX and RCA models have limited predictive discrimination in current validation results (ROC-AUC 0.584 and 0.652). Predictions should be interpreted cautiously and must not guide clinical care independently.
          </div>
        </div>
      </div>'''

new_perf_table = '''      <!-- Model Performance & Reliability Panel -->
      <div class="tableCard perfTableCard">
        <h3 class="resSectionTitle">Model Performance &amp; Reliability</h3>
        <p class="resSectionSub" id="perfTableSubtitle">{PERF_TABLE_SUBTITLE}</p>
        
        <table class="perfTable" id="perfTableMain">
          <thead>
            <tr>
              <th style="width:20%;">Model</th>
              <th style="width:35%;">Target Anatomical Outcome</th>
              <th style="width:15%;">Accuracy</th>
              <th style="width:15%;">F1 Score</th>
              <th style="width:15%;">ROC-AUC</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><b>CAD Model</b> (<code>cad_model.pkl</code>)</td>
              <td>Overall Coronary Artery Disease</td>
              <td><b>85.2%</b></td>
              <td>89.7%</td>
              <td>0.917</td>
            </tr>
            <tr>
              <td><b>LAD Model</b> (<code>lad_model.pkl</code>)</td>
              <td>Left Anterior Descending Stenosis</td>
              <td><b>65.6%</b></td>
              <td>67.7%</td>
              <td>0.756</td>
            </tr>
            <tr id="rowPerfLcx">
              <td><b>LCX Model</b> (<code id="tableLcxModelCode">{LCX_MODEL_FILE}</code>) <span id="tableLcxModeBadge" class="tableCandBadge" style="display:{IS_CANDIDATE_MODE_INLINE};">LCX Candidate ({LCX_THRESH_PCT}%)</span></td>
              <td>Left Circumflex Stenosis</td>
              <td id="tableLcxAcc">{LCX_PERF_ACC}</td>
              <td id="tableLcxF1">{LCX_PERF_F1}</td>
              <td id="tableLcxAuc">{LCX_PERF_AUC}</td>
            </tr>
            <tr id="rowPerfRca">
              <td><b>RCA Model</b> (<code id="tableRcaModelCode">{RCA_MODEL_FILE}</code>) <span id="tableRcaModeBadge" class="tableCandBadge" style="display:{IS_CANDIDATE_MODE_INLINE};">RCA Candidate ({RCA_THRESH_PCT}%)</span></td>
              <td>Right Coronary Artery Stenosis</td>
              <td id="tableRcaAcc">{RCA_PERF_ACC}</td>
              <td id="tableRcaF1">{RCA_PERF_F1}</td>
              <td id="tableRcaAuc">{RCA_PERF_AUC}</td>
            </tr>
          </tbody>
        </table>

        <!-- Nested CV Details Card for Candidate Mode -->
        <div id="candidateCvDetails" style="display:{IS_CANDIDATE_MODE_BLOCK};margin-top:10px;background:#f0f9ff;border:1px solid #bae6fd;border-radius:6px;padding:11px 15px;font-size:12px;color:#0369a1;line-height:1.5;">
          <b>Exploratory nested threshold cross-validation — not independent external clinical validation:</b>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:6px;">
            <div><b>LCX Candidate:</b> Macro F1: 0.689 | Stenotic Recall: 0.597 | Precision: 0.634 | Balanced Accuracy: 0.687<br><span style="color:#64748b;font-size:11px;">Accuracy & ROC-AUC: Not evaluated</span></div>
            <div><b>RCA Candidate:</b> Macro F1: 0.651 | Stenotic Recall: 0.632 | Precision: 0.545 | Balanced Accuracy: 0.657<br><span style="color:#64748b;font-size:11px;">Accuracy & ROC-AUC: Not evaluated</span></div>
          </div>
        </div>

        <div class="cautionNotice" id="perfCautionNotice">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          <div id="perfCautionText">{PERF_CAUTION_TEXT}</div>
        </div>
      </div>'''

assert old_perf_table in content, "old_perf_table not found!"
content = content.replace(old_perf_table, new_perf_table, 1)

# 2. Update Print View Performance Table
old_print_perf = '''          <tr>
            <td><b>LCX Model</b> (<code id="printLcxModelCode">{LCX_MODEL_FILE}</code>) <span id="printLcxModeBadge" class="tableCandBadge" style="display:{IS_CANDIDATE_MODE_INLINE};">LCX Candidate ({LCX_THRESH_PCT}%)</span></td>
            <td>Left Circumflex Stenosis</td>
            <td><b>57.4%</b></td>
            <td>53.6%</td>
            <td><b>0.584</b></td>
          </tr>
          <tr>
            <td><b>RCA Model</b> (<code id="printRcaModelCode">{RCA_MODEL_FILE}</code>) <span id="printRcaModeBadge" class="tableCandBadge" style="display:{IS_CANDIDATE_MODE_INLINE};">RCA Candidate ({RCA_THRESH_PCT}%)</span></td>
            <td>Right Coronary Artery Stenosis</td>
            <td><b>60.7%</b></td>
            <td>50.0%</td>
            <td><b>0.652</b></td>
          </tr>
        </tbody>
      </table>
      <div class="perfNote">
        <b>Model Reliability Notice:</b> LCX and RCA models have limited predictive discrimination in current validation results (ROC-AUC 0.584 and 0.652). Predictions should be interpreted cautiously and must not guide clinical care independently.
      </div>'''

new_print_perf = '''          <tr id="printRowLcx">
            <td><b>LCX Model</b> (<code id="printLcxModelCode">{LCX_MODEL_FILE}</code>) <span id="printLcxModeBadge" class="tableCandBadge" style="display:{IS_CANDIDATE_MODE_INLINE};">LCX Candidate ({LCX_THRESH_PCT}%)</span></td>
            <td>Left Circumflex Stenosis</td>
            <td id="printLcxAcc">{LCX_PERF_ACC}</td>
            <td id="printLcxF1">{LCX_PERF_F1}</td>
            <td id="printLcxAuc">{LCX_PERF_AUC}</td>
          </tr>
          <tr id="printRowRca">
            <td><b>RCA Model</b> (<code id="printRcaModelCode">{RCA_MODEL_FILE}</code>) <span id="printRcaModeBadge" class="tableCandBadge" style="display:{IS_CANDIDATE_MODE_INLINE};">RCA Candidate ({RCA_THRESH_PCT}%)</span></td>
            <td>Right Coronary Artery Stenosis</td>
            <td id="printRcaAcc">{RCA_PERF_ACC}</td>
            <td id="printRcaF1">{RCA_PERF_F1}</td>
            <td id="printRcaAuc">{RCA_PERF_AUC}</td>
          </tr>
        </tbody>
      </table>
      <div class="perfNote" id="printPerfNote">
        <span id="printPerfCautionText">{PERF_CAUTION_TEXT}</span>
      </div>'''

assert old_print_perf in content, "old_print_perf not found!"
content = content.replace(old_print_perf, new_print_perf, 1)

# 3. Replace Explainability section
old_explain_card = '''      <!-- Understanding the Prediction Section -->
      <div class="tableCard explainCard">
        <h3 class="resSectionTitle">Understanding the Prediction</h3>
        <p class="resSectionSub">Overview of feature inputs utilized across the multi-model architecture and explanation availability status.</p>

        <div class="explainGrid">
          <div class="explainCol">
            <div class="explainBox">
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
              </div>
              <div class="explainStatusDesc" style="font-size:11.5px;color:#718ba6;border-top:1px dashed #e2e8f0;padding-top:8px;">
                <b>Integrity Policy:</b> Global model feature importances are intentionally not substituted as patient-specific explanations to prevent misleading individual risk factor attribution.
              </div>
            </div>
          </div>
        </div>
      </div>'''

new_explain_card = '''      <!-- AI Explainability Section: Why This Prediction? -->
      <div class="tableCard explainSectionCard" id="aiExplainabilitySection">
        <div class="explainHeaderRow">
          <div class="explainTitleWrap">
            <div class="explainTitleIcon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" style="width:20px;height:20px;"><path d="M12 2a10 10 0 1 0 10 10H12V2z"/><path d="M12 2a10 10 0 0 1 10 10h-10V2z"/><path d="M12 12L2.5 7.5"/></svg>
            </div>
            <div>
              <h3 class="resSectionTitle" style="margin:0;">AI Explainability — Why This Prediction?</h3>
              <p class="resSectionSub" style="margin:2px 0 0;">Patient-specific SHAP (SHapley Additive exPlanations) attribution for active cardiovascular models</p>
            </div>
          </div>
          
          <!-- Vessel Model Selector -->
          <div class="explainVesselSelector" role="tablist">
            <button type="button" class="explainVesselBtn active cad" id="btnExpCad" onclick="selectExplainVessel('cad')">
              <span class="vesselDot cad"></span>
              <span>CAD (Overall)</span>
            </button>
            <button type="button" class="explainVesselBtn lad" id="btnExpLad" onclick="selectExplainVessel('lad')">
              <span class="vesselDot lad"></span>
              <span>LAD (Anterior)</span>
            </button>
            <button type="button" class="explainVesselBtn lcx" id="btnExpLcx" onclick="selectExplainVessel('lcx')">
              <span class="vesselDot lcx"></span>
              <span>LCX (Lateral)</span>
            </button>
            <button type="button" class="explainVesselBtn rca" id="btnExpRca" onclick="selectExplainVessel('rca')">
              <span class="vesselDot rca"></span>
              <span>RCA (Inferior)</span>
            </button>
          </div>
        </div>

        <!-- Active Model Info Banner -->
        <div class="explainVesselBanner cad" id="explainVesselBanner">
          <div class="explainVesselHeader">
            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
              <span class="explainVesselTag" id="expVesselTag">CAD — Overall Coronary Disease</span>
              <span class="explainModelFile" id="expModelFile"><code>cad_model.pkl</code></span>
              <span class="explainCandBadge" id="expCandBadge" style="display:none;">Candidate</span>
            </div>
            <div class="explainMetaStats">
              <div class="expMetaItem">
                <span class="expMetaLabel">Explained Target:</span>
                <span class="expMetaVal" id="expTargetClass">CAD (Positive Class)</span>
              </div>
              <div class="expMetaItem">
                <span class="expMetaLabel">Explainer Method:</span>
                <span class="expMetaVal" id="expMethod">LinearExplainer (Linear SHAP)</span>
              </div>
              <div class="expMetaItem">
                <span class="expMetaLabel">Output Scale:</span>
                <span class="expMetaVal" id="expScaleLabel">Log-odds scale (Δ log-odds)</span>
              </div>
              <div class="expMetaItem">
                <span class="expMetaLabel">Base Value E[f(x)]:</span>
                <span class="expMetaVal" id="expBaseVal">--</span>
              </div>
              <div class="expMetaItem">
                <span class="expMetaLabel">Model Output f(x):</span>
                <span class="expMetaVal" id="expOutputVal">--</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Main SHAP Content: Top 5 Features Table & Horizontal Contribution Chart -->
        <div class="explainContentGrid">
          <!-- Top 5 Features Table -->
          <div class="explainColLeft">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
              <span style="font-size:13px;font-weight:750;color:#1e293b;">Top 5 Contributing Clinical Features</span>
              <span style="font-size:11px;color:#64748b;">Ranked by absolute attribution |SHAP|</span>
            </div>
            <div class="explainTableWrap">
              <table class="explainTable" id="explainTopTable">
                <thead>
                  <tr>
                    <th style="width:36px;">#</th>
                    <th>Clinical Feature</th>
                    <th>Patient Value</th>
                    <th>Contribution</th>
                    <th>Direction</th>
                  </tr>
                </thead>
                <tbody id="explainTopTbody">
                  <!-- Dynamically populated -->
                </tbody>
              </table>
            </div>
          </div>

          <!-- Horizontal SHAP Contribution Bar Chart -->
          <div class="explainColRight">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
              <span style="font-size:13px;font-weight:750;color:#1e293b;">Horizontal SHAP Contribution Chart</span>
              <span id="chartScaleIndicator" style="font-size:11px;color:#64748b;">Log-odds scale</span>
            </div>
            <div class="shapBarContainer" id="shapBarContainer">
              <!-- Dynamically populated horizontal bars centered at 0 -->
            </div>
            <div class="shapAxisLegend">
              <span class="legendLeft">◄ Decreases Predicted Risk</span>
              <span class="legendCenter">Baseline (0)</span>
              <span class="legendRight">Increases Predicted Risk ►</span>
            </div>
          </div>
        </div>

        <!-- Expandable Waterfall Chart -->
        <div class="waterfallToggleRow">
          <button type="button" class="waterfallToggleBtn" id="btnToggleWaterfall" onclick="toggleWaterfallChart()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;"><path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/></svg>
            <span id="waterfallToggleText">View Cumulative SHAP Waterfall Breakdown</span>
            <svg id="waterfallChevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width:14px;height:14px;transition:transform 0.2s;"><path d="M6 9l6 6 6-6"/></svg>
          </button>
        </div>

        <div class="waterfallPanel" id="waterfallPanel" style="display:none;">
          <div class="waterfallHeader">
            <b>Cumulative Waterfall Decomposition:</b> Visualizing how the patient's individual clinical features cumulatively shift model output from the baseline expected value E[f(x)] to the final model prediction f(x).
          </div>
          <div class="waterfallChartWrap" id="waterfallChartWrap">
            <!-- Dynamically populated waterfall steps -->
          </div>
        </div>

        <!-- Research-Only Statistical Policy Disclaimer -->
        <div class="explainDisclaimerNotice">
          <svg viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" style="width:18px;height:18px;flex-shrink:0;"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          <div>
            <b>Research-Only Statistical Model Interpretation:</b> SHAP values quantify the mathematical attribution of patient inputs to this statistical model's output on its calibrated scale (probability for Tree models, log-odds for Linear models). They reflect mathematical statistical associations within the training data distribution and do not establish biological or clinical causation. Output scale differences are preserved; log-odds contributions must not be interpreted as probability percentage changes.
          </div>
        </div>
      </div>

      <!-- Feature Space Context Card -->
      <div class="tableCard" style="margin-bottom:20px;padding:16px 20px;background:#f8fafc;">
        <div style="font-size:12.5px;font-weight:750;color:#334155;margin-bottom:4px;">57-Feature Model Input Architecture</div>
        <div style="font-size:12px;color:#64748b;line-height:1.5;">
          All models evaluate the exact 57-feature vector from <code>feature_columns.pkl</code> structured across 7 clinical domains (Basic Demographics, Medical History, Symptoms, Vital Signs, Biomarkers, ECG Findings, Echocardiography/Physical Findings). All StandardScaler transformations are inverted or handled natively during Linear SHAP attribution.
        </div>
      </div>'''

assert old_explain_card in content, "old_explain_card not found!"
content = content.replace(old_explain_card, new_explain_card, 1)

print("SUCCESS: HTML cards replaced!")
with open('cardiovision_exact_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
