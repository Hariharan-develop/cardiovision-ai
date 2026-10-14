with open("cardiovision_exact_dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update CSS
old_css_target = """.extractPill.notFound { background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; }"""
new_css = """.extractPill.notFound { background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; }

#uploadErrorBox:empty,
#uploadAppliedAlert:empty {
  display: none !important;
}
.sourcePageBadge {
  font-size: 11px;
  color: #1e40af;
  font-weight: 700;
  background: #eff6ff;
  padding: 2px 7px;
  border-radius: 4px;
  border: 1px solid #bfdbfe;
  display: inline-block;
}
.sourcePageBadge.calc {
  color: #0369a1;
  background: #f0f9ff;
  border-color: #bae6fd;
}
.snippetQuote {
  font-size: 10.5px;
  color: #64748b;
  font-style: italic;
  margin-top: 3px;
  line-height: 1.35;
  max-width: 280px;
  word-break: break-word;
}"""

if old_css_target in content:
    content = content.replace(old_css_target, new_css, 1)
    print("1. Updated CSS.")
else:
    print("CSS target not found!")

# 2. Update HTML with Overview Metrics Banner
old_html_target = """              <!-- Summary Filter Pills -->
              <div class="extractSummaryPills" id="extractSummaryPills">"""

new_html = """              <!-- Extraction Overview Metric Cards -->
              <div id="extractOverviewBanner" style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px;padding:9px 12px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;margin-bottom:10px;font-size:11.5px;">
                <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;">
                  <span style="color:#15803d;font-weight:700;"><span id="badgeExtractedCount">0</span> Extracted</span>
                  <span style="color:#1d4ed8;font-weight:700;"><span id="badgeCalculatedCount">0</span> Calculated</span>
                  <span style="color:#b45309;font-weight:700;"><span id="badgeNeedsReviewCount">0</span> Needs Review</span>
                  <span style="color:#64748b;font-weight:700;"><span id="badgeNotFoundCount">0</span> Missing</span>
                </div>
                <div id="badgeOcrStatus" style="font-size:11px;padding:2px 8px;border-radius:12px;background:#ede9fe;color:#5b21b6;font-weight:700;">
                  OCR: Direct Text
                </div>
              </div>

              <!-- Summary Filter Pills -->
              <div class="extractSummaryPills" id="extractSummaryPills">"""

if old_html_target in content:
    content = content.replace(old_html_target, new_html, 1)
    print("2. Updated HTML with overview metrics banner.")
else:
    print("HTML target not found!")

# 3. Update JavaScript client engine
js_start = "// PATIENT DOCUMENT UPLOAD & EXTRACTION CLIENT ENGINE"
js_end = "// PREDICTION HISTORY CLIENT ENGINE"

idx_start = content.find(js_start)
idx_end = content.find(js_end)

if idx_start != -1 and idx_end != -1:
    new_js = """// PATIENT DOCUMENT UPLOAD & EXTRACTION CLIENT ENGINE
// ==========================================================================
let currentExtractionResult = null;
let currentReviewFilter = 'all';

function showUploadError(msg) {
  const errBox = document.getElementById('uploadErrorBox');
  const errMsg = document.getElementById('uploadErrorMsg');
  const appliedAlert = document.getElementById('uploadAppliedAlert');
  if (appliedAlert) {
    appliedAlert.innerHTML = '';
    appliedAlert.style.display = 'none';
  }

  if (!msg || typeof msg !== 'string' || !msg.trim()) {
    if (errBox) errBox.style.display = 'none';
    if (errMsg) errMsg.textContent = '';
    return;
  }
  if (errMsg) errMsg.textContent = msg.trim();
  if (errBox) {
    errBox.style.display = 'flex';
    errBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function hideUploadError() {
  const errBox = document.getElementById('uploadErrorBox');
  const errMsg = document.getElementById('uploadErrorMsg');
  if (errMsg) errMsg.textContent = '';
  if (errBox) errBox.style.display = 'none';
}

function showUploadApplied(html) {
  hideUploadError();
  const appliedAlert = document.getElementById('uploadAppliedAlert');
  if (!html || typeof html !== 'string' || !html.trim()) {
    if (appliedAlert) {
      appliedAlert.innerHTML = '';
      appliedAlert.style.display = 'none';
    }
    return;
  }
  if (appliedAlert) {
    appliedAlert.innerHTML = html.trim();
    appliedAlert.style.display = 'flex';
    setTimeout(() => {
      appliedAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 50);
  }
}

function hideUploadApplied() {
  const appliedAlert = document.getElementById('uploadAppliedAlert');
  if (appliedAlert) {
    appliedAlert.innerHTML = '';
    appliedAlert.style.display = 'none';
  }
}

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
  const progBox = document.getElementById('uploadProgressState');
  const progText = document.getElementById('uploadStatusText');
  const dropZone = document.getElementById('uploadDropZone');

  hideUploadError();
  hideUploadApplied();

  if (!allowedExts.includes(ext)) {
    showUploadError(`Unsupported file format '${ext}'. Please upload a clinical PDF (.pdf), Word (.docx) document, or ECG image.`);
    return;
  }

  if (file.size > 20 * 1024 * 1024) {
    showUploadError(`File is too large (${(file.size / (1024*1024)).toFixed(1)} MB). Maximum allowed size is 20 MB.`);
    return;
  }

  if (dropZone) dropZone.style.display = 'none';
  if (progBox) progBox.style.display = 'block';
  if (progText) progText.textContent = `Reading ${file.name} (${(file.size / 1024).toFixed(1)} KB)...`;

  const reader = new FileReader();
  reader.onload = function(e) {
    if (progText) progText.textContent = 'Extracting digital text, laboratory tables & clinical biomarkers...';
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
      let msg = err.message || 'Error parsing medical document';
      if (msg.toLowerCase().includes('scanned')) {
        msg = 'Scanned PDF detected without readable text. The server OCR engine (Tesseract) is unavailable. Please upload a digital text-based PDF or Word document.';
      } else if (msg.toLowerCase().includes('corrupt') || msg.toLowerCase().includes('invalid')) {
        msg = 'The uploaded document appears to be corrupted or invalid. Please check the document and upload a valid PDF or Word report.';
      }
      showUploadError(msg);
    });
  };
  reader.onerror = function() {
    if (progBox) progBox.style.display = 'none';
    if (dropZone) dropZone.style.display = 'block';
    showUploadError('Failed to read local file from your computer.');
  };
  reader.readAsDataURL(file);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderExtractionReview(result, filename) {
  const reviewContainer = document.getElementById('extractionReviewContainer');
  const reviewTbody = document.getElementById('extractionReviewTbody');
  const fnEl = document.getElementById('extractDocFilename');

  hideUploadError();
  hideUploadApplied();

  const pagesCount = result.pages_count || 1;
  const ocrStatus = result.ocr_status || 'not_needed';

  if (fnEl) {
    let metaTxt = `Report: ${filename} • ${pagesCount} Page${pagesCount > 1 ? 's' : ''}`;
    if (ocrStatus === 'performed') metaTxt += ' • OCR Applied';
    else if (ocrStatus === 'unavailable') metaTxt += ' • OCR Unavailable';
    fnEl.textContent = metaTxt;
  }

  const summary = result.summary || {};
  const extractedCount = summary.extracted_count !== undefined ? summary.extracted_count : (result.extracted_count || 0);
  const calculatedCount = summary.calculated_count !== undefined ? summary.calculated_count : (result.calculated_count || 0);
  const needsReviewCount = summary.needs_review_count !== undefined ? summary.needs_review_count : (result.needs_review_count || 0);
  const notFoundCount = summary.not_found_count !== undefined ? summary.not_found_count : (result.not_found_count || 0);
  const totalCount = result.review_items ? result.review_items.length : 57;

  // Update filter pills
  document.getElementById('pillCountAll').textContent = totalCount;
  document.getElementById('pillCountExtracted').textContent = extractedCount;
  document.getElementById('pillCountCalculated').textContent = calculatedCount;
  document.getElementById('pillCountNeedsReview').textContent = needsReviewCount;
  document.getElementById('pillCountNotFound').textContent = notFoundCount;

  // Update overview metrics banner
  const bExt = document.getElementById('badgeExtractedCount');
  if (bExt) bExt.textContent = `${extractedCount} (${Math.round((extractedCount/totalCount)*100)}%)`;
  const bCalc = document.getElementById('badgeCalculatedCount');
  if (bCalc) bCalc.textContent = `${calculatedCount}`;
  const bNR = document.getElementById('badgeNeedsReviewCount');
  if (bNR) bNR.textContent = `${needsReviewCount}`;
  const bNF = document.getElementById('badgeNotFoundCount');
  if (bNF) bNF.textContent = `${notFoundCount}`;
  const bOcr = document.getElementById('badgeOcrStatus');
  if (bOcr) {
    if (ocrStatus === 'performed') {
      bOcr.style.background = '#dcfce7';
      bOcr.style.color = '#15803d';
      bOcr.textContent = 'OCR Engine Applied';
    } else if (ocrStatus === 'unavailable') {
      bOcr.style.background = '#fee2e2';
      bOcr.style.color = '#b91c1c';
      bOcr.textContent = 'Scanned / OCR Missing';
    } else {
      bOcr.style.background = '#ede9fe';
      bOcr.style.color = '#5b21b6';
      bOcr.textContent = 'Digital Text Direct';
    }
  }

  reviewTbody.innerHTML = '';
  const items = result.review_items || [];
  items.forEach(item => {
    const tr = document.createElement('tr');
    tr.className = 'reviewTableRow';
    tr.setAttribute('data-status', item.status);
    tr.setAttribute('data-feat', item.field_key);

    const safeStatus = (item.status || 'Not_Found').replace(/\\s+/g, '_');
    const isAccepted = (item.status === 'Extracted' || item.status === 'Calculated');
    const displayVal = (item.extracted_value !== null && item.extracted_value !== undefined) ? String(item.extracted_value) : '';

    let snippetHtml = '';
    if (item.snippet) {
      snippetHtml = `<div class="snippetQuote" title="Supporting document snippet: ${escapeHtml(item.snippet)}">&ldquo;${escapeHtml(item.snippet)}&rdquo;</div>`;
    }
    let notesHtml = '';
    if (item.notes) {
      notesHtml = `<div style="font-size:10px;color:#b45309;font-weight:600;margin-top:2px;">⚠️ ${escapeHtml(item.notes)}</div>`;
    }

    let pageDisplay = item.source_page || '—';
    let isCalcPage = pageDisplay.toLowerCase().includes('calculated');
    let pageNumOnly = pageDisplay.replace(/page\\s*/i, '').trim();

    let pageBadge;
    if (isCalcPage) {
      pageBadge = `<span class="sourcePageBadge calc" title="Derived calculation">Calculated</span>`;
    } else if (pageDisplay !== '—' && pageNumOnly !== '') {
      pageBadge = `<span class="sourcePageBadge" title="Extracted from Page ${escapeHtml(pageNumOnly)}">${escapeHtml(pageNumOnly)}</span>`;
    } else {
      pageBadge = `<span style="font-size:11px;color:#94a3b8;">&mdash;</span>`;
    }

    tr.innerHTML = `
      <td>
        <div style="font-weight:700;color:#1e293b;">${escapeHtml(item.display_name)}</div>
        <div style="font-size:10px;color:#64748b;font-family:monospace;">${escapeHtml(item.field_key)}</div>
        ${snippetHtml}
      </td>
      <td>
        <input type="text" class="reviewInput reviewRowInput" data-feat="${escapeHtml(item.field_key)}" value="${escapeHtml(displayVal)}" placeholder="&mdash;" oninput="handleReviewInputEdit(this)">
      </td>
      <td>
        <span style="font-size:11px;color:#475569;font-weight:600;">${escapeHtml(item.unit || item.units || '—')}</span>
      </td>
      <td>
        ${pageBadge}
      </td>
      <td>
        <span class="statusBadge ${safeStatus}">${escapeHtml(item.status)}</span>
        ${notesHtml}
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

function handleReviewInputEdit(inp) {
  const row = inp.closest('.reviewTableRow');
  if (!row) return;
  const chk = row.querySelector('.reviewRowAccept');
  if (chk && inp.value.trim() !== '') {
    chk.checked = true;
  }
  const featKey = inp.getAttribute('data-feat');
  if (featKey === 'length' || featKey === 'weight') {
    const lenInp = document.querySelector('.reviewRowInput[data-feat="length"]');
    const wtInp = document.querySelector('.reviewRowInput[data-feat="weight"]');
    const bmiInp = document.querySelector('.reviewRowInput[data-feat="bmi"]');
    if (lenInp && wtInp && bmiInp) {
      const h_cm = parseFloat(lenInp.value);
      const w_kg = parseFloat(wtInp.value);
      if (!isNaN(h_cm) && !isNaN(w_kg) && h_cm > 0) {
        const hm = h_cm / 100.0;
        const newBmi = (w_kg / (hm * hm)).toFixed(1);
        bmiInp.value = newBmi;
        const bmiRow = bmiInp.closest('.reviewTableRow');
        if (bmiRow) {
          const bmiChk = bmiRow.querySelector('.reviewRowAccept');
          if (bmiChk) bmiChk.checked = true;
        }
      }
    }
  }
}

function filterReviewTable(status) {
  currentReviewFilter = status;
  document.querySelectorAll('.extractPill').forEach(p => p.classList.remove('active'));
  const targetPill = document.querySelector(`.extractPill[onclick*="'${status}'"]`);
  if (targetPill) targetPill.classList.add('active');

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
  const fileInput = document.getElementById('reportFileInput');
  if (reviewContainer) reviewContainer.style.display = 'none';
  if (dropZone) dropZone.style.display = 'block';
  hideUploadError();
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
      if (featKey && val !== '' && val !== '—' && val !== 'Not found') {
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
          }, 3500);
          appliedCount++;
        }
      }
    }
  });

  // 3. Recalculate derived fields (e.g. BMI from height and weight)
  if (typeof updateBMI === 'function') {
    updateBMI();
  }

  // 4. Invalidate previous predictions and SHAP results
  clearPredictionResults();
  sessionStorage.setItem('cardiovision_state', 'awaiting');
  sessionStorage.removeItem('cardiovision_last_prediction');
  currentShapData = null;

  // 5. Hide review container
  discardExtraction();

  // 6. Show informative applied banner (never empty)
  const totalCanonicalFields = 57;
  const remainingCount = Math.max(0, totalCanonicalFields - appliedCount);
  const successHtml = `
    <svg viewBox="0 0 24 24" style="width:16px;height:16px;color:#059669;flex-shrink:0;" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
    <span>Successfully applied <b>${appliedCount} extracted clinical parameters</b> to the patient form. <b>${remainingCount} fields</b> remain unpopulated (standard clinical defaults will be used for inference unless manually entered). Previous predictions and SHAP explanations are invalidated. Click <b>Predict Cardiovascular Risk</b> below to run model inference.</span>
  `;
  showUploadApplied(successHtml);
}

"""
    content = content[:idx_start] + new_js + content[idx_end:]
    print("3. Updated JavaScript client engine.")
else:
    print(f"Could not locate JS block: idx_start={idx_start}, idx_end={idx_end}")

with open("cardiovision_exact_dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Saved cardiovision_exact_dashboard.html successfully.")
