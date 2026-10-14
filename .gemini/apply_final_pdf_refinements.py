import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

new_export_fn = """function exportClinicalReport(){
  syncPatientDetails();
  const pat = getPatientDetails();
  const age = document.getElementById('inp_age')?.value || 58;
  const sex = document.getElementById('inp_sex')?.value || 'Male';
  const length = document.getElementById('inp_length')?.value || 170;
  const weight = document.getElementById('inp_weight')?.value || 72;
  const bmi = document.getElementById('inp_bmi')?.value || '24.9';
  const bp = document.getElementById('inp_bp')?.value || 130;
  const pr = document.getElementById('inp_pr')?.value || 70;
  const ef = document.getElementById('inp_ef_tte')?.value || 50;
  const fbs = document.getElementById('inp_fbs')?.value || 98;
  const cr = document.getElementById('inp_cr')?.value || 1.0;
  const ldl = document.getElementById('inp_ldl')?.value || 100;
  const hdl = document.getElementById('inp_hdl')?.value || 39;
  const tg = document.getElementById('inp_tg')?.value || 122;

  const cadRisk = document.getElementById('cadRiskNum')?.textContent || '—';
  const cadLbl = document.getElementById('cadLabelText')?.textContent || 'Awaiting';
  const ladRisk = document.getElementById('ladRiskNum')?.textContent || '—';
  const ladLbl = document.getElementById('ladLabelText')?.textContent || 'Awaiting';
  const lcxRisk = document.getElementById('lcxRiskNum')?.textContent || '—';
  const lcxLbl = document.getElementById('lcxLabelText')?.textContent || 'Awaiting';
  const rcaRisk = document.getElementById('rcaRiskNum')?.textContent || '—';
  const rcaLbl = document.getElementById('rcaLabelText')?.textContent || 'Awaiting';

  const now = new Date();
  const dateFormatted = now.toLocaleDateString('en-US', {
    weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'
  });
  const timeFormatted = now.toLocaleTimeString('en-US', {
    hour: '2-digit', minute: '2-digit', hour12: true
  }).replace(/\\s+/g, '&nbsp;');
  const reportDateTime = `${dateFormatted},&nbsp;${timeFormatted}`;

  const crVal = parseFloat(cr);
  const crStatus = (!isNaN(crVal) && crVal >= 0.7 && crVal <= 1.3)
    ? 'Within displayed adult reference range (Informational)'
    : 'Outside displayed adult reference range (Informational)';

  const reportHtml = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CardioVision AI - Research Evaluation Report - ${pat.id}</title>
<style>
  @page {
    size: A4 portrait;
    margin: 10mm 14mm 10mm 14mm;
  }
  * {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
  html, body {
    margin: 0;
    padding: 0;
    background: #fff;
    color: #1e293b;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 11.5px;
    line-height: 1.45;
  }
  .nowrap {
    white-space: nowrap !important;
  }

  /* Screen preview styling */
  @media screen {
    body {
      background: #e2e8f0;
      padding: 24px 12px;
    }
    .reportSheet {
      background: #fff;
      width: 210mm;
      max-width: 100%;
      min-height: 297mm;
      margin: 0 auto 24px auto;
      padding: 13mm 16mm 12mm 16mm;
      box-shadow: 0 4px 18px rgba(0,0,0,0.12);
      border-radius: 4px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .page-2 {
      page-break-before: auto !important;
      break-before: auto !important;
    }
    .noPrintBar {
      max-width: 210mm;
      margin: 0 auto 14px auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #0f172a;
      color: #fff;
      padding: 11px 18px;
      border-radius: 6px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.18);
    }
  }

  /* Print / PDF styling */
  @media print {
    body {
      background: #fff;
      padding: 0;
    }
    .reportSheet {
      width: 100% !important;
      min-height: 0 !important;
      margin: 0 !important;
      padding: 0 !important;
      box-shadow: none !important;
      border-radius: 0 !important;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      height: 100%;
    }
    .page-2 {
      page-break-before: always !important;
      break-before: page !important;
      padding-top: 3px !important;
    }
    .noPrint, .noPrintBar {
      display: none !important;
    }
  }

  /* Page break rules */
  .keepTogether {
    page-break-inside: avoid !important;
    break-inside: avoid !important;
  }

  /* Running header for Page 2 */
  .pageRunningHeader {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1.5px solid #cbd5e1;
    padding-bottom: 6px;
    margin-bottom: 14px;
    font-size: 10px;
    font-weight: 750;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  /* Document Header (Page 1) */
  .docHeader {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 2px solid #1759e8;
    padding-bottom: 11px;
    margin-bottom: 13px;
  }
  .brandWrap {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .logoSvg {
    width: 34px;
    height: 34px;
    color: #1759e8;
    flex-shrink: 0;
  }
  .brandTitle {
    font-size: 20px;
    font-weight: 800;
    color: #0b2b5b;
    margin: 0;
    line-height: 1.15;
    letter-spacing: -0.2px;
  }
  .brandSub {
    font-size: 11px;
    color: #475569;
    margin: 2px 0 0;
  }
  .protoBadge {
    display: inline-block;
    background: #fef3c7;
    color: #92400e;
    border: 1px solid #fde68a;
    font-size: 9.5px;
    font-weight: 750;
    padding: 2.5px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin-top: 4px;
  }
  .reportMeta {
    text-align: right;
    font-size: 10.5px;
    color: #475569;
    line-height: 1.5;
  }
  .reportId {
    font-family: monospace;
    font-size: 12px;
    font-weight: 750;
    color: #1759e8;
    background: #eef4ff;
    padding: 2.5px 8px;
    border-radius: 4px;
    display: inline-block;
    margin-top: 2px;
  }

  /* Patient Summary Card */
  .patientCard {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 7px;
    padding: 10px 14px;
    margin-bottom: 13px;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
  }
  .metaItem {
    display: flex;
    flex-direction: column;
    gap: 2.5px;
  }
  .metaItem label {
    font-size: 9.5px;
    font-weight: 750;
    text-transform: uppercase;
    color: #64748b;
    letter-spacing: 0.5px;
  }
  .metaItem span {
    font-size: 12px;
    font-weight: 650;
    color: #0f172a;
    line-height: 1.35;
  }

  /* Section Headings */
  h3 {
    font-size: 12.5px;
    font-weight: 800;
    color: #0b2b5b;
    margin: 12px 0 6px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 3.5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .tableSub {
    font-size: 10.5px;
    color: #475569;
    margin: -2px 0 8px;
    line-height: 1.4;
  }

  /* 4 Outcome Probability Cards */
  .riskGrid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 9px;
    margin-bottom: 9px;
  }
  .riskBox {
    border-radius: 7px;
    padding: 9px 11px;
    border: 1px solid #e2e8f0;
    background: #fff;
    text-align: center;
  }
  .riskBox.cad { border-color: #fecaca; background: #fff5f5; }
  .riskBox.lad { border-color: #bfdbfe; background: #eff6ff; }
  .riskBox.lcx { border-color: #bbf7d0; background: #f0fdf4; }
  .riskBox.rca { border-color: #fed7aa; background: #fff7ed; }

  .riskTitle {
    font-size: 10.5px;
    font-weight: 750;
    color: #475569;
    margin-bottom: 2.5px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }
  .riskNum {
    font-size: 20px;
    font-weight: 850;
    line-height: 1.15;
    margin: 2px 0 3px;
  }
  .riskBox.cad .riskNum { color: #dc2626; }
  .riskBox.lad .riskNum { color: #2563eb; }
  .riskBox.lcx .riskNum { color: #16a34a; }
  .riskBox.rca .riskNum { color: #ea580c; }

  .riskLbl {
    font-size: 10px;
    font-weight: 700;
    padding: 2.5px 7px;
    border-radius: 3.5px;
    display: inline-block;
  }
  .riskBox.cad .riskLbl { background: #fee2e2; color: #b91c1c; }
  .riskBox.lad .riskLbl { background: #dbeafe; color: #1d4ed8; }
  .riskBox.lcx .riskLbl { background: #dcfce7; color: #15803d; }
  .riskBox.rca .riskLbl { background: #ffedd5; color: #c2410c; }

  .cardNote {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 5px;
    padding: 7px 11px;
    font-size: 10px;
    color: #475569;
    line-height: 1.4;
    margin-bottom: 12px;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    font-size: 10.5px;
  }
  th {
    background: #f1f5f9;
    text-align: left;
    padding: 6px 9px;
    font-weight: 750;
    color: #334155;
    border: 1px solid #cbd5e1;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }
  td {
    padding: 5.5px 9px;
    border: 1px solid #e2e8f0;
    color: #1e293b;
    vertical-align: middle;
  }
  tr:nth-child(even) td {
    background: #f8fafc;
  }

  /* Educational Guidance Box */
  .guidanceBox {
    background: #f0f6fc;
    border: 1px solid #cce0f5;
    border-radius: 7px;
    padding: 10px 14px;
    margin-bottom: 12px;
    font-size: 10.5px;
    color: #1e3a5f;
    line-height: 1.45;
  }
  .guidanceBox ul {
    margin: 5px 0 0;
    padding-left: 18px;
  }
  .guidanceBox li {
    margin-bottom: 4px;
  }

  /* Performance Note */
  .perfNote {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-left: 4px solid #f59e0b;
    padding: 8px 12px;
    font-size: 10px;
    color: #92400e;
    line-height: 1.4;
    margin-top: 7px;
    border-radius: 5px;
  }

  /* Research Disclaimer */
  .disclaimer {
    font-size: 10px;
    color: #475569;
    line-height: 1.45;
    border: 1px solid #e2e8f0;
    background: #f8fafc;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 10px;
  }

  /* Footers */
  .pageFooter {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1.5px solid #cbd5e1;
    padding-top: 6px;
    margin-top: auto;
    font-size: 9.5px;
    color: #64748b;
  }
</style>
</head>
<body>

<div class="noPrintBar">
  <div style="font-weight:700;font-size:12.5px;letter-spacing:0.3px;">CardioVision AI — Research Evaluation Report (A4 Format, 2 Pages)</div>
  <div style="display:flex;gap:8px;">
    <button onclick="window.print()" style="padding:6px 16px;background:#1759e8;color:white;border:none;border-radius:4px;font-weight:700;cursor:pointer;font-size:11px;">Print / Save as PDF</button>
    <button onclick="window.close()" style="padding:6px 14px;background:#334155;color:white;border:none;border-radius:4px;font-weight:700;cursor:pointer;font-size:11px;">Close</button>
  </div>
</div>

<!-- ==================== PAGE 1 ==================== -->
<div class="reportSheet page-1">
  <div>
    <!-- Document Header -->
    <div class="docHeader">
      <div class="brandWrap">
        <svg class="logoSvg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8Z"/></svg>
        <div>
          <h1 class="brandTitle">CardioVision AI</h1>
          <div class="brandSub">Multi-Vessel Risk Assessment &amp; Clinical Vector Evaluation</div>
          <div class="protoBadge">Research Prototype Evaluation Report — Not for Clinical Diagnosis</div>
        </div>
      </div>
      <div class="reportMeta">
        <div><b>Evaluation Date:</b> <span class="nowrap">${reportDateTime}</span></div>
        <div><b>Patient ID:</b> <span class="reportId">${pat.id}</span></div>
        <div><b>Architecture:</b> 57-Feature Four-Model Architecture</div>
      </div>
    </div>

    <!-- Patient Summary Card -->
    <div class="patientCard">
      <div class="metaItem">
        <label>Patient Name</label>
        <span>${pat.displayName}</span>
      </div>
      <div class="metaItem">
        <label>Patient ID</label>
        <span class="nowrap" style="font-family:monospace;color:#1759e8;">${pat.id}</span>
      </div>
      <div class="metaItem">
        <label>Age / Biological Sex</label>
        <span class="nowrap">${age}&nbsp;years / ${sex}</span>
      </div>
      <div class="metaItem">
        <label>Height / Weight / BMI</label>
        <span class="nowrap">${length}&nbsp;cm / ${weight}&nbsp;kg (<span class="nowrap">${bmi}&nbsp;kg/m²</span>)</span>
      </div>
    </div>

    <!-- Section 1: Probability Outcomes -->
    <h3>1. Model-Estimated Coronary Outcome Probabilities</h3>
    <div class="riskGrid">
      <div class="riskBox cad">
        <div class="riskTitle">Overall CAD</div>
        <div class="riskNum">${cadRisk}</div>
        <div class="riskLbl">${cadLbl}</div>
      </div>
      <div class="riskBox lad">
        <div class="riskTitle">LAD Artery</div>
        <div class="riskNum">${ladRisk}</div>
        <div class="riskLbl">${ladLbl}</div>
      </div>
      <div class="riskBox lcx">
        <div class="riskTitle">LCX Artery</div>
        <div class="riskNum">${lcxRisk}</div>
        <div class="riskLbl">${lcxLbl}</div>
      </div>
      <div class="riskBox rca">
        <div class="riskTitle">RCA Artery</div>
        <div class="riskNum">${rcaRisk}</div>
        <div class="riskLbl">${rcaLbl}</div>
      </div>
    </div>
    <div class="cardNote">
      <b>Model Estimation Notice:</b> These are model-estimated probabilities, not clinically calibrated risk estimates or measured coronary artery narrowing percentages.
    </div>

    <!-- Section 2: Clinical Input Measurements Summary -->
    <h3>2. Clinical Input Measurements Summary</h3>
    <div class="tableSub">Selected patient measurements from current patient session. Machine learning prediction models evaluate the full standardized 57-feature input vector.</div>
    <table>
      <thead>
        <tr>
          <th style="width:28%;">Parameter</th>
          <th style="width:18%;">Patient Value</th>
          <th style="width:28%;">General Adult Reference (Informational)</th>
          <th style="width:26%;">Informational Status</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><b>Blood Pressure (BP, Systolic)</b></td>
          <td class="nowrap">${bp}&nbsp;mmHg</td>
          <td>&lt; 120 mmHg (resting systolic)</td>
          <td>${parseFloat(bp) >= 130 ? 'Above standard systolic reference (≥ 130 mmHg, Informational)' : parseFloat(bp) >= 120 ? 'Elevated systolic reference (120–129 mmHg, Informational)' : 'Within standard systolic reference'}</td>
        </tr>
        <tr>
          <td><b>Resting Pulse Rate (PR)</b></td>
          <td class="nowrap">${pr}&nbsp;bpm</td>
          <td>60 – 100 bpm</td>
          <td>${parseFloat(pr) >= 60 && parseFloat(pr) <= 100 ? 'Within standard resting range' : 'Outside standard resting range (Informational)'}</td>
        </tr>
        <tr>
          <td><b>Left Ventricular EF (EF-TTE)</b></td>
          <td class="nowrap">${ef}%</td>
          <td>&ge; 50%</td>
          <td>${parseFloat(ef) >= 50 ? 'LVEF ≥ 50% — interpret in clinical context' : 'LVEF < 50% — below reference, interpret in clinical context'}</td>
        </tr>
        <tr>
          <td><b>Fasting Blood Sugar (FBS)</b></td>
          <td class="nowrap">${fbs}&nbsp;mg/dL</td>
          <td>70 – 99 mg/dL</td>
          <td>${parseFloat(fbs) >= 126 ? 'Above standard fasting threshold (≥ 126 mg/dL, Informational)' : parseFloat(fbs) >= 100 ? 'Above standard fasting range (100–125 mg/dL, Informational)' : 'Within standard fasting range'}</td>
        </tr>
        <tr>
          <td><b>Serum Creatinine (CR)</b></td>
          <td class="nowrap">${cr}&nbsp;mg/dL</td>
          <td>0.7 – 1.3 mg/dL</td>
          <td>${crStatus}</td>
        </tr>
        <tr>
          <td><b>LDL Cholesterol</b></td>
          <td class="nowrap">${ldl}&nbsp;mg/dL</td>
          <td>&lt; 100 mg/dL</td>
          <td>${parseFloat(ldl) >= 100 ? 'Above standard reference (≥ 100 mg/dL, Informational)' : 'Within standard reference'}</td>
        </tr>
        <tr>
          <td><b>HDL Cholesterol</b></td>
          <td class="nowrap">${hdl}&nbsp;mg/dL</td>
          <td>&gt; 40 mg/dL (M) / &gt; 50 mg/dL (F)</td>
          <td>${parseFloat(hdl) < 40 ? 'Below standard reference (Informational)' : 'Within standard reference'}</td>
        </tr>
        <tr>
          <td><b>Triglycerides (TG)</b></td>
          <td class="nowrap">${tg}&nbsp;mg/dL</td>
          <td>&lt; 150 mg/dL</td>
          <td>${parseFloat(tg) >= 150 ? 'Above standard reference (Informational)' : 'Within standard reference'}</td>
        </tr>
        <tr>
          <td><b>Evaluated Model Features</b></td>
          <td class="nowrap"><b>57 Model Inputs</b></td>
          <td>Standardized 7-domain feature vector</td>
          <td>34 numeric and 23 one-hot encoded inputs</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- Page 1 Footer -->
  <div class="pageFooter">
    <span>CardioVision AI — Research Evaluation Report</span>
    <span>Confidential Prototype Record</span>
    <span class="nowrap"><b>Page 1 of 2</b></span>
  </div>
</div>

<!-- ==================== PAGE 2 ==================== -->
<div class="reportSheet page-2">
  <div>
    <!-- Running Header (Page 2) -->
    <div class="pageRunningHeader">
      <span>CardioVision AI — Research Evaluation Report</span>
      <span class="nowrap" style="font-family:monospace;color:#1759e8;">${pat.id} — ${pat.displayName}</span>
    </div>

    <!-- Section 3: Model Validation Performance & Reliability (All Kept Together) -->
    <div class="keepTogether">
      <h3>3. Model Validation Performance &amp; Reliability</h3>
      <div class="tableSub">Retrospective model evaluation metrics recorded during development using held-out test data. Not independently verified prospective clinical trial performance.</div>
      <table>
        <thead>
          <tr>
            <th style="width:24%;">Model</th>
            <th style="width:34%;">Target Vascular Outcome</th>
            <th style="width:14%;">Accuracy</th>
            <th style="width:14%;">F1 Score</th>
            <th style="width:14%;">ROC-AUC</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><b>CAD Model</b> (<code>cad_model.pkl</code>)</td>
            <td>Overall Coronary Artery Disease</td>
            <td><b>85.2%</b></td>
            <td>89.7%</td>
            <td><b>0.917</b></td>
          </tr>
          <tr>
            <td><b>LAD Model</b> (<code>lad_model.pkl</code>)</td>
            <td>Left Anterior Descending Stenosis</td>
            <td><b>65.6%</b></td>
            <td>67.7%</td>
            <td><b>0.756</b></td>
          </tr>
          <tr>
            <td><b>LCX Model</b> (<code>lcx_model.pkl</code>)</td>
            <td>Left Circumflex Stenosis</td>
            <td><b>57.4%</b></td>
            <td>53.6%</td>
            <td><b>0.584</b></td>
          </tr>
          <tr>
            <td><b>RCA Model</b> (<code>rca_model.pkl</code>)</td>
            <td>Right Coronary Artery Stenosis</td>
            <td><b>60.7%</b></td>
            <td>50.0%</td>
            <td><b>0.652</b></td>
          </tr>
        </tbody>
      </table>
      <div class="perfNote">
        <b>Model Reliability Notice:</b> LCX and RCA models have limited predictive discrimination in current validation results (ROC-AUC 0.584 and 0.652). Predictions should be interpreted cautiously and must not guide clinical care independently.
      </div>
    </div>

    <div style="height:14px;"></div>

    <!-- Section 4: Educational Guidance & Interpretation -->
    <div class="keepTogether">
      <h3>4. Educational Guidance &amp; Clinical Considerations</h3>
      <div class="guidanceBox">
        <b>Scope of Evaluation &amp; Clinical Considerations:</b>
        <ul>
          <li>Predictions represent statistical model estimates derived from patient input vectors and are not clinical diagnoses.</li>
          <li>Results require interpretation by a qualified physician in full clinical context.</li>
          <li>Actual coronary anatomy and luminal patency cannot be confirmed from machine learning probabilities alone.</li>
          <li>Diagnostic testing and management decisions depend on patient symptoms, physical examination, comprehensive history, and professional medical assessment.</li>
          <li>This application is a research prototype and is not intended for independent clinical decision-making or therapy initiation.</li>
        </ul>
      </div>
    </div>

    <div style="height:8px;"></div>

    <!-- Section 5: Research Prototype Disclaimer -->
    <div class="keepTogether">
      <div class="disclaimer">
        <b>RESEARCH PROTOTYPE — NOT A MEDICAL DEVICE:</b><br>
        For educational and research demonstration purposes only. Predictions must not independently guide clinical decisions. This application is not certified for diagnostic use or treatment planning. Model probabilities and classifications do not substitute for formal diagnostic coronary imaging, physician examination, or qualified medical judgment.
      </div>
    </div>
  </div>

  <!-- Page 2 Footer -->
  <div class="pageFooter">
    <span>CardioVision AI — Research Evaluation Report</span>
    <span class="nowrap">Generated: ${reportDateTime}</span>
    <span class="nowrap"><b>Page 2 of 2</b></span>
  </div>
</div>

<script>
  window.onload = function() {
    setTimeout(function(){ window.print(); }, 400);
  };
<\\/script>
</body>
</html>`;

  const printWindow = window.open('', '_blank');
  if (printWindow) {
    printWindow.document.open();
    printWindow.document.write(reportHtml);
    printWindow.document.close();
  } else {
    const iframe = document.createElement('iframe');
    iframe.style.position = 'fixed';
    iframe.style.right = '0';
    iframe.style.bottom = '0';
    iframe.style.width = '0';
    iframe.style.height = '0';
    iframe.style.border = '0';
    document.body.appendChild(iframe);
    iframe.contentDocument.open();
    iframe.contentDocument.write(reportHtml);
    iframe.contentDocument.close();
    setTimeout(() => {
      iframe.contentWindow.focus();
      iframe.contentWindow.print();
      setTimeout(() => document.body.removeChild(iframe), 2000);
    }, 400);
  }
  return reportHtml;
}"""

with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx_start = text.find('function exportClinicalReport(){')
idx_end = text.find('function sendNavigate(search){', idx_start)

assert idx_start != -1 and idx_end != -1, "Function bounds not found"

text = text[:idx_start] + new_export_fn + text[idx_end:]

with open('cardiovision_exact_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("exportClinicalReport updated successfully in cardiovision_exact_dashboard.html with refined spacing and creatinine logic")
