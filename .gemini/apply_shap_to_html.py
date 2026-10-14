import sys

with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Results View Performance Table
start_perf = content.find('<div class="tableCard perfTableCard">')
assert start_perf != -1, "start_perf not found!"
end_perf = content.find('<!-- Understanding the Prediction (Model Explainability Section) -->', start_perf)
assert end_perf != -1, "end_perf not found!"

new_perf_table = '''<div class="tableCard perfTableCard">
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
      </div>

      '''

content = content[:start_perf] + new_perf_table + content[end_perf:]

# 2. Update Print View Performance Table
old_print_tbody = '''          <tr>
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

new_print_tbody = '''          <tr id="printRowLcx">
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

assert old_print_tbody in content, "old_print_tbody not found!"
content = content.replace(old_print_tbody, new_print_tbody, 1)

# 3. Replace Explainability section
start_exp = content.find('<!-- Understanding the Prediction (Model Explainability Section) -->')
assert start_exp != -1, "start_exp not found!"
end_exp = content.find('</div>\n  </div>\n  <!-- 4. 3D VISUALIZATION VIEW -->', start_exp)
assert end_exp != -1, "end_exp not found!"

new_explain_section = '''<!-- AI Explainability Section: Why This Prediction? -->
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
          All models evaluate the exact 57-feature vector from <code>feature_columns.pkl</code> structured across 7 clinical domains (Basic Demographics, Medical History, Symptoms, Vital Signs, Biomarkers, ECG Findings, Echocardiography/Physical Findings). All StandardScaler transformations are handled natively during Linear SHAP attribution.
        </div>
      </div>
'''

content = content[:start_exp] + new_explain_section + content[end_exp:]

