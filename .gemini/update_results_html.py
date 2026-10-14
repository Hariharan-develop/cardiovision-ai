# Script to replace #view-results in cardiovision_exact_dashboard.html
with open("cardiovision_exact_dashboard.html", "r", encoding="utf-8") as f:
    text = f.read()

start_marker = '  <!-- 3. RESULTS & ANALYSIS VIEW -->\n  <div id="view-results" class="mainView" style="display:none;">'
end_marker = '  <!-- 4. 3D VISUALIZATION VIEW -->\n  <div id="view-viewer3d" class="mainView" style="display:none;">'

start_idx = text.find(start_marker)
end_idx = text.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print(f"ERROR: Markers not found: start_idx={start_idx}, end_idx={end_idx}")
    exit(1)

new_results_html = """  <!-- 3. RESULTS & ANALYSIS VIEW -->
  <div id="view-results" class="mainView" style="display:none;">
    <div class="viewContainer">
      <!-- Screen Header -->
      <div class="viewTitleBox">
        <svg viewBox="0 0 24 24" style="width:36px;height:36px;color:#1759e8;flex-shrink:0;" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 20V5M3 20h18"/><path d="m6 15 4-4 3 2 5-6"/><path d="M17 7h2v2"/></svg>
        <div>
          <h2>Coronary Artery Risk &amp; Prediction Analysis</h2>
          <p>Multi-vessel model probability assessment and explainable cardiovascular risk visualization.</p>
        </div>
        <button type="button" class="exportReportBtn" onclick="exportClinicalReport()" title="Export formal research evaluation report">
          <svg viewBox="0 0 24 24" style="width:16px;height:16px;" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
          <span>Export Clinical Report</span>
        </button>
      </div>

      <!-- Patient Summary Bar -->
      <div class="patientSummaryCard">
        <div class="patientMetaGrid">
          <div class="patientMetaItem">
            <span class="metaLabel">Patient Name</span>
            <span class="metaValue" id="resPatientName">Alex Morgan (Demo Patient)</span>
          </div>
          <div class="patientMetaItem">
            <span class="metaLabel">Patient ID</span>
            <span class="metaValue badgeId" id="resPatientId">CV-2026-8492</span>
          </div>
          <div class="patientMetaItem">
            <span class="metaLabel">Clinical Demographics</span>
            <span class="metaValue" id="resDemographics">58 yrs • Male • BMI 24.9 kg/m²</span>
          </div>
          <div class="patientMetaItem">
            <span class="metaLabel">Evaluation Date</span>
            <span class="metaValue" id="resDate">October 10, 2026</span>
          </div>
          <div class="patientMetaItem">
            <span class="metaLabel">Overall CAD Status</span>
            <span class="metaValue" id="resRiskSummary" style="color:#b91c1c;font-weight:700;">Overall CAD: {CAD_RISK}% ({CAD_LABEL})</span>
          </div>
        </div>
      </div>

      <!-- Stale State Warning Banner -->
      <div id="resStaleNotice" class="resStaleBanner" style="display:none;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        <span>Inputs Modified — Click Predict to Recalculate Model Probabilities</span>
      </div>

      <!-- Four Prediction Summary Cards (Responsive 2x2 Layout) -->
      <div class="resCardsGrid">
        <!-- CAD Card -->
        <div class="resPredCard cad">
          <div class="resCardHeader">
            <div class="resVesselInfo">
              <span class="resVesselTag cad">Overall Disease</span>
              <h3 class="resVesselTitle">CAD — Overall Coronary Disease</h3>
              <span class="resModelSub">Global CAD Classifier (<code>cad_model.pkl</code>)</span>
            </div>
            <div class="resCircleWrap">
              <svg class="resCircleSvg" viewBox="0 0 72 72">
                <circle class="resCircleBg" cx="36" cy="36" r="30" />
                <circle class="resCircleBar cad" id="resCadCircleBar" cx="36" cy="36" r="30" stroke-dasharray="188.5" stroke-dashoffset="18.8" />
              </svg>
              <span class="resCirclePct" id="resCadCardPct">{CAD_RISK}%</span>
            </div>
          </div>
          <div class="resCardBody">
            <div class="resMetricRow">
              <span class="resMetricLabel">Predicted Classification:</span>
              <span class="resClassBadge cad" id="resCadClassBadge">{CAD_LABEL}</span>
            </div>
            <div class="resMetricRow">
              <span class="resMetricLabel">Estimated Probability Category:</span>
              <span class="resTierBadge cad {CAD_TIER_CLASS}" id="resCadTierBadge">{CAD_TIER_LABEL}</span>
            </div>
          </div>
          <div class="resCardFooter">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
            <span>Visualization category, not validated clinical threshold</span>
          </div>
        </div>

        <!-- LAD Card -->
        <div class="resPredCard lad">
          <div class="resCardHeader">
            <div class="resVesselInfo">
              <span class="resVesselTag lad">Anterior Territory</span>
              <h3 class="resVesselTitle">LAD — Left Anterior Descending</h3>
              <span class="resModelSub">Anterior Stenosis Classifier (<code>lad_model.pkl</code>)</span>
            </div>
            <div class="resCircleWrap">
              <svg class="resCircleSvg" viewBox="0 0 72 72">
                <circle class="resCircleBg" cx="36" cy="36" r="30" />
                <circle class="resCircleBar lad" id="resLadCircleBar" cx="36" cy="36" r="30" stroke-dasharray="188.5" stroke-dashoffset="49.0" />
              </svg>
              <span class="resCirclePct" id="resLadCardPct">{LAD_RISK}%</span>
            </div>
          </div>
          <div class="resCardBody">
            <div class="resMetricRow">
              <span class="resMetricLabel">Predicted Classification:</span>
              <span class="resClassBadge lad" id="resLadClassBadge">{LAD_LABEL}</span>
            </div>
            <div class="resMetricRow">
              <span class="resMetricLabel">Estimated Probability Category:</span>
              <span class="resTierBadge lad {LAD_TIER_CLASS}" id="resLadTierBadge">{LAD_TIER_LABEL}</span>
            </div>
          </div>
          <div class="resCardFooter">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
            <span>Visualization category, not validated clinical threshold</span>
          </div>
        </div>

        <!-- LCX Card -->
        <div class="resPredCard lcx">
          <div class="resCardHeader">
            <div class="resVesselInfo">
              <span class="resVesselTag lcx">Lateral Territory</span>
              <h3 class="resVesselTitle">LCX — Left Circumflex Artery</h3>
              <span class="resModelSub">Lateral Stenosis Classifier (<code>lcx_model.pkl</code>)</span>
            </div>
            <div class="resCircleWrap">
              <svg class="resCircleSvg" viewBox="0 0 72 72">
                <circle class="resCircleBg" cx="36" cy="36" r="30" />
                <circle class="resCircleBar lcx" id="resLcxCircleBar" cx="36" cy="36" r="30" stroke-dasharray="188.5" stroke-dashoffset="79.2" />
              </svg>
              <span class="resCirclePct" id="resLcxCardPct">{LCX_RISK}%</span>
            </div>
          </div>
          <div class="resCardBody">
            <div class="resMetricRow">
              <span class="resMetricLabel">Predicted Classification:</span>
              <span class="resClassBadge lcx" id="resLcxClassBadge">{LCX_LABEL}</span>
            </div>
            <div class="resMetricRow">
              <span class="resMetricLabel">Estimated Probability Category:</span>
              <span class="resTierBadge lcx {LCX_TIER_CLASS}" id="resLcxTierBadge">{LCX_TIER_LABEL}</span>
            </div>
          </div>
          <div class="resCardFooter">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
            <span>Visualization category, not validated clinical threshold</span>
          </div>
        </div>

        <!-- RCA Card -->
        <div class="resPredCard rca">
          <div class="resCardHeader">
            <div class="resVesselInfo">
              <span class="resVesselTag rca">Inferior Territory</span>
              <h3 class="resVesselTitle">RCA — Right Coronary Artery</h3>
              <span class="resModelSub">Inferior Stenosis Classifier (<code>rca_model.pkl</code>)</span>
            </div>
            <div class="resCircleWrap">
              <svg class="resCircleSvg" viewBox="0 0 72 72">
                <circle class="resCircleBg" cx="36" cy="36" r="30" />
                <circle class="resCircleBar rca" id="resRcaCircleBar" cx="36" cy="36" r="30" stroke-dasharray="188.5" stroke-dashoffset="59.2" />
              </svg>
              <span class="resCirclePct" id="resRcaCardPct">{RCA_RISK}%</span>
            </div>
          </div>
          <div class="resCardBody">
            <div class="resMetricRow">
              <span class="resMetricLabel">Predicted Classification:</span>
              <span class="resClassBadge rca" id="resRcaClassBadge">{RCA_LABEL}</span>
            </div>
            <div class="resMetricRow">
              <span class="resMetricLabel">Estimated Probability Category:</span>
              <span class="resTierBadge rca {RCA_TIER_CLASS}" id="resRcaTierBadge">{RCA_TIER_LABEL}</span>
            </div>
          </div>
          <div class="resCardFooter">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
            <span>Visualization category, not validated clinical threshold</span>
          </div>
        </div>
      </div>

      <!-- Coronary Probability Comparison Chart -->
      <div class="tableCard resChartCard">
        <div class="resChartHeader">
          <div>
            <h3 class="resSectionTitle">Coronary Probability Comparison Chart</h3>
            <p class="resSectionSub">Comparative model-estimated risk probabilities across the four evaluated anatomical targets.</p>
          </div>
          <div class="resChartLegend">
            <span class="legendItem"><span class="legendDot cad"></span>Overall CAD</span>
            <span class="legendItem"><span class="legendDot lad"></span>LAD Artery</span>
            <span class="legendItem"><span class="legendDot lcx"></span>LCX Artery</span>
            <span class="legendItem"><span class="legendDot rca"></span>RCA Artery</span>
          </div>
        </div>

        <div class="resChartContainer">
          <!-- Y-Axis labels & Gridlines -->
          <div class="chartYAxis">
            <div class="yTick"><span>100%</span><div class="gridLine"></div></div>
            <div class="yTick"><span>75%</span><div class="gridLine"></div></div>
            <div class="yTick"><span>50%</span><div class="gridLine threshold" title="50% Probability visualization threshold"></div></div>
            <div class="yTick"><span>25%</span><div class="gridLine"></div></div>
            <div class="yTick"><span>0%</span><div class="gridLine zero"></div></div>
          </div>

          <!-- Bars Area -->
          <div class="chartBarsArea">
            <!-- CAD Bar -->
            <div class="chartBarCol">
              <div class="barTrack">
                <div class="barValueLabel cad" id="chartCadVal">{CAD_RISK}%</div>
                <div class="barFill cad" id="chartCadBar" style="height:{CAD_RISK}%;"></div>
              </div>
              <div class="barXLabel">
                <b>CAD</b>
                <span>Overall</span>
              </div>
            </div>

            <!-- LAD Bar -->
            <div class="chartBarCol">
              <div class="barTrack">
                <div class="barValueLabel lad" id="chartLadVal">{LAD_RISK}%</div>
                <div class="barFill lad" id="chartLadBar" style="height:{LAD_RISK}%;"></div>
              </div>
              <div class="barXLabel">
                <b>LAD</b>
                <span>Anterior</span>
              </div>
            </div>

            <!-- LCX Bar -->
            <div class="chartBarCol">
              <div class="barTrack">
                <div class="barValueLabel lcx" id="chartLcxVal">{LCX_RISK}%</div>
                <div class="barFill lcx" id="chartLcxBar" style="height:{LCX_RISK}%;"></div>
              </div>
              <div class="barXLabel">
                <b>LCX</b>
                <span>Lateral</span>
              </div>
            </div>

            <!-- RCA Bar -->
            <div class="chartBarCol">
              <div class="barTrack">
                <div class="barValueLabel rca" id="chartRcaVal">{RCA_RISK}%</div>
                <div class="barFill rca" id="chartRcaBar" style="height:{RCA_RISK}%;"></div>
              </div>
              <div class="barXLabel">
                <b>RCA</b>
                <span>Inferior</span>
              </div>
            </div>
          </div>
        </div>

        <div class="chartNote">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          <span>Chart displays model-estimated risk probabilities (0–100%) from statistical estimators, not anatomical diameter narrowing percentages.</span>
        </div>
      </div>

      <!-- Two-Column Grid: Interpretation & Educational Guidance -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;">
        <!-- Card 1: Coronary Stenosis Interpretation -->
        <div class="tableCard">
          <h3 style="font-size:18px;color:#0b2b5b;margin-top:0;margin-bottom:6px;">Coronary Stenosis Interpretation</h3>
          <p style="font-size:13px;color:#4c6993;line-height:1.5;margin-top:0;">Based on the patient's 57 model input features, the specialized machine learning models calculated the following vessel-specific probabilities:</p>
          <ul style="font-size:13.5px;line-height:1.8;color:#1c3e6b;padding-left:20px;margin-bottom:14px;">
            <li><b>Overall CAD:</b> <span id="resCadVal" style="color:#ff2437;font-weight:750;">{CAD_RISK}%</span> (<span id="resCadLbl">{CAD_LABEL}</span>) — Global coronary tree disease burden</li>
            <li><b>Left Anterior Descending (LAD):</b> <span id="resLadVal" style="color:#2d86ea;font-weight:750;">{LAD_RISK}%</span> (<span id="resLadLbl">{LAD_LABEL}</span>) — Anterior myocardial wall &amp; septal perfusion</li>
            <li><b>Left Circumflex (LCX):</b> <span id="resLcxVal" style="color:#19b77c;font-weight:750;">{LCX_RISK}%</span> (<span id="resLcxLbl">{LCX_LABEL}</span>) — Lateral &amp; posterior left ventricular perfusion</li>
            <li><b>Right Coronary Artery (RCA):</b> <span id="resRcaVal" style="color:#ff9700;font-weight:750;">{RCA_RISK}%</span> (<span id="resRcaLbl">{RCA_LABEL}</span>) — Inferior myocardial wall, right ventricle &amp; nodal perfusion</li>
          </ul>
          <div style="background:#f0f6fc;border:1px solid #d0e2f5;border-radius:8px;padding:10px 14px;font-size:12px;color:#284a7d;line-height:1.45;">
            <b>Interpretation Note:</b> Model stenosis probability represents statistical likelihood derived from clinical input patterns and is not a measurement of percentage luminal diameter narrowing. Model estimates do not constitute confirmed coronary stenosis.
          </div>
        </div>

        <!-- Card 2: Clinical Interpretation & Next Steps -->
        <div class="tableCard">
          <h3 style="font-size:18px;color:#0b2b5b;margin-top:0;margin-bottom:6px;">Clinical Interpretation &amp; Next Steps</h3>
          <div id="resMultiVesselAlert" style="background:#fff7ea;border-left:4px solid #ff9700;padding:12px 16px;border-radius:8px;font-size:13px;color:#7a4b00;margin-bottom:12px;">
            <b id="resMultiVesselTitle">Elevated Model-Estimated Probabilities Across Multiple Vessels</b>
            <div id="resMultiVesselText" style="font-size:12px;margin-top:3px;opacity:0.9;">Exploratory visualization criteria indicate elevated probability (&ge; 50%) in multiple vessel targets. This represents an exploratory model pattern and is not a clinical diagnosis.</div>
          </div>
          <div style="font-size:12.5px;line-height:1.6;color:#234470;">
            <p style="margin:0 0 8px;"><b>Educational Guidance &amp; Scope of Use:</b></p>
            <ul style="margin:0;padding-left:18px;display:flex;flex-direction:column;gap:5px;">
              <li>Model probabilities are statistical estimates and require qualified clinician interpretation in full medical context.</li>
              <li>Actual coronary anatomy and luminal patency cannot be confirmed from machine learning probabilities alone.</li>
              <li>Diagnostic testing (e.g., stress imaging or anatomical angiography) and management decisions depend on patient symptoms, physical examination, comprehensive history, and professional medical judgment.</li>
              <li>This application is a research prototype and is not intended for independent clinical decision-making or prescribing therapy.</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Model Performance & Reliability Panel -->
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
              <td><b>LCX Model</b> (<code>lcx_model.pkl</code>)</td>
              <td>Left Circumflex Stenosis</td>
              <td><b>57.4%</b></td>
              <td>53.6%</td>
              <td>0.584</td>
            </tr>
            <tr>
              <td><b>RCA Model</b> (<code>rca_model.pkl</code>)</td>
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
            <b>Model Reliability Notice:</b> LCX and RCA models have limited predictive discrimination in the current validation results (ROC-AUC 0.584 and 0.652). Predictions for these vessels should be interpreted cautiously and must not guide clinical care independently.
          </div>
        </div>
      </div>

      <!-- Understanding the Prediction (Model Explainability Section) -->
      <div class="tableCard explainCard">
        <h3 class="resSectionTitle">Understanding the Prediction</h3>
        <p class="resSectionSub">Overview of feature inputs utilized across the multi-model architecture and explanation availability status.</p>

        <div class="explainGrid">
          <div class="explainCol">
            <div class="explainBox">
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
              </div>
              <div class="explainStatusDesc" style="font-size:11.5px;color:#718ba6;border-top:1px dashed #e2e8f0;padding-top:8px;">
                <b>Integrity Policy:</b> Global model feature importances are intentionally not substituted as patient-specific explanations to prevent misleading individual risk factor attribution.
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
"""

text = text[:start_idx] + new_results_html + text[end_idx:]

with open("cardiovision_exact_dashboard.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Results HTML replaced successfully.")
