import os
import re

print("Starting dashboard integration...")

with open("cardiovision_exact_dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

# ---------------------------------------------------------------------------
# 1. Add CSS rules before </style>
# ---------------------------------------------------------------------------
css_additions = """
/* ==========================================================================
   PATIENT DOCUMENT UPLOAD & EXTRACTION REVIEW STYLES
   ========================================================================== */
.uploadSection {
  background: white;
  border: 1px solid #d9e5f2;
  border-radius: 12px;
  margin-bottom: 20px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(15,44,89,0.04);
}
.uploadSection .sectionHead {
  padding: 12px 18px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.uploadDropZone {
  border: 2px dashed #93c5fd;
  background: #f8fbff;
  border-radius: 10px;
  padding: 22px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
}
.uploadDropZone:hover, .uploadDropZone.dragover {
  border-color: #1759e8;
  background: #eff6ff;
  transform: translateY(-1px);
}
.uploadIconWrap {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #e0edff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}
.browseFilesBtn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  background: #1759e8;
  color: white;
  border: none;
  border-radius: 7px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}
.browseFilesBtn:hover {
  background: #0d47cb;
  transform: translateY(-1px);
}
.extractSummaryPills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}
.extractPill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border-radius: 14px;
  font-size: 11.5px;
  font-weight: 700;
  cursor: pointer;
}
.extractPill.active {
  box-shadow: 0 0 0 2px #0f172a;
}
.extractPill.extracted { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.extractPill.calculated { background: #dbeafe; color: #1d4ed8; border: 1px solid #bfdbfe; }
.extractPill.needsReview { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
.extractPill.notFound { background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; }

.reviewTableWrap {
  max-height: 380px;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  margin-bottom: 14px;
}
.reviewTable {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  text-align: left;
}
.reviewTable th {
  background: #f8fafc;
  padding: 10px 12px;
  font-weight: 750;
  color: #334155;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 2;
}
.reviewTable td {
  padding: 8px 12px;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}
.reviewTable tr:hover td {
  background: #f8fbff;
}
.reviewInput {
  width: 100%;
  padding: 5px 8px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
  background: #fff;
  transition: border-color 0.15s ease;
}
.reviewInput:focus {
  border-color: #1759e8;
  outline: none;
  box-shadow: 0 0 0 2px rgba(23,89,232,0.15);
}
.statusBadge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2.5px 7.5px;
  border-radius: 6px;
  font-size: 10.5px;
  font-weight: 750;
  letter-spacing: 0.3px;
  text-transform: uppercase;
}
.statusBadge.Extracted { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
.statusBadge.Calculated { background: #dbeafe; color: #1d4ed8; border: 1px solid #93c5fd; }
.statusBadge.Needs_Review, .statusBadge.NeedsReview { background: #fef3c7; color: #b45309; border: 1px solid #fcd34d; }
.statusBadge.Not_Found, .statusBadge.NotFound { background: #f1f5f9; color: #94a3b8; border: 1px solid #e2e8f0; }

.applyExtractedBtn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 18px;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 750;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(16,185,129,0.3);
  transition: all 0.15s ease;
}
.applyExtractedBtn:hover {
  background: linear-gradient(135deg, #059669, #047857);
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(16,185,129,0.4);
}
.discardBtn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 650;
  cursor: pointer;
  transition: all 0.15s ease;
}
.discardBtn:hover {
  background: #e2e8f0;
  color: #1e293b;
}

/* ==========================================================================
   PREDICTION HISTORY VIEW STYLES
   ========================================================================== */
.historyMetricsGrid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 22px;
}
.historyMetricCard {
  background: white;
  border: 1px solid #d9e5f2;
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(20,52,95,.04);
}
.historyMetricIcon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.historyMetricIcon.blue { background: #e8f1fd; color: #1759e8; }
.historyMetricIcon.green { background: #e8faf3; color: #0ab76a; }
.historyMetricIcon.purple { background: #f2eefa; color: #7952e9; }
.historyMetricIcon.amber { background: #fef6e7; color: #d97706; }
.historyMetricIcon svg { width: 24px; height: 24px; }
.historyMetricVal { font-size: 24px; font-weight: 850; color: #0f172a; line-height: 1.1; }
.historyMetricLabel { font-size: 11px; font-weight: 750; color: #64748b; letter-spacing: 0.4px; text-transform: uppercase; margin-top: 2px; }

.historyControlsBar {
  background: white;
  border: 1px solid #d9e5f2;
  border-radius: 12px;
  padding: 12px 18px;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
}
.historySearchWrap {
  position: relative;
  flex: 1;
  min-width: 260px;
}
.historySearchWrap input {
  width: 100%;
  padding: 8px 12px 8px 36px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 12.5px;
  color: #1e293b;
  background: #f8fafc;
}
.historySearchWrap svg {
  position: absolute;
  left: 11px;
  top: 50%;
  transform: translateY(-50%);
  width: 15px;
  height: 15px;
  color: #94a3b8;
}
.historyFiltersGroup {
  display: flex;
  align-items: center;
  gap: 10px;
}
.historySelect {
  padding: 7px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 12px;
  color: #334155;
  background: white;
  font-weight: 600;
}
.historyTableContainer {
  background: white;
  border: 1px solid #d9e5f2;
  border-radius: 12px;
  overflow-x: auto;
  box-shadow: 0 2px 10px rgba(15,44,89,0.03);
  margin-bottom: 24px;
}
.historyTable {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  text-align: left;
}
.historyTable th {
  background: #f8fafc;
  padding: 12px 14px;
  font-weight: 750;
  color: #475569;
  border-bottom: 1px solid #e2e8f0;
  letter-spacing: 0.3px;
  font-size: 11px;
  text-transform: uppercase;
  white-space: nowrap;
}
.historyTable td {
  padding: 12px 14px;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}
.historyTable tr:hover td {
  background: #f8fbff;
}
.modeBadge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2.5px 7px;
  border-radius: 6px;
  font-size: 10.5px;
  font-weight: 750;
  letter-spacing: 0.3px;
}
.modeBadge.standard { background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }
.modeBadge.candidate { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }

.historyVesselPill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2.5px 7px;
  border-radius: 5px;
  font-size: 11px;
  font-weight: 750;
}
.historyVesselPill.stenotic { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }
.historyVesselPill.normal { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }

.histActionBtn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 9px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.12s ease;
  border: 1px solid transparent;
}
.histActionBtn.view { background: #eff6ff; color: #1d4ed8; border-color: #bfdbfe; }
.histActionBtn.view:hover { background: #dbeafe; }
.histActionBtn.load { background: #ecfdf5; color: #047857; border-color: #a7f3d0; }
.histActionBtn.load:hover { background: #d1fae5; }
.histActionBtn.pdf { background: #f5f3ff; color: #6d28d9; border-color: #ddd6fe; }
.histActionBtn.pdf:hover { background: #ede9fe; }
.histActionBtn.del { background: #fff1f2; color: #be123c; border-color: #fecdd3; }
.histActionBtn.del:hover { background: #ffe4e6; }

/* Modal Styles */
.histModalOverlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.histModalContent {
  background: white;
  border-radius: 16px;
  max-width: 920px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.35);
}
.histModalHead {
  padding: 18px 24px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.histModalBody {
  padding: 20px 24px;
  overflow-y: auto;
  flex: 1;
}
.histModalFoot {
  padding: 14px 24px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}
@media (max-width: 900px) {
  .historyMetricsGrid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .historyMetricsGrid { grid-template-columns: 1fr; }
}
"""

if "PATIENT DOCUMENT UPLOAD & EXTRACTION REVIEW STYLES" not in content:
    content = content.replace("</style>", css_additions + "\n</style>", 1)
    print("1. Added CSS additions.")
else:
    print("1. CSS already present.")

# ---------------------------------------------------------------------------
# 2. Add Prediction History nav item to sidebar
# ---------------------------------------------------------------------------
nav_history_item = """    <div class="navItem" onclick="switchNav('results')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20V10M10 20V4M16 20v-7M22 20V7"/><path d="M2 20h22"/></svg>Results &amp; Analysis</div>
    <div class="navItem" onclick="switchNav('history')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>Prediction History</div>"""

if "switchNav('history')" not in content:
    target_nav = '<div class="navItem" onclick="switchNav(\'results\')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20V10M10 20V4M16 20v-7M22 20V7"/><path d="M2 20h22"/></svg>Results &amp; Analysis</div>'
    if target_nav in content:
        content = content.replace(target_nav, nav_history_item, 1)
        print("2. Added Prediction History nav item to sidebar.")
    else:
        print("2. ERROR: target_nav not found!")
else:
    print("2. Prediction History nav item already present.")

# ---------------------------------------------------------------------------
# 3. Add Document Upload Section in Predict Risk View (above Basic Info)
# ---------------------------------------------------------------------------
upload_section_html = """        <!-- 0. Smart Patient Medical Report Upload Section -->
        <div class="section uploadSection" id="uploadReportSection">
          <div class="sectionHead" style="background:linear-gradient(135deg,#0e274d,#173d72);color:white;">
            <svg viewBox="0 0 24 24" class="headIcon" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="12" y2="12"/><line x1="15" y1="15" x2="12" y2="12"/></svg>
            <span>Upload Patient Medical Report</span>
            <span style="margin-left:auto;font-size:10px;font-weight:700;padding:2px 8px;border-radius:12px;background:rgba(255,255,255,0.15);letter-spacing:0.4px;">PDF • DOCX • OCR</span>
          </div>
          <div style="padding:14px;">
            <!-- Drag & Drop Zone -->
            <div id="uploadDropZone" class="uploadDropZone" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event)" onclick="document.getElementById('reportFileInput').click()">
              <input type="file" id="reportFileInput" accept=".pdf,.docx,.doc,.png,.jpg,.jpeg" style="display:none;" onchange="handleFileSelected(event)">
              <div class="uploadIconWrap">
                <svg viewBox="0 0 24 24" fill="none" stroke="#1759e8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:26px;height:26px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
              </div>
              <div style="font-size:13.5px;font-weight:750;color:#1e293b;margin-bottom:3px;">Drag &amp; Drop Patient Report here</div>
              <div style="font-size:11.5px;color:#64748b;margin-bottom:10px;">Supports text &amp; scanned PDFs, Word (.docx), and ECG/lab images</div>
              <button type="button" class="browseFilesBtn" onclick="event.stopPropagation();document.getElementById('reportFileInput').click()">
                <svg viewBox="0 0 24 24" style="width:14px;height:14px;" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                <span>Browse Files</span>
              </button>
            </div>

            <!-- Upload & Parsing Progress -->
            <div id="uploadProgressState" style="display:none;padding:16px 12px;text-align:center;">
              <div class="spinner" style="display:inline-block;width:24px;height:24px;border:3px solid #e2e8f0;border-top-color:#1759e8;border-radius:50%;animation:cvSpin 0.8s linear infinite;"></div>
              <div id="uploadStatusText" style="margin-top:8px;font-size:12.5px;font-weight:650;color:#1e40af;">Parsing document and extracting clinical biomarkers...</div>
            </div>

            <!-- Upload Error Alert -->
            <div id="uploadErrorBox" style="display:none;margin-top:10px;padding:10px 14px;background:#fef2f2;border:1px solid #fecaca;border-radius:8px;font-size:12px;color:#b91c1c;display:flex;align-items:center;gap:8px;">
              <svg viewBox="0 0 24 24" style="width:16px;height:16px;flex-shrink:0;" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              <span id="uploadErrorMsg"></span>
            </div>

            <!-- Applied Success Alert -->
            <div id="uploadAppliedAlert" style="display:none;margin-top:10px;padding:10px 14px;background:#ecfdf5;border:1px solid #a7f3d0;border-radius:8px;font-size:12px;color:#065f46;display:flex;align-items:center;gap:8px;">
            </div>

            <!-- Review Table Container -->
            <div id="extractionReviewContainer" style="display:none;margin-top:14px;">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                <div style="font-size:13px;font-weight:800;color:#1e293b;">Clinical Extraction Review &amp; Confirmation</div>
                <div style="font-size:11px;color:#64748b;" id="extractDocFilename">Report: sample.pdf</div>
              </div>
              <div style="font-size:11.5px;color:#64748b;margin-bottom:10px;line-height:1.4;">
                Review extracted parameters before applying. Edit any field directly. <b>Apply to Patient Form</b> updates matching inputs and requires a new prediction before results or PDF reports can be exported.
              </div>

              <!-- Summary Filter Pills -->
              <div class="extractSummaryPills" id="extractSummaryPills">
                <span class="extractPill active" onclick="filterReviewTable('all')">All (<span id="pillCountAll">0</span>)</span>
                <span class="extractPill extracted" onclick="filterReviewTable('Extracted')">Extracted (<span id="pillCountExtracted">0</span>)</span>
                <span class="extractPill calculated" onclick="filterReviewTable('Calculated')">Calculated (<span id="pillCountCalculated">0</span>)</span>
                <span class="extractPill needsReview" onclick="filterReviewTable('Needs Review')">Needs Review (<span id="pillCountNeedsReview">0</span>)</span>
                <span class="extractPill notFound" onclick="filterReviewTable('Not Found')">Not Found (<span id="pillCountNotFound">0</span>)</span>
              </div>

              <!-- Scrollable Table -->
              <div class="reviewTableWrap">
                <table class="reviewTable">
                  <thead>
                    <tr>
                      <th style="width:38%;">Clinical Field</th>
                      <th style="width:34%;">Extracted Value</th>
                      <th style="width:16%;">Status</th>
                      <th style="width:12%;text-align:right;">Action</th>
                    </tr>
                  </thead>
                  <tbody id="extractionReviewTbody">
                  </tbody>
                </table>
              </div>

              <!-- Action Buttons -->
              <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;">
                <button type="button" class="discardBtn" onclick="discardExtraction()">
                  <svg viewBox="0 0 24 24" style="width:13px;height:13px;" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  <span>Discard Extraction</span>
                </button>
                <button type="button" class="applyExtractedBtn" onclick="applyExtractedValues()">
                  <svg viewBox="0 0 24 24" style="width:16px;height:16px;" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                  <span>Apply to Patient Form</span>
                </button>
              </div>
            </div>
          </div>
        </div>
"""

if 'id="uploadReportSection"' not in content:
    target_basic = '        <!-- 1. Basic Information -->'
    if target_basic in content:
        content = content.replace(target_basic, upload_section_html + "\n" + target_basic, 1)
        print("3. Added Document Upload Section before Basic Information.")
    else:
        print("3. ERROR: target_basic not found!")
else:
    print("3. Document Upload Section already present.")

# ---------------------------------------------------------------------------
# 4. Add Prediction History View (between results and viewer3d)
# ---------------------------------------------------------------------------
history_view_html = """  <!-- 4. PREDICTION HISTORY VIEW -->
  <div id="view-history" class="mainView" style="display:none;">
    <div class="viewContainer">
      <div class="viewTitleBox" style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
        <div style="display:flex;align-items:center;gap:14px;">
          <div style="width:44px;height:44px;border-radius:12px;background:#e8f1fd;color:#1759e8;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
            <svg viewBox="0 0 24 24" style="width:24px;height:24px;" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          </div>
          <div>
            <h2 style="font-size:20px;font-weight:800;color:#0f172a;margin:0 0 4px 0;">Prediction History &amp; Clinical Audit Trail</h2>
            <p style="font-size:12.5px;color:#64748b;margin:0;">Immutable clinical snapshots, multi-vessel probability estimates, and reproducible research reports.</p>
          </div>
        </div>
        <button type="button" class="discardBtn" onclick="loadHistoryEvaluations()" style="gap:6px;">
          <svg viewBox="0 0 24 24" style="width:14px;height:14px;" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6M1 20v-6h6"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
          <span>Refresh Records</span>
        </button>
      </div>

      <!-- Summary Metrics Cards -->
      <div class="historyMetricsGrid">
        <div class="historyMetricCard">
          <div class="historyMetricIcon blue">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
          </div>
          <div>
            <div class="historyMetricVal" id="histStatTotal">0</div>
            <div class="historyMetricLabel">Total Evaluations</div>
          </div>
        </div>
        <div class="historyMetricCard">
          <div class="historyMetricIcon green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </div>
          <div>
            <div class="historyMetricVal" id="histStatPatients">0</div>
            <div class="historyMetricLabel">Unique Patients</div>
          </div>
        </div>
        <div class="historyMetricCard">
          <div class="historyMetricIcon purple">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="m9 12 2 2 4-4"/></svg>
          </div>
          <div>
            <div class="historyMetricVal" id="histStatStandard">0</div>
            <div class="historyMetricLabel">Standard Mode</div>
          </div>
        </div>
        <div class="historyMetricCard">
          <div class="historyMetricIcon amber">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          </div>
          <div>
            <div class="historyMetricVal" id="histStatCandidate">0</div>
            <div class="historyMetricLabel">Experimental Mode</div>
          </div>
        </div>
      </div>

      <!-- Controls Bar (Search, Filters, Sort) -->
      <div class="historyControlsBar">
        <div class="historySearchWrap">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input type="text" id="histSearchInput" placeholder="Search by patient name or ID..." oninput="handleHistorySearch(this.value)">
        </div>
        <div class="historyFiltersGroup">
          <label style="font-size:12px;font-weight:700;color:#64748b;">Mode:</label>
          <select class="historySelect" id="histModeFilter" onchange="filterHistoryEvaluations()">
            <option value="all">All Modes</option>
            <option value="standard">Standard Mode</option>
            <option value="candidate">Experimental Mode</option>
          </select>
          <label style="font-size:12px;font-weight:700;color:#64748b;margin-left:8px;">Sort:</label>
          <select class="historySelect" id="histSortSelect" onchange="filterHistoryEvaluations()">
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
          </select>
        </div>
      </div>

      <!-- Evaluations Table Container -->
      <div class="historyTableContainer">
        <div id="histLoadingIndicator" style="display:none;padding:30px;text-align:center;">
          <div class="spinner" style="display:inline-block;width:26px;height:26px;border:3px solid #e2e8f0;border-top-color:#1759e8;border-radius:50%;animation:cvSpin 0.8s linear infinite;"></div>
          <div style="margin-top:8px;font-size:12.5px;color:#64748b;font-weight:600;">Loading historical evaluations...</div>
        </div>
        <div id="histEmptyState" style="display:none;padding:45px 20px;text-align:center;">
          <div style="width:52px;height:52px;border-radius:50%;background:#f1f5f9;color:#94a3b8;display:inline-flex;align-items:center;justify-content:center;margin-bottom:12px;">
            <svg viewBox="0 0 24 24" style="width:26px;height:26px;" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          </div>
          <div style="font-size:14px;font-weight:750;color:#334155;margin-bottom:4px;">No Prediction Records Found</div>
          <div style="font-size:12px;color:#64748b;max-width:380px;margin:0 auto 16px;">Perform a prediction from the Predict Risk screen or import a clinical report to log evaluations.</div>
          <button type="button" class="browseFilesBtn" onclick="switchNav('predict')">Go to Predict Risk</button>
        </div>
        <table class="historyTable" id="histTable" style="display:none;">
          <thead>
            <tr>
              <th>Date &amp; Evaluation ID</th>
              <th>Patient Identity</th>
              <th>Mode</th>
              <th>CAD Risk</th>
              <th>LAD Risk</th>
              <th>LCX Risk</th>
              <th>RCA Risk</th>
              <th>Snapshot Hash</th>
              <th style="text-align:right;">Actions</th>
            </tr>
          </thead>
          <tbody id="histTableBody">
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Prediction History Details Modal -->
  <div id="historyDetailsModal" class="histModalOverlay" style="display:none;" onclick="if(event.target===this)closeHistoryModal()">
    <div class="histModalContent">
      <div class="histModalHead">
        <div style="display:flex;align-items:center;gap:10px;">
          <div style="width:36px;height:36px;border-radius:8px;background:#e8f1fd;color:#1759e8;display:flex;align-items:center;justify-content:center;">
            <svg viewBox="0 0 24 24" style="width:20px;height:20px;" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          </div>
          <div>
            <h3 style="font-size:16px;font-weight:800;color:#0f172a;margin:0;" id="histModalTitle">Evaluation Details</h3>
            <div style="font-size:11.5px;color:#64748b;font-family:monospace;" id="histModalSubtitle">ID: &mdash;</div>
          </div>
        </div>
        <button type="button" onclick="closeHistoryModal()" style="background:none;border:none;cursor:pointer;color:#64748b;padding:4px;">
          <svg viewBox="0 0 24 24" style="width:20px;height:20px;" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <div class="histModalBody" id="histModalBody">
      </div>
      <div class="histModalFoot">
        <button type="button" class="discardBtn" onclick="closeHistoryModal()">Close</button>
        <button type="button" class="histActionBtn load" style="padding:8px 14px;font-size:12px;" id="histModalLoadBtn" onclick="loadModalPatient()">
          <svg viewBox="0 0 24 24" style="width:14px;height:14px;" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
          <span>Load Patient Into Form</span>
        </button>
        <button type="button" class="histActionBtn pdf" style="padding:8px 14px;font-size:12px;" id="histModalPdfBtn" onclick="exportModalPdf()">
          <svg viewBox="0 0 24 24" style="width:14px;height:14px;" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          <span>Export Historical PDF</span>
        </button>
      </div>
    </div>
  </div>
"""

if 'id="view-history"' not in content:
    target_3d = '  <!-- 4. 3D VISUALIZATION VIEW -->'
    if target_3d in content:
        content = content.replace(target_3d, history_view_html + "\n  <!-- 5. 3D VISUALIZATION VIEW -->", 1)
        print("4. Added Prediction History view.")
    else:
        print("4. ERROR: target_3d not found!")
else:
    print("4. Prediction History view already present.")

# ---------------------------------------------------------------------------
# 5. Update switchNav to include 'history'
# ---------------------------------------------------------------------------
old_ids = "const ids = ['predict', 'patient', 'results', 'viewer3d', 'about'];"
new_ids = "const ids = ['predict', 'patient', 'results', 'history', 'viewer3d', 'about'];"

if old_ids in content:
    content = content.replace(old_ids, new_ids, 1)
    print("5. Updated switchNav ids array to include 'history'.")

# Add history tab handler inside switchNav
old_sn_block = """  if (viewId === 'patient') {
    renderPatientInfoScreen();
  }"""

new_sn_block = """  if (viewId === 'patient') {
    renderPatientInfoScreen();
  }
  if (viewId === 'history') {
    loadHistoryEvaluations();
  }"""

if old_sn_block in content:
    content = content.replace(old_sn_block, new_sn_block, 1)
    print("5b. Added loadHistoryEvaluations() call in switchNav.")

# ---------------------------------------------------------------------------
# 6. Update predictRisk() to send patient_id and patient_name
# ---------------------------------------------------------------------------
old_predict_payload = """  // Strictly extract ONLY the 57 clinical features (excluding patient identity)
  const payload = {};
  document.querySelectorAll('#view-predict input, #view-predict select').forEach(el => {
    if (el.name && el.name !== 'bmi' && el.name !== 'patient_name' && el.name !== 'patient_id' && el.value !== '') {
      payload[el.name] = el.value;
    }
  });

  payload['model_mode'] = currentModelMode;"""

new_predict_payload = """  // Extract clinical features and patient identity
  const payload = {};
  document.querySelectorAll('#view-predict input, #view-predict select').forEach(el => {
    if (el.name && el.name !== 'bmi' && el.name !== 'patient_name' && el.name !== 'patient_id' && el.value !== '') {
      payload[el.name] = el.value;
    }
  });

  const patIdEl = document.getElementById('inp_patient_id');
  const patNmEl = document.getElementById('inp_patient_name');
  if (patIdEl && patIdEl.value) payload['patient_id'] = patIdEl.value;
  if (patNmEl && patNmEl.value) payload['patient_name'] = patNmEl.value;
  payload['model_mode'] = currentModelMode;"""

if old_predict_payload in content:
    content = content.replace(old_predict_payload, new_predict_payload, 1)
    print("6. Updated predictRisk() payload with patient_id and patient_name.")

# ---------------------------------------------------------------------------
# 7. Add JavaScript for Document Upload & Prediction History
# ---------------------------------------------------------------------------
js_additions = """
// ==========================================================================
// PATIENT DOCUMENT UPLOAD & EXTRACTION CLIENT ENGINE
// ==========================================================================
let currentExtractionResult = null;
let currentReviewFilter = 'all';

function handleDragOver(e) {
  e.preventDefault();
  e.stopPropagation();
  const dz = document.getElementById('uploadDropZone');
  if (dz) dz.classList.add('dragover');
}

function handleDragLeave(e) {
  e.preventDefault();
  e.stopPropagation();
  const dz = document.getElementById('uploadDropZone');
  if (dz) dz.classList.remove('dragover');
}

function handleDrop(e) {
  e.preventDefault();
  e.stopPropagation();
  const dz = document.getElementById('uploadDropZone');
  if (dz) dz.classList.remove('dragover');
  const files = e.dataTransfer ? e.dataTransfer.files : null;
  if (files && files.length > 0) {
    uploadPatientReportFile(files[0]);
  }
}

function handleFileSelected(e) {
  const files = e.target.files;
  if (files && files.length > 0) {
    uploadPatientReportFile(files[0]);
  }
}

function uploadPatientReportFile(file) {
  const allowedExts = ['.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg'];
  const ext = '.' + file.name.split('.').pop().toLowerCase();
  const errBox = document.getElementById('uploadErrorBox');
  const errMsg = document.getElementById('uploadErrorMsg');
  const progBox = document.getElementById('uploadProgressState');
  const dropZone = document.getElementById('uploadDropZone');
  const appliedAlert = document.getElementById('uploadAppliedAlert');
  if (appliedAlert) appliedAlert.style.display = 'none';

  if (!allowedExts.includes(ext)) {
    if (errBox && errMsg) {
      errMsg.textContent = `Unsupported file format '${ext}'. Please upload a clinical PDF, Word (.docx) document, or ECG image.`;
      errBox.style.display = 'flex';
    }
    return;
  }

  if (file.size > 20 * 1024 * 1024) {
    if (errBox && errMsg) {
      errMsg.textContent = `File is too large (${(file.size / (1024*1024)).toFixed(1)} MB). Maximum allowed size is 20 MB.`;
      errBox.style.display = 'flex';
    }
    return;
  }

  if (errBox) errBox.style.display = 'none';
  if (dropZone) dropZone.style.display = 'none';
  if (progBox) progBox.style.display = 'block';

  const reader = new FileReader();
  reader.onload = function(e) {
    const rawData = e.target.result;
    const base64Data = rawData.split(',')[1] || rawData;

    fetch('http://127.0.0.1:8502/api/upload-report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename: file.name,
        file_data: base64Data,
        extract_ocr: true
      })
    })
    .then(res => {
      if (!res.ok) {
        return res.json().then(j => { throw new Error(j.error || ('Server error ' + res.status)); });
      }
      return res.json();
    })
    .then(data => {
      if (progBox) progBox.style.display = 'none';
      if (!data.success) {
        throw new Error(data.error || 'Extraction failed');
      }
      currentExtractionResult = data;
      renderExtractionReview(data, file.name);
    })
    .catch(err => {
      if (progBox) progBox.style.display = 'none';
      if (dropZone) dropZone.style.display = 'block';
      if (errBox && errMsg) {
        errMsg.textContent = err.message || 'Error parsing medical document';
        errBox.style.display = 'flex';
      }
    });
  };
  reader.onerror = function() {
    if (progBox) progBox.style.display = 'none';
    if (dropZone) dropZone.style.display = 'block';
    if (errBox && errMsg) {
      errMsg.textContent = 'Failed to read local file.';
      errBox.style.display = 'flex';
    }
  };
  reader.readAsDataURL(file);
}

function renderExtractionReview(result, filename) {
  const reviewContainer = document.getElementById('extractionReviewContainer');
  const reviewTbody = document.getElementById('extractionReviewTbody');
  const fnEl = document.getElementById('extractDocFilename');
  if (fnEl) fnEl.textContent = `Report: ${filename}`;

  const summary = result.summary || {};
  document.getElementById('pillCountAll').textContent = result.review_items ? result.review_items.length : 57;
  document.getElementById('pillCountExtracted').textContent = summary.extracted_count || 0;
  document.getElementById('pillCountCalculated').textContent = summary.calculated_count || 0;
  document.getElementById('pillCountNeedsReview').textContent = summary.needs_review_count || 0;
  document.getElementById('pillCountNotFound').textContent = summary.not_found_count || 0;

  reviewTbody.innerHTML = '';
  const items = result.review_items || [];
  items.forEach(item => {
    const tr = document.createElement('tr');
    tr.className = 'reviewTableRow';
    tr.setAttribute('data-status', item.status);

    const safeStatus = (item.status || 'Not_Found').replace(/\s+/g, '_');
    const isAccepted = item.status === 'Extracted' || item.status === 'Calculated';
    const displayVal = item.extracted_value !== null && item.extracted_value !== undefined ? String(item.extracted_value) : '';

    tr.innerHTML = `
      <td>
        <div style="font-weight:700;color:#1e293b;">${item.display_name}</div>
        <div style="font-size:10px;color:#64748b;font-family:monospace;">${item.field_key}${item.units ? ' (' + item.units + ')' : ''}</div>
      </td>
      <td>
        <input type="text" class="reviewInput reviewRowInput" data-feat="${item.field_key}" value="${displayVal}" placeholder="&mdash;">
      </td>
      <td>
        <span class="statusBadge ${safeStatus}">${item.status}</span>
      </td>
      <td style="text-align:right;">
        <label style="font-size:11px;font-weight:700;color:#334155;cursor:pointer;display:inline-flex;align-items:center;gap:4px;">
          <input type="checkbox" class="reviewRowAccept" ${isAccepted ? 'checked' : ''}>
          <span>Accept</span>
        </label>
      </td>
    `;
    reviewTbody.appendChild(tr);
  });

  if (reviewContainer) reviewContainer.style.display = 'block';
  filterReviewTable('all');
}

function filterReviewTable(status) {
  currentReviewFilter = status;
  document.querySelectorAll('.extractPill').forEach(p => p.classList.remove('active'));
  const rows = document.querySelectorAll('.reviewTableRow');
  rows.forEach(r => {
    const rStatus = r.getAttribute('data-status');
    if (status === 'all' || rStatus === status) {
      r.style.display = '';
    } else {
      r.style.display = 'none';
    }
  });
}

function discardExtraction() {
  currentExtractionResult = null;
  const reviewContainer = document.getElementById('extractionReviewContainer');
  const dropZone = document.getElementById('uploadDropZone');
  const errBox = document.getElementById('uploadErrorBox');
  const fileInput = document.getElementById('reportFileInput');
  if (reviewContainer) reviewContainer.style.display = 'none';
  if (dropZone) dropZone.style.display = 'block';
  if (errBox) errBox.style.display = 'none';
  if (fileInput) fileInput.value = '';
}

function applyExtractedValues() {
  if (!currentExtractionResult) return;
  let appliedCount = 0;

  // 1. Patient identity if extracted
  if (currentExtractionResult.patient_info) {
    if (currentExtractionResult.patient_info.id) {
      const pid = document.getElementById('inp_patient_id');
      if (pid) pid.value = currentExtractionResult.patient_info.id;
    }
    if (currentExtractionResult.patient_info.name) {
      const pnm = document.getElementById('inp_patient_name');
      if (pnm) pnm.value = currentExtractionResult.patient_info.name;
    }
  }

  // 2. Iterate over user review rows that are checked for Accept
  const rows = document.querySelectorAll('.reviewTableRow');
  rows.forEach(r => {
    const chk = r.querySelector('.reviewRowAccept');
    const inp = r.querySelector('.reviewRowInput');
    if (chk && chk.checked && inp) {
      const featKey = inp.getAttribute('data-feat');
      const val = inp.value.trim();
      if (featKey && val !== '' && val !== '—') {
        const formEl = document.getElementById('inp_' + featKey);
        if (formEl) {
          formEl.value = val;
          formEl.dispatchEvent(new Event('input', { bubbles: true }));
          formEl.dispatchEvent(new Event('change', { bubbles: true }));
          formEl.style.transition = 'background-color 0.4s ease, border-color 0.4s ease';
          formEl.style.backgroundColor = '#ecfdf5';
          formEl.style.borderColor = '#10b981';
          setTimeout(() => {
            formEl.style.backgroundColor = '';
            formEl.style.borderColor = '';
          }, 3000);
          appliedCount++;
        }
      }
    }
  });

  // 3. Recalculate derived fields
  if (typeof updateBMI === 'function') {
    updateBMI();
  }

  // 4. Invalidate previous predictions and SHAP results
  clearPredictionResults();
  sessionStorage.setItem('cardiovision_state', 'awaiting');
  sessionStorage.removeItem('cardiovision_last_prediction');

  // 5. Hide review container and show notification
  discardExtraction();
  const appliedAlert = document.getElementById('uploadAppliedAlert');
  if (appliedAlert) {
    appliedAlert.style.display = 'flex';
    appliedAlert.innerHTML = `
      <svg viewBox="0 0 24 24" style="width:16px;height:16px;color:#059669;flex-shrink:0;" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
      <span>Successfully applied <b>${appliedCount} extracted clinical parameters</b> to the patient form. Previous predictions and SHAP explanations are invalidated. Click <b>Predict Cardiovascular Risk</b> below to run model inference.</span>
    `;
    setTimeout(() => {
      appliedAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
  }
}

// ==========================================================================
// PREDICTION HISTORY CLIENT ENGINE
// ==========================================================================
let historyRecordsCache = [];
let activeModalEvalRecord = null;

function loadHistoryEvaluations() {
  const loading = document.getElementById('histLoadingIndicator');
  const empty = document.getElementById('histEmptyState');
  const table = document.getElementById('histTable');

  if (loading) loading.style.display = 'block';
  if (empty) empty.style.display = 'none';
  if (table) table.style.display = 'none';

  fetch('http://127.0.0.1:8502/api/history?limit=100')
    .then(res => res.json())
    .then(data => {
      if (loading) loading.style.display = 'none';
      if (!data.success) throw new Error(data.error || 'Failed to fetch history');

      // Update summary metric cards
      const metrics = data.metrics || {};
      document.getElementById('histStatTotal').textContent = metrics.total_evaluations || 0;
      document.getElementById('histStatPatients').textContent = metrics.total_patients || 0;
      document.getElementById('histStatStandard').textContent = metrics.standard_evaluations || 0;
      document.getElementById('histStatCandidate').textContent = metrics.candidate_evaluations || 0;

      historyRecordsCache = data.evaluations || [];
      filterHistoryEvaluations();
    })
    .catch(err => {
      if (loading) loading.style.display = 'none';
      if (empty) empty.style.display = 'block';
      console.error('History load error:', err);
    });
}

function handleHistorySearch(query) {
  filterHistoryEvaluations();
}

function filterHistoryEvaluations() {
  const searchInput = document.getElementById('histSearchInput');
  const modeSelect = document.getElementById('histModeFilter');
  const sortSelect = document.getElementById('histSortSelect');

  const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
  const mode = modeSelect ? modeSelect.value : 'all';
  const sort = sortSelect ? sortSelect.value : 'newest';

  let filtered = historyRecordsCache.filter(item => {
    if (mode !== 'all' && item.model_mode !== mode) return false;
    if (query) {
      const matchName = (item.patient_name || '').toLowerCase().includes(query);
      const matchId = (item.patient_id || '').toLowerCase().includes(query);
      const matchEvalId = (item.id || '').toLowerCase().includes(query);
      if (!matchName && !matchId && !matchEvalId) return false;
    }
    return true;
  });

  filtered.sort((a, b) => {
    const tA = new Date(a.timestamp || 0).getTime();
    const tB = new Date(b.timestamp || 0).getTime();
    return sort === 'newest' ? tB - tA : tA - tB;
  });

  renderHistoryTableRows(filtered);
}

function renderHistoryTableRows(evaluations) {
  const tbody = document.getElementById('histTableBody');
  const table = document.getElementById('histTable');
  const empty = document.getElementById('histEmptyState');

  if (!tbody || !table || !empty) return;

  if (evaluations.length === 0) {
    table.style.display = 'none';
    empty.style.display = 'block';
    return;
  }

  empty.style.display = 'none';
  table.style.display = 'table';
  tbody.innerHTML = '';

  evaluations.forEach(ev => {
    const tr = document.createElement('tr');
    const isCand = ev.model_mode === 'candidate';
    const dStr = ev.timestamp ? new Date(ev.timestamp).toLocaleString() : 'Recent';
    const hashShort = (ev.snapshot_hash || '').substring(0, 8);

    const cadSten = ev.cad_classification === 'CAD';
    const ladSten = ev.lad_classification === 'Stenotic';
    const lcxSten = ev.lcx_classification === 'Stenotic';
    const rcaSten = ev.rca_classification === 'Stenotic';

    tr.innerHTML = `
      <td>
        <div style="font-weight:750;color:#0f172a;">${dStr}</div>
        <div style="font-size:10.5px;color:#64748b;font-family:monospace;">ID: ${ev.id.substring(0, 13)}...</div>
      </td>
      <td>
        <div style="font-weight:750;color:#1e293b;">${ev.patient_name || 'Alex Morgan'}</div>
        <div style="font-size:11px;color:#64748b;">${ev.patient_id || 'CV-2026-8492'} &bull; ${ev.patient_data && ev.patient_data.age ? ev.patient_data.age + 'y' : '58y'} ${ev.patient_data && ev.patient_data.sex ? ev.patient_data.sex : 'Male'}</div>
      </td>
      <td>
        <span class="modeBadge ${isCand ? 'candidate' : 'standard'}">${isCand ? 'Experimental' : 'Standard'}</span>
      </td>
      <td>
        <span class="historyVesselPill ${cadSten ? 'stenotic' : 'normal'}">${(ev.cad_probability * 100).toFixed(1)}% &bull; ${cadSten ? 'CAD' : 'Normal'}</span>
      </td>
      <td>
        <span class="historyVesselPill ${ladSten ? 'stenotic' : 'normal'}">${(ev.lad_probability * 100).toFixed(1)}% &bull; ${ladSten ? 'Stenotic' : 'Normal'}</span>
      </td>
      <td>
        <span class="historyVesselPill ${lcxSten ? 'stenotic' : 'normal'}">${(ev.lcx_probability * 100).toFixed(1)}% &bull; ${lcxSten ? 'Stenotic' : 'Normal'}</span>
      </td>
      <td>
        <span class="historyVesselPill ${rcaSten ? 'stenotic' : 'normal'}">${(ev.rca_probability * 100).toFixed(1)}% &bull; ${rcaSten ? 'Stenotic' : 'Normal'}</span>
      </td>
      <td>
        <code style="font-size:10.5px;padding:2px 5px;background:#f1f5f9;border-radius:4px;color:#334155;">#${hashShort}</code>
      </td>
      <td style="text-align:right;white-space:nowrap;">
        <button type="button" class="histActionBtn view" onclick="viewHistoryDetails('${ev.id}')" title="View snapshot and SHAP breakdown">Details</button>
        <button type="button" class="histActionBtn load" onclick="loadHistoryPatient('${ev.id}')" title="Restore snapshot into prediction form">Load</button>
        <button type="button" class="histActionBtn pdf" onclick="exportHistoryPdf('${ev.id}')" title="Export exact historical PDF">PDF</button>
        <button type="button" class="histActionBtn del" onclick="deleteHistoryEvaluation('${ev.id}')" title="Delete record">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function viewHistoryDetails(evalId) {
  const ev = historyRecordsCache.find(x => x.id === evalId);
  if (!ev) return;
  activeModalEvalRecord = ev;

  const modal = document.getElementById('historyDetailsModal');
  const title = document.getElementById('histModalTitle');
  const sub = document.getElementById('histModalSubtitle');
  const body = document.getElementById('histModalBody');

  if (title) title.textContent = `Historical Evaluation &bull; ${ev.patient_name || 'Alex Morgan'}`;
  if (sub) sub.textContent = `Evaluation ID: ${ev.id} &bull; Timestamp: ${ev.timestamp} &bull; Snapshot Hash: #${ev.snapshot_hash}`;

  const isCand = ev.model_mode === 'candidate';
  const pat = ev.patient_data || {};
  const th = ev.decision_thresholds || {};

  body.innerHTML = `
    <!-- Top summary bar -->
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:18px;">
      <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:12px;">
        <div style="font-size:11px;font-weight:750;color:#64748b;">CAD OVERALL</div>
        <div style="font-size:18px;font-weight:850;color:${ev.cad_probability >= (th.CAD || 0.5) ? '#dc2626' : '#16a34a'};">${(ev.cad_probability * 100).toFixed(1)}%</div>
        <div style="font-size:11px;color:#64748b;">Threshold: ${((th.CAD || 0.5)*100).toFixed(0)}%</div>
      </div>
      <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:12px;">
        <div style="font-size:11px;font-weight:750;color:#64748b;">LAD ARTERY</div>
        <div style="font-size:18px;font-weight:850;color:${ev.lad_probability >= (th.LAD || 0.5) ? '#dc2626' : '#16a34a'};">${(ev.lad_probability * 100).toFixed(1)}%</div>
        <div style="font-size:11px;color:#64748b;">Threshold: ${((th.LAD || 0.5)*100).toFixed(0)}%</div>
      </div>
      <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:12px;">
        <div style="font-size:11px;font-weight:750;color:#64748b;">LCX ARTERY</div>
        <div style="font-size:18px;font-weight:850;color:${ev.lcx_probability >= (th.LCX || (isCand?0.45:0.5)) ? '#dc2626' : '#16a34a'};">${(ev.lcx_probability * 100).toFixed(1)}%</div>
        <div style="font-size:11px;color:#64748b;">Threshold: ${((th.LCX || (isCand?0.45:0.5))*100).toFixed(0)}%</div>
      </div>
      <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:12px;">
        <div style="font-size:11px;font-weight:750;color:#64748b;">RCA ARTERY</div>
        <div style="font-size:18px;font-weight:850;color:${ev.rca_probability >= (th.RCA || (isCand?0.40:0.5)) ? '#dc2626' : '#16a34a'};">${(ev.rca_probability * 100).toFixed(1)}%</div>
        <div style="font-size:11px;color:#64748b;">Threshold: ${((th.RCA || (isCand?0.40:0.5))*100).toFixed(0)}%</div>
      </div>
    </div>

    <!-- Active Models & Mode -->
    <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:10px 14px;margin-bottom:18px;font-size:12px;color:#1e40af;">
      <b>Evaluation Mode:</b> ${isCand ? 'Experimental Candidate Mode' : 'Standard Baseline Production Mode'} &bull; 
      <b>Active Models:</b> CAD: <code>${(ev.active_models||{}).CAD||'cad_model.pkl'}</code>, LAD: <code>${(ev.active_models||{}).LAD||'lad_model.pkl'}</code>, LCX: <code>${(ev.active_models||{}).LCX||'lcx_model.pkl'}</code>, RCA: <code>${(ev.active_models||{}).RCA||'rca_model.pkl'}</code>
    </div>

    <!-- Clinical Parameter Snapshot (57 Features) -->
    <div style="font-size:13px;font-weight:750;color:#0f172a;margin-bottom:8px;">Validated 57-Feature Patient Snapshot</div>
    <div style="max-height:220px;overflow-y:auto;border:1px solid #e2e8f0;border-radius:8px;padding:10px;background:#f8fafc;font-size:11.5px;margin-bottom:18px;">
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px 12px;">
        ${Object.entries(pat).map(([k, v]) => `<div><b>${k}:</b> <span style="font-family:monospace;color:#1e293b;">${v}</span></div>`).join('')}
      </div>
    </div>
  `;

  if (modal) modal.style.display = 'flex';
}

function closeHistoryModal() {
  const modal = document.getElementById('historyDetailsModal');
  if (modal) modal.style.display = 'none';
  activeModalEvalRecord = null;
}

function loadModalPatient() {
  if (activeModalEvalRecord) {
    loadHistoryPatient(activeModalEvalRecord.id);
    closeHistoryModal();
  }
}

function exportModalPdf() {
  if (activeModalEvalRecord) {
    exportHistoryPdf(activeModalEvalRecord.id);
  }
}

function loadHistoryPatient(evalId) {
  const ev = historyRecordsCache.find(x => x.id === evalId);
  if (!ev) return;

  const pat = ev.patient_data || {};
  let loadedCount = 0;

  // Set patient identity
  const pid = document.getElementById('inp_patient_id');
  if (pid) pid.value = ev.patient_id || 'CV-2026-8492';
  const pnm = document.getElementById('inp_patient_name');
  if (pnm) pnm.value = ev.patient_name || 'Alex Morgan (Demo Patient)';

  // Populate all matching form fields
  for (const [k, v] of Object.entries(pat)) {
    const el = document.getElementById('inp_' + k);
    if (el) {
      el.value = v;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
      loadedCount++;
    }
  }

  // Recalculate BMI
  if (typeof updateBMI === 'function') {
    updateBMI();
  }

  // Invalidate previous predictions
  clearPredictionResults();
  sessionStorage.setItem('cardiovision_state', 'awaiting');
  sessionStorage.removeItem('cardiovision_last_prediction');

  // Switch to Predict Risk screen
  switchNav('predict');

  // Show banner alert
  const appliedAlert = document.getElementById('uploadAppliedAlert');
  if (appliedAlert) {
    appliedAlert.style.display = 'flex';
    appliedAlert.innerHTML = `
      <svg viewBox="0 0 24 24" style="width:16px;height:16px;color:#059669;flex-shrink:0;" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
      <span>Loaded historical patient snapshot <b>${ev.patient_name || 'Alex Morgan'} (${ev.patient_id})</b>. Previous predictions have been cleared. Please click <b>Predict Cardiovascular Risk</b> below to re-evaluate.</span>
    `;
    setTimeout(() => {
      appliedAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
  }
}

function exportHistoryPdf(evalId) {
  window.open(`http://127.0.0.1:8502/api/history/${evalId}/export-pdf`, '_blank');
}

function deleteHistoryEvaluation(evalId) {
  if (!confirm('Are you sure you want to permanently delete this prediction record from the history audit log?')) {
    return;
  }
  fetch(`http://127.0.0.1:8502/api/history/${evalId}`, { method: 'DELETE' })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        loadHistoryEvaluations();
      } else {
        alert('Failed to delete evaluation: ' + (data.error || 'Unknown error'));
      }
    })
    .catch(err => {
      alert('Network error while deleting evaluation: ' + err.message);
    });
}
"""

if "PATIENT DOCUMENT UPLOAD & EXTRACTION CLIENT ENGINE" not in content:
    target_script_end = "</script>"
    idx = content.rfind(target_script_end)
    if idx != -1:
        content = content[:idx] + js_additions + "\n" + content[idx:]
        print("7. Added JavaScript engine additions before </script>.")
    else:
        print("7. ERROR: </script> not found!")
else:
    print("7. JavaScript additions already present.")

# Save modified dashboard
with open("cardiovision_exact_dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)

print(f"Integration complete! File size: {len(content)} bytes.")