# 4. Add CSS styles
css_target = '/* Understanding Prediction (Explainability) */'
css_replacement = '''/* AI Explainability Section */
.explainSectionCard {
  background: #ffffff;
  border: 1px solid #d9e6f3;
  border-radius: 10px;
  padding: 22px 24px;
  margin-bottom: 22px;
  box-shadow: 0 1px 4px rgba(18, 54, 98, 0.05);
}

.explainHeaderRow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 14px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #edf3f9;
}

.explainTitleWrap {
  display: flex;
  align-items: center;
  gap: 12px;
}

.explainTitleIcon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #eef5ff;
  color: #1760e8;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.explainVesselSelector {
  display: inline-flex;
  background: #f1f5fa;
  border: 1px solid #dce6f2;
  border-radius: 8px;
  padding: 3px;
  gap: 4px;
}

.explainVesselBtn {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 12.5px;
  font-weight: 750;
  color: #556987;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.explainVesselBtn:hover {
  color: #1a2e4b;
  background: rgba(255, 255, 255, 0.7);
}

.explainVesselBtn .vesselDot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  display: inline-block;
}
.explainVesselBtn .vesselDot.cad { background: #dc2626; }
.explainVesselBtn .vesselDot.lad { background: #2563eb; }
.explainVesselBtn .vesselDot.lcx { background: #16a34a; }
.explainVesselBtn .vesselDot.rca { background: #ea580c; }

.explainVesselBtn.active.cad {
  background: #ffffff;
  color: #b91c1c;
  box-shadow: 0 1px 3px rgba(185, 28, 28, 0.18);
}
.explainVesselBtn.active.lad {
  background: #ffffff;
  color: #1d4ed8;
  box-shadow: 0 1px 3px rgba(29, 78, 216, 0.18);
}
.explainVesselBtn.active.lcx {
  background: #ffffff;
  color: #15803d;
  box-shadow: 0 1px 3px rgba(21, 128, 61, 0.18);
}
.explainVesselBtn.active.rca {
  background: #ffffff;
  color: #c2410c;
  box-shadow: 0 1px 3px rgba(194, 65, 12, 0.18);
}

.explainVesselBanner {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 14px 18px;
  margin-bottom: 18px;
}
.explainVesselBanner.cad { border-left: 4px solid #dc2626; background: #fffbfb; }
.explainVesselBanner.lad { border-left: 4px solid #2563eb; background: #fbfdff; }
.explainVesselBanner.lcx { border-left: 4px solid #16a34a; background: #fbfefc; }
.explainVesselBanner.rca { border-left: 4px solid #ea580c; background: #fffdfa; }

.explainVesselTag {
  font-size: 13.5px;
  font-weight: 800;
  color: #0f172a;
}
.explainModelFile code {
  font-size: 11px;
  background: #e2e8f0;
  color: #334155;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 700;
}
.explainCandBadge {
  font-size: 10px;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 999px;
  background: #fef3c7;
  color: #b45309;
  border: 1px solid #fde68a;
  text-transform: uppercase;
}

.explainMetaStats {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #e2e8f0;
  font-size: 12px;
}
.expMetaItem {
  display: flex;
  align-items: center;
  gap: 5px;
}
.expMetaLabel {
  color: #64748b;
  font-weight: 600;
}
.expMetaVal {
  color: #0f172a;
  font-weight: 750;
}

.explainContentGrid {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 20px;
  margin-bottom: 16px;
}

.explainTableWrap {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}
.explainTable {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.explainTable th {
  background: #f1f5f9;
  color: #334155;
  padding: 8px 12px;
  font-weight: 750;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}
.explainTable td {
  padding: 8px 12px;
  border-bottom: 1px solid #f1f5f9;
  color: #1e293b;
  vertical-align: middle;
}
.explainTable tr:last-child td {
  border-bottom: none;
}
.explainTable tr:hover td {
  background: #f8fafc;
}

.dirBadge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 7px;
  border-radius: 999px;
  font-size: 10.5px;
  font-weight: 750;
  white-space: nowrap;
}
.dirBadge.increases {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}
.dirBadge.decreases {
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #bbf7d0;
}
.dirBadge.neutral {
  background: #f1f5f9;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

/* Horizontal SHAP Bar Chart */
.shapBarContainer {
  background: #fafcff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 220px;
}
.shapBarRow {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.shapBarLabelRow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11.5px;
}
.shapBarFeatName {
  font-weight: 700;
  color: #1e293b;
}
.shapBarValTxt {
  color: #64748b;
  font-size: 11px;
}
.shapBarShapVal {
  font-weight: 750;
  font-size: 11.5px;
}
.shapTrackWrap {
  position: relative;
  height: 18px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
}
.shapZeroLine {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 2px;
  background: #94a3b8;
  z-index: 2;
}
.shapBarFill {
  position: absolute;
  top: 2px;
  bottom: 2px;
  border-radius: 3px;
  transition: width 0.3s ease;
  z-index: 1;
}
.shapBarFill.increases {
  left: 50%;
  background: #ef4444;
}
.shapBarFill.decreases {
  right: 50%;
  background: #10b981;
}

.shapAxisLegend {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
  font-size: 10.5px;
  font-weight: 700;
}
.legendLeft { color: #059669; }
.legendCenter { color: #64748b; }
.legendRight { color: #dc2626; }

/* Waterfall section */
.waterfallToggleRow {
  margin-top: 14px;
  margin-bottom: 10px;
}
.waterfallToggleBtn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 8px 14px;
  font-size: 12.5px;
  font-weight: 700;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}
.waterfallToggleBtn:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
}

.waterfallPanel {
  background: #fafcff;
  border: 1px solid #dbe6f2;
  border-radius: 8px;
  padding: 16px 18px;
  margin-bottom: 14px;
}
.waterfallHeader {
  font-size: 12px;
  color: #475569;
  margin-bottom: 14px;
  line-height: 1.5;
}
.waterfallList {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.waterfallStepRow {
  display: grid;
  grid-template-columns: 200px 90px 100px 1fr;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  padding: 6px 10px;
  border-radius: 6px;
  background: #ffffff;
  border: 1px solid #edf2f7;
}
.waterfallStepRow.base, .waterfallStepRow.final {
  background: #f8fafc;
  font-weight: 750;
}

.explainDisclaimerNotice {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 10px 14px;
  font-size: 11.5px;
  color: #64748b;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-top: 16px;
  line-height: 1.5;
}
'''

assert css_target in content, "css_target not found!"
content = content.replace(css_target, css_replacement, 1)

# 5. Add JavaScript variables and functions
js_target = 'window.CANDIDATE_RCA_THRESH_PCT = \'{RCA_THRESH_PCT}\' || \'40.0\';'
js_addition = '''window.CANDIDATE_RCA_THRESH_PCT = '{RCA_THRESH_PCT}' || '40.0';
window.INITIAL_SHAP_DATA = {SHAP_DATA_JSON};
let currentExplainVessel = 'cad';
let currentShapData = window.INITIAL_SHAP_DATA || {};
let waterfallExpanded = false;'''

assert js_target in content, "js_target not found!"
content = content.replace(js_target, js_addition, 1)

# 6. Add JS explainability functions right before function updateModeUI
js_fn_target = 'function updateModeUI(mode) {'
js_functions = '''function selectExplainVessel(vessel) {
  currentExplainVessel = vessel;
  
  ['cad', 'lad', 'lcx', 'rca'].forEach(v => {
    const btn = document.getElementById('btnExp' + v.charAt(0).toUpperCase() + v.slice(1));
    if (btn) {
      if (v === vessel) {
        btn.className = 'explainVesselBtn active ' + v;
      } else {
        btn.className = 'explainVesselBtn ' + v;
      }
    }
  });

  renderActiveVesselExplanation();
}

function toggleWaterfallChart() {
  waterfallExpanded = !waterfallExpanded;
  const panel = document.getElementById('waterfallPanel');
  const chevron = document.getElementById('waterfallChevron');
  const btnTxt = document.getElementById('waterfallToggleText');
  if (panel) panel.style.display = waterfallExpanded ? 'block' : 'none';
  if (chevron) chevron.style.transform = waterfallExpanded ? 'rotate(180deg)' : 'rotate(0deg)';
  if (btnTxt) btnTxt.textContent = waterfallExpanded ? 'Hide Cumulative SHAP Waterfall Breakdown' : 'View Cumulative SHAP Waterfall Breakdown';
}

function renderActiveVesselExplanation() {
  const data = (currentShapData && currentShapData[currentExplainVessel]) ? currentShapData[currentExplainVessel] : null;
  const container = document.getElementById('aiExplainabilitySection');
  if (!container) return;

  const banner = document.getElementById('explainVesselBanner');
  if (banner) {
    banner.className = 'explainVesselBanner ' + currentExplainVessel;
  }

  const vesselTitles = {
    'cad': 'CAD — Overall Coronary Disease',
    'lad': 'LAD — Left Anterior Descending Artery',
    'lcx': 'LCX — Left Circumflex Artery',
    'rca': 'RCA — Right Coronary Artery'
  };

  const tagEl = document.getElementById('expVesselTag');
  if (tagEl) tagEl.textContent = vesselTitles[currentExplainVessel] || currentExplainVessel.toUpperCase();

  const fileEl = document.getElementById('expModelFile');
  const candBadge = document.getElementById('expCandBadge');
  const isCand = (currentModelMode === 'candidate' || currentModelMode === 'experimental');
  
  let activeFile = 'cad_model.pkl';
  let isCandidateModel = false;
  if (currentExplainVessel === 'cad') activeFile = 'cad_model.pkl';
  else if (currentExplainVessel === 'lad') activeFile = 'lad_model.pkl';
  else if (currentExplainVessel === 'lcx') {
    activeFile = isCand ? 'lcx_model_candidate.pkl' : 'lcx_model.pkl';
    isCandidateModel = isCand;
  } else if (currentExplainVessel === 'rca') {
    activeFile = isCand ? 'rca_model_candidate.pkl' : 'rca_model.pkl';
    isCandidateModel = isCand;
  }

  if (fileEl) fileEl.innerHTML = '<code>' + activeFile + '</code>';
  if (candBadge) candBadge.style.display = isCandidateModel ? 'inline-flex' : 'none';

  if (!data || !data.available) {
    const reason = (data && data.reason) ? data.reason : 'Explanation unavailable for this model configuration';
    const tbody = document.getElementById('explainTopTbody');
    if (tbody) tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:24px;color:#64748b;font-style:italic;">' + reason + '</td></tr>';
    const chartBox = document.getElementById('shapBarContainer');
    if (chartBox) chartBox.innerHTML = '<div style="text-align:center;padding:40px;color:#64748b;font-style:italic;">Explanation unavailable</div>';
    const wfWrap = document.getElementById('waterfallChartWrap');
    if (wfWrap) wfWrap.innerHTML = '<div style="color:#64748b;font-style:italic;padding:12px;">Explanation unavailable</div>';
    return;
  }

  const targetEl = document.getElementById('expTargetClass');
  if (targetEl) targetEl.textContent = data.target_class + ' (Positive Class)';

  const methodEl = document.getElementById('expMethod');
  if (methodEl) methodEl.textContent = data.explainer_type;

  const scaleEl = document.getElementById('expScaleLabel');
  if (scaleEl) scaleEl.textContent = data.scale_label;

  const baseEl = document.getElementById('expBaseVal');
  if (baseEl) baseEl.textContent = data.base_value_display;

  const outEl = document.getElementById('expOutputVal');
  if (outEl) outEl.textContent = data.model_output_display;

  const scaleIndicator = document.getElementById('chartScaleIndicator');
  if (scaleIndicator) scaleIndicator.textContent = data.scale_label;

  const tbody = document.getElementById('explainTopTbody');
  if (tbody) {
    const topRows = (data.top_features || []).map(f => {
      const dirCls = f.direction;
      const dirIcon = f.direction === 'increases' ? '▲ ' : (f.direction === 'decreases' ? '▼ ' : '• ');
      return `<tr>
        <td style="font-weight:750;color:#64748b;">${f.rank}</td>
        <td>
          <div style="font-weight:700;color:#0f172a;">${f.display_name}</div>
          <div style="font-size:10.5px;color:#64748b;">${f.feature_col} (${f.category})</div>
        </td>
        <td style="font-weight:600;color:#1e293b;">${f.patient_value}</td>
        <td style="font-weight:750;font-size:12px;">${f.display_shap}</td>
        <td><span class="dirBadge ${dirCls}">${dirIcon}${f.direction_label}</span></td>
      </tr>`;
    }).join('');
    tbody.innerHTML = topRows || '<tr><td colspan="5">No features available</td></tr>';
  }

  const chartBox = document.getElementById('shapBarContainer');
  if (chartBox && data.top_features && data.top_features.length > 0) {
    const maxAbs = Math.max(...data.top_features.map(f => f.abs_shap), 0.0001);
    
    chartBox.innerHTML = data.top_features.map(f => {
      const widthPct = Math.min(48, Math.max(3, (f.abs_shap / maxAbs) * 48));
      const isPos = f.shap_value >= 0;
      const barColor = isPos ? (currentExplainVessel === 'cad' ? '#dc2626' : currentExplainVessel === 'lad' ? '#2563eb' : currentExplainVessel === 'lcx' ? '#16a34a' : '#ea580c') : '#10b981';
      
      return `<div class="shapBarRow">
        <div class="shapBarLabelRow">
          <span class="shapBarFeatName">${f.display_name} <span class="shapBarValTxt">(${f.patient_value})</span></span>
          <span class="shapBarShapVal" style="color:${isPos ? '#b91c1c' : '#15803d'};">${f.display_shap}</span>
        </div>
        <div class="shapTrackWrap">
          <div class="shapZeroLine"></div>
          ${isPos ? 
            `<div class="shapBarFill increases" style="width:${widthPct.toFixed(1)}%;background:${barColor};"></div>` :
            `<div class="shapBarFill decreases" style="width:${widthPct.toFixed(1)}%;background:#10b981;"></div>`
          }
        </div>
      </div>`;
    }).join('');
  }

  const wfWrap = document.getElementById('waterfallChartWrap');
  if (wfWrap && data.waterfall_steps) {
    const stepsHtml = data.waterfall_steps.map((st) => {
      let badgeStyle = 'background:#f1f5f9;color:#475569;';
      if (st.type === 'base') {
        badgeStyle = 'background:#e0f2fe;color:#0369a1;';
      } else if (st.type === 'final') {
        badgeStyle = 'background:#fef3c7;color:#92400e;font-weight:800;';
      } else if (st.value > 0) {
        badgeStyle = 'background:#fee2e2;color:#b91c1c;';
      } else if (st.value < 0) {
        badgeStyle = 'background:#dcfce7;color:#15803d;';
      }

      const displayVal = data.scale === 'probability' ? 
        (st.type === 'base' || st.type === 'final' ? (st.value * 100).toFixed(1) + '%' : (st.value >= 0 ? '+' : '') + (st.value * 100).toFixed(1) + '%') :
        (st.type === 'base' || st.type === 'final' ? st.value.toFixed(3) + ' log-odds' : (st.value >= 0 ? '+' : '') + st.value.toFixed(3) + ' log-odds');

      const displayCum = data.scale === 'probability' ? 
        (st.cumulative * 100).toFixed(1) + '%' : 
        st.cumulative.toFixed(3) + ' log-odds';

      return `<div class="waterfallStepRow ${st.type}">
        <div style="font-weight:700;color:#1e293b;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${st.label}">
          ${st.label} ${st.patient_val ? '<span style="font-size:11px;font-weight:normal;color:#64748b;">(' + st.patient_val + ')</span>' : ''}
        </div>
        <div>
          <span style="display:inline-block;padding:2px 7px;border-radius:4px;font-size:11px;font-weight:750;${badgeStyle}">
            ${displayVal}
          </span>
        </div>
        <div style="font-size:11.5px;color:#475569;">
          Running: <b>${displayCum}</b>
        </div>
        <div style="font-size:11px;color:#94a3b8;">
          ${st.type === 'base' ? 'Model Prior' : (st.type === 'final' ? 'Final Model Output' : (st.value >= 0 ? 'Shifts toward target' : 'Shifts away from target'))}
        </div>
      </div>`;
    }).join('');
    
    wfWrap.innerHTML = `<div class="waterfallList">${stepsHtml}</div>`;
  }
}

function updateModeUI(mode) {'''

assert js_fn_target in content, "js_fn_target not found!"
content = content.replace(js_fn_target, js_functions, 1)

# 7. Update updateModeUI to update performance tables & explainability
old_update_tail = '''  const prntLcxBadge = document.getElementById('printLcxModeBadge');
  const prntRcaBadge = document.getElementById('printRcaModeBadge');
  if (prntLcxBadge) {
    prntLcxBadge.style.display = isCand ? 'inline-flex' : 'none';
    prntLcxBadge.textContent = 'LCX Candidate (' + lcxCandPct + '%)';
  }
  if (prntRcaBadge) {
    prntRcaBadge.style.display = isCand ? 'inline-flex' : 'none';
    prntRcaBadge.textContent = 'RCA Candidate (' + rcaCandPct + '%)';
  }
}'''

new_update_tail = '''  const prntLcxBadge = document.getElementById('printLcxModeBadge');
  const prntRcaBadge = document.getElementById('printRcaModeBadge');
  if (prntLcxBadge) {
    prntLcxBadge.style.display = isCand ? 'inline-flex' : 'none';
    prntLcxBadge.textContent = 'LCX Candidate (' + lcxCandPct + '%)';
  }
  if (prntRcaBadge) {
    prntRcaBadge.style.display = isCand ? 'inline-flex' : 'none';
    prntRcaBadge.textContent = 'RCA Candidate (' + rcaCandPct + '%)';
  }

  // Update Performance & Reliability Tables
  const tblLcxAcc = document.getElementById('tableLcxAcc');
  const tblLcxF1 = document.getElementById('tableLcxF1');
  const tblLcxAuc = document.getElementById('tableLcxAuc');
  const tblRcaAcc = document.getElementById('tableRcaAcc');
  const tblRcaF1 = document.getElementById('tableRcaF1');
  const tblRcaAuc = document.getElementById('tableRcaAuc');
  const prntLcxAcc = document.getElementById('printLcxAcc');
  const prntLcxF1 = document.getElementById('printLcxF1');
  const prntLcxAuc = document.getElementById('printLcxAuc');
  const prntRcaAcc = document.getElementById('printRcaAcc');
  const prntRcaF1 = document.getElementById('printRcaF1');
  const prntRcaAuc = document.getElementById('printRcaAuc');
  const perfSubtitle = document.getElementById('perfTableSubtitle');
  const perfCautionText = document.getElementById('perfCautionText');
  const candCvDetails = document.getElementById('candidateCvDetails');
  const prntPerfCaution = document.getElementById('printPerfCautionText');

  if (isCand) {
    if (perfSubtitle) perfSubtitle.textContent = 'Exploratory nested threshold cross-validation — not independent external clinical validation.';
    if (tblLcxAcc) tblLcxAcc.innerHTML = '<i>Not evaluated</i>';
    if (tblLcxF1) tblLcxF1.innerHTML = '<b>0.689</b> <span style="font-size:11px;color:#0284c7;">(Macro F1)</span>';
    if (tblLcxAuc) tblLcxAuc.innerHTML = '<i>Not evaluated</i>';
    if (tblRcaAcc) tblRcaAcc.innerHTML = '<i>Not evaluated</i>';
    if (tblRcaF1) tblRcaF1.innerHTML = '<b>0.651</b> <span style="font-size:11px;color:#0284c7;">(Macro F1)</span>';
    if (tblRcaAuc) tblRcaAuc.innerHTML = '<i>Not evaluated</i>';

    if (prntLcxAcc) prntLcxAcc.innerHTML = '<i>Not evaluated</i>';
    if (prntLcxF1) prntLcxF1.innerHTML = '<b>0.689</b>';
    if (prntLcxAuc) prntLcxAuc.innerHTML = '<i>Not evaluated</i>';
    if (prntRcaAcc) prntRcaAcc.innerHTML = '<i>Not evaluated</i>';
    if (prntRcaF1) prntRcaF1.innerHTML = '<b>0.651</b>';
    if (prntRcaAuc) prntRcaAuc.innerHTML = '<i>Not evaluated</i>';

    if (candCvDetails) candCvDetails.style.display = 'block';
    const candNoticeHtml = '<b>Candidate Cross-Validation Notice:</b> LCX and RCA candidate models report exploratory nested threshold cross-validation metrics (LCX Macro F1: 0.689, Stenotic Recall: 0.597, Precision: 0.634, Balanced Accuracy: 0.687; RCA Macro F1: 0.651, Stenotic Recall: 0.632, Precision: 0.545, Balanced Accuracy: 0.657). Accuracy and ROC-AUC were not evaluated. These are exploratory findings, not independent external clinical validation.';
    if (perfCautionText) perfCautionText.innerHTML = candNoticeHtml;
    if (prntPerfCaution) prntPerfCaution.innerHTML = candNoticeHtml;
  } else {
    if (perfSubtitle) perfSubtitle.textContent = 'Previously recorded validation metrics from model development on retrospective test cohorts. Not independently verified prospective clinical trial performance.';
    if (tblLcxAcc) tblLcxAcc.innerHTML = '<b>57.4%</b>';
    if (tblLcxF1) tblLcxF1.innerHTML = '53.6%';
    if (tblLcxAuc) tblLcxAuc.innerHTML = '0.584';
    if (tblRcaAcc) tblRcaAcc.innerHTML = '<b>60.7%</b>';
    if (tblRcaF1) tblRcaF1.innerHTML = '50.0%';
    if (tblRcaAuc) tblRcaAuc.innerHTML = '0.652';

    if (prntLcxAcc) prntLcxAcc.innerHTML = '<b>57.4%</b>';
    if (prntLcxF1) prntLcxF1.innerHTML = '53.6%';
    if (prntLcxAuc) prntLcxAuc.innerHTML = '<b>0.584</b>';
    if (prntRcaAcc) prntRcaAcc.innerHTML = '<b>60.7%</b>';
    if (prntRcaF1) prntRcaF1.innerHTML = '50.0%';
    if (prntRcaAuc) prntRcaAuc.innerHTML = '<b>0.652</b>';

    if (candCvDetails) candCvDetails.style.display = 'none';
    const stdNoticeHtml = '<b>Model Reliability Notice:</b> LCX and RCA models have limited predictive discrimination in current validation results (ROC-AUC 0.584 and 0.652). Predictions should be interpreted cautiously and must not guide clinical care independently.';
    if (perfCautionText) perfCautionText.innerHTML = stdNoticeHtml;
    if (prntPerfCaution) prntPerfCaution.innerHTML = stdNoticeHtml;
  }

  // Update Explainability view with active model info
  renderActiveVesselExplanation();
}'''

assert old_update_tail in content, "old_update_tail not found!"
content = content.replace(old_update_tail, new_update_tail, 1)

# 8. Update applyPredictions to store SHAP data
old_apply_pred = '''  if (data.candidate_rca_thresh_pct) {
    window.CANDIDATE_RCA_THRESH_PCT = data.candidate_rca_thresh_pct;
  }

  if (data.model_mode) {
    updateModeUI(data.model_mode);
  }'''

new_apply_pred = '''  if (data.candidate_rca_thresh_pct) {
    window.CANDIDATE_RCA_THRESH_PCT = data.candidate_rca_thresh_pct;
  }

  if (data.shap_explanations) {
    currentShapData = data.shap_explanations;
  }

  if (data.model_mode) {
    updateModeUI(data.model_mode);
  } else {
    renderActiveVesselExplanation();
  }'''

assert old_apply_pred in content, "old_apply_pred not found!"
content = content.replace(old_apply_pred, new_apply_pred, 1)

# 9. Trigger initial renderActiveVesselExplanation on load
init_target = "window.addEventListener('hashchange', handleHashRoute);"
init_replacement = '''window.addEventListener('hashchange', handleHashRoute);
  if (typeof renderActiveVesselExplanation === 'function') {
    renderActiveVesselExplanation();
  }'''

assert init_target in content, "init_target not found!"
content = content.replace(init_target, init_replacement, 1)

with open('cardiovision_exact_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Updated cardiovision_exact_dashboard.html with SHAP Explainability & Performance Table fixes!")
