# Script to update JavaScript logic in cardiovision_exact_dashboard.html
with open("cardiovision_exact_dashboard.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update markInputsModified to show resStaleNotice
old_mark = """function markInputsModified(){
  if (!inputsModified) {
    inputsModified = true;
    const badge = document.getElementById('predStatusBadge');
    if (badge) {
      badge.className = 'predBadge stale';
      badge.innerHTML = '<span class="badgeDot"></span><span>Inputs Modified — Click Predict to Recalculate</span>';
    }
    const notice = document.getElementById('staleNotice');
    if (notice) {
      notice.style.display = 'flex';
    }
  }
}"""

new_mark = """function markInputsModified(){
  if (!inputsModified) {
    inputsModified = true;
    const badge = document.getElementById('predStatusBadge');
    if (badge) {
      badge.className = 'predBadge stale';
      badge.innerHTML = '<span class="badgeDot"></span><span>Inputs Modified — Click Predict to Recalculate</span>';
    }
    const notice = document.getElementById('staleNotice');
    if (notice) notice.style.display = 'flex';
    const resNotice = document.getElementById('resStaleNotice');
    if (resNotice) resNotice.style.display = 'flex';
  }
}"""

if old_mark in text:
    text = text.replace(old_mark, new_mark, 1)
    print("1. markInputsModified updated.")
else:
    print("WARNING: old_mark not matched exactly.")

# 2. Update applyVisualStyles
old_apply_visual = """function applyVisualStyles(data){
  const cadR = document.getElementById('cadRing');
  if (cadR && data.cad_pct !== undefined) cadR.style.background = 'conic-gradient(#ff4054 0% ' + data.cad_pct + '%, #ffd9dd ' + data.cad_pct + '% 100%)';
  const ladR = document.getElementById('ladRing');
  if (ladR && data.lad_pct !== undefined) ladR.style.background = 'conic-gradient(#2a86ef 0% ' + data.lad_pct + '%, #d5e8fa ' + data.lad_pct + '% 100%)';
  const lcxR = document.getElementById('lcxRing');
  if (lcxR && data.lcx_pct !== undefined) lcxR.style.background = 'conic-gradient(#0fb77d 0% ' + data.lcx_pct + '%, #cfeee2 ' + data.lcx_pct + '% 100%)';
  const rcaR = document.getElementById('rcaRing');
  if (rcaR && data.rca_pct !== undefined) rcaR.style.background = 'conic-gradient(#ff9900 0% ' + data.rca_pct + '%, #f6e5c8 ' + data.rca_pct + '% 100%)';

  const cadBar = document.getElementById('cadBar');
  const cadBarVal = document.getElementById('cadBarVal');
  if (cadBar && cadBarVal && data.cad_risk !== undefined) {
    cadBar.style.height = data.cad_risk + '%';
    cadBarVal.style.bottom = data.cad_risk + '%';
    cadBarVal.textContent = Number(data.cad_risk).toFixed(1);
  }
  const ladBar = document.getElementById('ladBar');
  const ladBarVal = document.getElementById('ladBarVal');
  if (ladBar && ladBarVal && data.lad_risk !== undefined) {
    ladBar.style.height = data.lad_risk + '%';
    ladBarVal.style.bottom = data.lad_risk + '%';
    ladBarVal.textContent = Number(data.lad_risk).toFixed(1);
  }
  const lcxBar = document.getElementById('lcxBar');
  const lcxBarVal = document.getElementById('lcxBarVal');
  if (lcxBar && lcxBarVal && data.lcx_risk !== undefined) {
    lcxBar.style.height = data.lcx_risk + '%';
    lcxBarVal.style.bottom = data.lcx_risk + '%';
    lcxBarVal.textContent = Number(data.lcx_risk).toFixed(1);
  }
  const rcaBar = document.getElementById('rcaBar');
  const rcaBarVal = document.getElementById('rcaBarVal');
  if (rcaBar && rcaBarVal && data.rca_risk !== undefined) {
    rcaBar.style.height = data.rca_risk + '%';
    rcaBarVal.style.bottom = data.rca_risk + '%';
    rcaBarVal.textContent = Number(data.rca_risk).toFixed(1);
  }
}"""

new_apply_visual = """function applyVisualStyles(data){
  // Donut rings in Predict view
  const cadR = document.getElementById('cadRing');
  if (cadR && data.cad_pct !== undefined) cadR.style.background = 'conic-gradient(#ff4054 0% ' + data.cad_pct + '%, #ffd9dd ' + data.cad_pct + '% 100%)';
  const ladR = document.getElementById('ladRing');
  if (ladR && data.lad_pct !== undefined) ladR.style.background = 'conic-gradient(#2a86ef 0% ' + data.lad_pct + '%, #d5e8fa ' + data.lad_pct + '% 100%)';
  const lcxR = document.getElementById('lcxRing');
  if (lcxR && data.lcx_pct !== undefined) lcxR.style.background = 'conic-gradient(#0fb77d 0% ' + data.lcx_pct + '%, #cfeee2 ' + data.lcx_pct + '% 100%)';
  const rcaR = document.getElementById('rcaRing');
  if (rcaR && data.rca_pct !== undefined) rcaR.style.background = 'conic-gradient(#ff9900 0% ' + data.rca_pct + '%, #f6e5c8 ' + data.rca_pct + '% 100%)';

  // Predict view right panel comparison bars
  const cadBar = document.getElementById('cadBar');
  const cadBarVal = document.getElementById('cadBarVal');
  if (cadBar && cadBarVal && data.cad_risk !== undefined) {
    cadBar.style.height = data.cad_risk + '%';
    cadBarVal.style.bottom = data.cad_risk + '%';
    cadBarVal.textContent = Number(data.cad_risk).toFixed(1);
  }
  const ladBar = document.getElementById('ladBar');
  const ladBarVal = document.getElementById('ladBarVal');
  if (ladBar && ladBarVal && data.lad_risk !== undefined) {
    ladBar.style.height = data.lad_risk + '%';
    ladBarVal.style.bottom = data.lad_risk + '%';
    ladBarVal.textContent = Number(data.lad_risk).toFixed(1);
  }
  const lcxBar = document.getElementById('lcxBar');
  const lcxBarVal = document.getElementById('lcxBarVal');
  if (lcxBar && lcxBarVal && data.lcx_risk !== undefined) {
    lcxBar.style.height = data.lcx_risk + '%';
    lcxBarVal.style.bottom = data.lcx_risk + '%';
    lcxBarVal.textContent = Number(data.lcx_risk).toFixed(1);
  }
  const rcaBar = document.getElementById('rcaBar');
  const rcaBarVal = document.getElementById('rcaBarVal');
  if (rcaBar && rcaBarVal && data.rca_risk !== undefined) {
    rcaBar.style.height = data.rca_risk + '%';
    rcaBarVal.style.bottom = data.rca_risk + '%';
    rcaBarVal.textContent = Number(data.rca_risk).toFixed(1);
  }

  // Results & Analysis view: Four Prediction Summary Cards SVG Circular Progress Rings
  const CIRCLE_CIRCUMFERENCE = 188.5; // 2 * pi * 30
  if (data.cad_risk !== undefined) {
    const cadCardPct = document.getElementById('resCadCardPct');
    if (cadCardPct) cadCardPct.textContent = Number(data.cad_risk).toFixed(1) + '%';
    const cadCircleBar = document.getElementById('resCadCircleBar');
    if (cadCircleBar) cadCircleBar.style.strokeDashoffset = (CIRCLE_CIRCUMFERENCE * (1 - data.cad_risk / 100)).toFixed(1);
  }
  if (data.lad_risk !== undefined) {
    const ladCardPct = document.getElementById('resLadCardPct');
    if (ladCardPct) ladCardPct.textContent = Number(data.lad_risk).toFixed(1) + '%';
    const ladCircleBar = document.getElementById('resLadCircleBar');
    if (ladCircleBar) ladCircleBar.style.strokeDashoffset = (CIRCLE_CIRCUMFERENCE * (1 - data.lad_risk / 100)).toFixed(1);
  }
  if (data.lcx_risk !== undefined) {
    const lcxCardPct = document.getElementById('resLcxCardPct');
    if (lcxCardPct) lcxCardPct.textContent = Number(data.lcx_risk).toFixed(1) + '%';
    const lcxCircleBar = document.getElementById('resLcxCircleBar');
    if (lcxCircleBar) lcxCircleBar.style.strokeDashoffset = (CIRCLE_CIRCUMFERENCE * (1 - data.lcx_risk / 100)).toFixed(1);
  }
  if (data.rca_risk !== undefined) {
    const rcaCardPct = document.getElementById('resRcaCardPct');
    if (rcaCardPct) rcaCardPct.textContent = Number(data.rca_risk).toFixed(1) + '%';
    const rcaCircleBar = document.getElementById('resRcaCircleBar');
    if (rcaCircleBar) rcaCircleBar.style.strokeDashoffset = (CIRCLE_CIRCUMFERENCE * (1 - data.rca_risk / 100)).toFixed(1);
  }

  // Results & Analysis view: Comparison Bar Chart
  const chartCadBar = document.getElementById('chartCadBar');
  const chartCadVal = document.getElementById('chartCadVal');
  if (chartCadBar && chartCadVal && data.cad_risk !== undefined) {
    chartCadBar.style.height = Math.max(2, Math.min(100, data.cad_risk)) + '%';
    chartCadVal.textContent = Number(data.cad_risk).toFixed(1) + '%';
  }
  const chartLadBar = document.getElementById('chartLadBar');
  const chartLadVal = document.getElementById('chartLadVal');
  if (chartLadBar && chartLadVal && data.lad_risk !== undefined) {
    chartLadBar.style.height = Math.max(2, Math.min(100, data.lad_risk)) + '%';
    chartLadVal.textContent = Number(data.lad_risk).toFixed(1) + '%';
  }
  const chartLcxBar = document.getElementById('chartLcxBar');
  const chartLcxVal = document.getElementById('chartLcxVal');
  if (chartLcxBar && chartLcxVal && data.lcx_risk !== undefined) {
    chartLcxBar.style.height = Math.max(2, Math.min(100, data.lcx_risk)) + '%';
    chartLcxVal.textContent = Number(data.lcx_risk).toFixed(1) + '%';
  }
  const chartRcaBar = document.getElementById('chartRcaBar');
  const chartRcaVal = document.getElementById('chartRcaVal');
  if (chartRcaBar && chartRcaVal && data.rca_risk !== undefined) {
    chartRcaBar.style.height = Math.max(2, Math.min(100, data.rca_risk)) + '%';
    chartRcaVal.textContent = Number(data.rca_risk).toFixed(1) + '%';
  }

  // Results & Analysis view: Multi-vessel criteria check
  if (data.lad_risk !== undefined && data.lcx_risk !== undefined && data.rca_risk !== undefined) {
    const elevatedCount = [data.lad_risk, data.lcx_risk, data.rca_risk].filter(r => r >= 50.0).length;
    const alertBox = document.getElementById('resMultiVesselAlert');
    const alertTitle = document.getElementById('resMultiVesselTitle');
    const alertText = document.getElementById('resMultiVesselText');
    if (alertBox && alertTitle && alertText) {
      if (elevatedCount >= 2) {
        alertBox.style.background = '#fff7ea';
        alertBox.style.borderLeftColor = '#ff9700';
        alertBox.style.color = '#7a4b00';
        alertTitle.textContent = 'Elevated Model-Estimated Probabilities Across Multiple Vessels';
        alertText.textContent = `Exploratory visualization criteria indicate elevated probability (≥ 50%) across ${elevatedCount} evaluated vessel territories. This represents an exploratory model pattern and is not a clinical diagnosis.`;
      } else if (elevatedCount === 1) {
        alertBox.style.background = '#f0f7ff';
        alertBox.style.borderLeftColor = '#2a86ef';
        alertBox.style.color = '#154e99';
        alertTitle.textContent = 'Elevated Model-Estimated Probability in Single Vascular Territory';
        alertText.textContent = 'Model indicates elevated risk probability (≥ 50%) in 1 anatomical vessel territory. This is an informational model estimate, not confirmed coronary stenosis.';
      } else {
        alertBox.style.background = '#f0fdf4';
        alertBox.style.borderLeftColor = '#10b981';
        alertBox.style.color = '#065f46';
        alertTitle.textContent = 'Model-Estimated Low-Probability Profile Across Evaluated Vessels';
        alertText.textContent = 'Estimated probabilities across all evaluated vessel territories remain below 50% in the current model assessment.';
      }
    }
  }
}"""

if old_apply_visual in text:
    text = text.replace(old_apply_visual, new_apply_visual, 1)
    print("2. applyVisualStyles updated.")
else:
    print("WARNING: old_apply_visual not matched.")

# 3. Update applyPredictions badges
old_apply_pred_tiers = """  // 3. Clinical Probability Tier Badges
  const cadTier = document.getElementById('cadTierBadge');
  if (cadTier && data.cad_tier_class) {
    cadTier.className = 'probTier ' + data.cad_tier_class;
    cadTier.textContent = data.cad_tier_label;
  }
  const ladTier = document.getElementById('ladTierBadge');
  if (ladTier && data.lad_tier_class) {
    ladTier.className = 'probTier ' + data.lad_tier_class;
    ladTier.textContent = data.lad_tier_label;
  }
  const lcxTier = document.getElementById('lcxTierBadge');
  if (lcxTier && data.lcx_tier_class) {
    lcxTier.className = 'probTier ' + data.lcx_tier_class;
    lcxTier.textContent = data.lcx_tier_label;
  }
  const rcaTier = document.getElementById('rcaTierBadge');
  if (rcaTier && data.rca_tier_class) {
    rcaTier.className = 'probTier ' + data.rca_tier_class;
    rcaTier.textContent = data.rca_tier_label;
  }"""

new_apply_pred_tiers = """  // 3. Clinical Probability Tier Badges (Predict View & Results View)
  const cadTier = document.getElementById('cadTierBadge');
  if (cadTier && data.cad_tier_class) {
    cadTier.className = 'probTier ' + data.cad_tier_class;
    cadTier.textContent = data.cad_tier_label;
  }
  const ladTier = document.getElementById('ladTierBadge');
  if (ladTier && data.lad_tier_class) {
    ladTier.className = 'probTier ' + data.lad_tier_class;
    ladTier.textContent = data.lad_tier_label;
  }
  const lcxTier = document.getElementById('lcxTierBadge');
  if (lcxTier && data.lcx_tier_class) {
    lcxTier.className = 'probTier ' + data.lcx_tier_class;
    lcxTier.textContent = data.lcx_tier_label;
  }
  const rcaTier = document.getElementById('rcaTierBadge');
  if (rcaTier && data.rca_tier_class) {
    rcaTier.className = 'probTier ' + data.rca_tier_class;
    rcaTier.textContent = data.rca_tier_label;
  }

  // Update Results View 4-Card Classifications & Tier Badges
  const resCadClass = document.getElementById('resCadClassBadge');
  if (resCadClass && data.cad_label) { resCadClass.textContent = data.cad_label; resCadClass.className = 'resClassBadge cad'; }
  const resLadClass = document.getElementById('resLadClassBadge');
  if (resLadClass && data.lad_label) { resLadClass.textContent = data.lad_label; resLadClass.className = 'resClassBadge lad'; }
  const resLcxClass = document.getElementById('resLcxClassBadge');
  if (resLcxClass && data.lcx_label) { resLcxClass.textContent = data.lcx_label; resLcxClass.className = 'resClassBadge lcx'; }
  const resRcaClass = document.getElementById('resRcaClassBadge');
  if (resRcaClass && data.rca_label) { resRcaClass.textContent = data.rca_label; resRcaClass.className = 'resClassBadge rca'; }

  const resCadTier = document.getElementById('resCadTierBadge');
  if (resCadTier && data.cad_tier_class) { resCadTier.className = 'resTierBadge cad ' + data.cad_tier_class; resCadTier.textContent = data.cad_tier_label; }
  const resLadTier = document.getElementById('resLadTierBadge');
  if (resLadTier && data.lad_tier_class) { resLadTier.className = 'resTierBadge lad ' + data.lad_tier_class; resLadTier.textContent = data.lad_tier_label; }
  const resLcxTier = document.getElementById('resLcxTierBadge');
  if (resLcxTier && data.lcx_tier_class) { resLcxTier.className = 'resTierBadge lcx ' + data.lcx_tier_class; resLcxTier.textContent = data.lcx_tier_label; }
  const resRcaTier = document.getElementById('resRcaTierBadge');
  if (resRcaTier && data.rca_tier_class) { resRcaTier.className = 'resTierBadge rca ' + data.rca_tier_class; resRcaTier.textContent = data.rca_tier_label; }"""

if old_apply_pred_tiers in text:
    text = text.replace(old_apply_pred_tiers, new_apply_pred_tiers, 1)
    print("3. applyPredictions badges updated.")
else:
    print("WARNING: old_apply_pred_tiers not matched.")

# 4. Update clearPredictionResults
old_clear_pred = """  const notice = document.getElementById('staleNotice');
  if (notice) notice.style.display = 'none';"""

new_clear_pred = """  const notice = document.getElementById('staleNotice');
  if (notice) notice.style.display = 'none';
  const resNotice = document.getElementById('resStaleNotice');
  if (resNotice) resNotice.style.display = 'none';"""

if old_clear_pred in text:
    text = text.replace(old_clear_pred, new_clear_pred, 1)

old_clear_bottom = """  // 5. Clear Results & Analysis
  const resSummary = document.getElementById('resRiskSummary');
  if (resSummary) resSummary.textContent = 'Awaiting Prediction — Click Predict to evaluate';
  const resCadVal = document.getElementById('resCadVal');
  if (resCadVal) resCadVal.textContent = '—';
  const resCadLbl = document.getElementById('resCadLbl');
  if (resCadLbl) resCadLbl.textContent = 'Pending';
  const resLadVal = document.getElementById('resLadVal');
  if (resLadVal) resLadVal.textContent = '—';
  const resLadLbl = document.getElementById('resLadLbl');
  if (resLadLbl) resLadLbl.textContent = 'Pending';
  const resLcxVal = document.getElementById('resLcxVal');
  if (resLcxVal) resLcxVal.textContent = '—';
  const resLcxLbl = document.getElementById('resLcxLbl');
  if (resLcxLbl) resLcxLbl.textContent = 'Pending';
  const resRcaVal = document.getElementById('resRcaVal');
  if (resRcaVal) resRcaVal.textContent = '—';
  const resRcaLbl = document.getElementById('resRcaLbl');
  if (resRcaLbl) resRcaLbl.textContent = 'Pending';"""

new_clear_bottom = """  // 5. Clear Results & Analysis
  const resSummary = document.getElementById('resRiskSummary');
  if (resSummary) resSummary.textContent = 'Awaiting Prediction — Click Predict to evaluate';
  const resCadVal = document.getElementById('resCadVal');
  if (resCadVal) resCadVal.textContent = '—';
  const resCadLbl = document.getElementById('resCadLbl');
  if (resCadLbl) resCadLbl.textContent = 'Pending';
  const resLadVal = document.getElementById('resLadVal');
  if (resLadVal) resLadVal.textContent = '—';
  const resLadLbl = document.getElementById('resLadLbl');
  if (resLadLbl) resLadLbl.textContent = 'Pending';
  const resLcxVal = document.getElementById('resLcxVal');
  if (resLcxVal) resLcxVal.textContent = '—';
  const resLcxLbl = document.getElementById('resLcxLbl');
  if (resLcxLbl) resLcxLbl.textContent = 'Pending';
  const resRcaVal = document.getElementById('resRcaVal');
  if (resRcaVal) resRcaVal.textContent = '—';
  const resRcaLbl = document.getElementById('resRcaLbl');
  if (resRcaLbl) resRcaLbl.textContent = 'Pending';

  // Clear Results View 4 Cards & Comparison Chart
  const CIRCLE_CIRC = 188.5;
  ['cad', 'lad', 'lcx', 'rca'].forEach(v => {
    const cardPct = document.getElementById(`res${v.charAt(0).toUpperCase() + v.slice(1)}CardPct`);
    if (cardPct) cardPct.textContent = '—';
    const classBadge = document.getElementById(`res${v.charAt(0).toUpperCase() + v.slice(1)}ClassBadge`);
    if (classBadge) { classBadge.textContent = 'Awaiting'; classBadge.className = 'resClassBadge awaiting'; }
    const tierBadge = document.getElementById(`res${v.charAt(0).toUpperCase() + v.slice(1)}TierBadge`);
    if (tierBadge) { tierBadge.textContent = 'Awaiting Prediction'; tierBadge.className = `resTierBadge ${v} tierAwaiting`; }
    const circleBar = document.getElementById(`res${v.charAt(0).toUpperCase() + v.slice(1)}CircleBar`);
    if (circleBar) circleBar.style.strokeDashoffset = CIRCLE_CIRC.toString();

    const chartBar = document.getElementById(`chart${v.charAt(0).toUpperCase() + v.slice(1)}Bar`);
    if (chartBar) chartBar.style.height = '0%';
    const chartVal = document.getElementById(`chart${v.charAt(0).toUpperCase() + v.slice(1)}Val`);
    if (chartVal) chartVal.textContent = '—';
  });

  const alertBox = document.getElementById('resMultiVesselAlert');
  const alertTitle = document.getElementById('resMultiVesselTitle');
  const alertText = document.getElementById('resMultiVesselText');
  if (alertBox && alertTitle && alertText) {
    alertBox.style.background = '#f8fafc';
    alertBox.style.borderLeftColor = '#94a3b8';
    alertBox.style.color = '#475569';
    alertTitle.textContent = 'Awaiting Model Prediction';
    alertText.textContent = 'Click "Predict Cardiovascular Risk" to calculate multi-vessel probability assessment.';
  }"""

if old_clear_bottom in text:
    text = text.replace(old_clear_bottom, new_clear_bottom, 1)
    print("4. clearPredictionResults updated.")
else:
    print("WARNING: old_clear_bottom not matched.")

# 5. Update renderVisualsFromDOM to also populate the new Results View cards and chart
old_render_dom = """function renderVisualsFromDOM(){
  const cadRing = document.getElementById('cadRing');
  const ladRing = document.getElementById('ladRing');
  const lcxRing = document.getElementById('lcxRing');
  const rcaRing = document.getElementById('rcaRing');

  const cadBar = document.getElementById('cadBar');
  const ladBar = document.getElementById('ladBar');
  const lcxBar = document.getElementById('lcxBar');
  const rcaBar = document.getElementById('rcaBar');

  applyVisualStyles({
    cad_pct: cadRing ? (cadRing.getAttribute('data-pct') || 94) : 94,
    lad_pct: ladRing ? (ladRing.getAttribute('data-pct') || 74) : 74,
    lcx_pct: lcxRing ? (lcxRing.getAttribute('data-pct') || 58) : 58,
    rca_pct: rcaRing ? (rcaRing.getAttribute('data-pct') || 69) : 69,
    cad_risk: cadBar ? parseFloat(cadBar.getAttribute('data-val') || 94.1) : 94.1,
    lad_risk: ladBar ? parseFloat(ladBar.getAttribute('data-val') || 74.0) : 74.0,
    lcx_risk: lcxBar ? parseFloat(lcxBar.getAttribute('data-val') || 58.0) : 58.0,
    rca_risk: rcaBar ? parseFloat(rcaBar.getAttribute('data-val') || 68.6) : 68.6
  });
}"""

new_render_dom = """function renderVisualsFromDOM(){
  const cadRing = document.getElementById('cadRing');
  const ladRing = document.getElementById('ladRing');
  const lcxRing = document.getElementById('lcxRing');
  const rcaRing = document.getElementById('rcaRing');

  const cadBar = document.getElementById('cadBar');
  const ladBar = document.getElementById('ladBar');
  const lcxBar = document.getElementById('lcxBar');
  const rcaBar = document.getElementById('rcaBar');

  const cadVal = cadBar ? parseFloat(cadBar.getAttribute('data-val') || 94.1) : 94.1;
  const ladVal = ladBar ? parseFloat(ladBar.getAttribute('data-val') || 74.0) : 74.0;
  const lcxVal = lcxBar ? parseFloat(lcxBar.getAttribute('data-val') || 58.0) : 58.0;
  const rcaVal = rcaBar ? parseFloat(rcaBar.getAttribute('data-val') || 68.6) : 68.6;

  applyVisualStyles({
    cad_pct: cadRing ? (cadRing.getAttribute('data-pct') || Math.round(cadVal)) : Math.round(cadVal),
    lad_pct: ladRing ? (ladRing.getAttribute('data-pct') || Math.round(ladVal)) : Math.round(ladVal),
    lcx_pct: lcxRing ? (lcxRing.getAttribute('data-pct') || Math.round(lcxVal)) : Math.round(lcxVal),
    rca_pct: rcaRing ? (rcaRing.getAttribute('data-pct') || Math.round(rcaVal)) : Math.round(rcaVal),
    cad_risk: cadVal,
    lad_risk: ladVal,
    lcx_risk: lcxVal,
    rca_risk: rcaVal
  });
}"""

if old_render_dom in text:
    text = text.replace(old_render_dom, new_render_dom, 1)
    print("5. renderVisualsFromDOM updated.")
else:
    print("WARNING: old_render_dom not matched.")

# 6. Update exportClinicalReport to comply strictly with Requirement 9
old_export_fn = text[text.find('function exportClinicalReport(){'):text.find('function sendNavigate(search){')]

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

  const cadRisk = document.getElementById('cadRiskNum')?.textContent || '94.1%';
  const cadLbl = document.getElementById('cadLabelText')?.textContent || 'CAD Present';
  const ladRisk = document.getElementById('ladRiskNum')?.textContent || '74.0%';
  const ladLbl = document.getElementById('ladLabelText')?.textContent || 'Significant Stenosis';
  const lcxRisk = document.getElementById('lcxRiskNum')?.textContent || '58.0%';
  const lcxLbl = document.getElementById('lcxLabelText')?.textContent || 'Significant Stenosis';
  const rcaRisk = document.getElementById('rcaRiskNum')?.textContent || '68.6%';
  const rcaLbl = document.getElementById('rcaLabelText')?.textContent || 'Significant Stenosis';

  const reportDate = new Date().toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });

  const reportHtml = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CardioVision AI - Research Evaluation Report - ${pat.id}</title>
<style>
  @page { size: letter; margin: 16mm 14mm; }
  * { box-sizing: border-box; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #1e293b; background: #fff; margin: 0; padding: 24px; font-size: 13px; line-height: 1.45; }
  .header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #1759e8; padding-bottom: 14px; margin-bottom: 18px; }
  .brand { display: flex; align-items: center; gap: 12px; }
  .logoSvg { width: 38px; height: 38px; color: #1759e8; }
  .brandTitle { font-size: 22px; font-weight: 800; color: #0b2b5b; margin: 0; }
  .brandSub { font-size: 11.5px; color: #64748b; margin: 2px 0 0; }
  .protoBadge { display: inline-block; background: #fef3c7; color: #92400e; border: 1px solid #fde68a; font-size: 10px; font-weight: 750; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; margin-top: 4px; }
  .reportMeta { text-align: right; font-size: 11px; color: #475569; }
  .reportId { font-family: monospace; font-size: 13px; font-weight: 700; color: #1759e8; background: #eef4ff; padding: 2px 8px; border-radius: 4px; display: inline-block; margin-top: 4px; }
  
  .patientCard { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; margin-bottom: 18px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
  .metaItem { display: flex; flex-direction: column; gap: 2px; }
  .metaItem label { font-size: 10px; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.5px; }
  .metaItem span { font-size: 13px; font-weight: 600; color: #0f172a; }
  
  h3 { font-size: 13.5px; font-weight: 800; color: #0b2b5b; margin: 18px 0 8px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; }
  
  .riskGrid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 18px; }
  .riskBox { border-radius: 8px; padding: 12px; border: 1px solid #e2e8f0; background: #fff; text-align: center; }
  .riskBox.cad { border-color: #fecaca; background: #fff5f5; }
  .riskBox.lad { border-color: #bfdbfe; background: #eff6ff; }
  .riskBox.lcx { border-color: #bbf7d0; background: #f0fdf4; }
  .riskBox.rca { border-color: #fed7aa; background: #fff7ed; }
  .riskTitle { font-size: 11px; font-weight: 700; color: #475569; margin-bottom: 4px; text-transform: uppercase; }
  .riskNum { font-size: 22px; font-weight: 800; margin: 2px 0; }
  .riskBox.cad .riskNum { color: #dc2626; }
  .riskBox.lad .riskNum { color: #2563eb; }
  .riskBox.lcx .riskNum { color: #16a34a; }
  .riskBox.rca .riskNum { color: #ea580c; }
  .riskLbl { font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 4px; display: inline-block; }
  .riskBox.cad .riskLbl { background: #fee2e2; color: #b91c1c; }
  .riskBox.lad .riskLbl { background: #dbeafe; color: #1d4ed8; }
  .riskBox.lcx .riskLbl { background: #dcfce7; color: #15803d; }
  .riskBox.rca .riskLbl { background: #ffedd5; color: #c2410c; }
  
  table { width: 100%; border-collapse: collapse; margin-bottom: 16px; font-size: 11.5px; }
  th { background: #f1f5f9; text-align: left; padding: 6px 10px; font-weight: 700; color: #334155; border: 1px solid #e2e8f0; }
  td { padding: 6px 10px; border: 1px solid #e2e8f0; color: #1e293b; }
  tr:nth-child(even) td { background: #f8fafc; }
  
  .guidanceBox { background: #f0f6fc; border: 1px solid #cce0f5; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; font-size: 12px; color: #1e3a5f; }
  .guidanceBox ul { margin: 6px 0 0; padding-left: 18px; }
  .guidanceBox li { margin-bottom: 4px; }
  
  .perfNote { background: #fffbeb; border: 1px solid #fde68a; border-left: 4px solid #f59e0b; padding: 8px 12px; font-size: 11px; color: #92400e; margin-top: 8px; }
  
  .disclaimer { font-size: 10.5px; color: #64748b; line-height: 1.45; border-top: 1px solid #e2e8f0; padding-top: 10px; margin-top: 20px; }
  
  @media print {
    body { padding: 0; }
    .noPrint { display: none !important; }
  }
</style>
</head>
<body>
<div class="noPrint" style="margin-bottom:16px;display:flex;justify-content:flex-end;gap:10px;">
  <button onclick="window.print()" style="padding:8px 18px;background:#1759e8;color:white;border:none;border-radius:6px;font-weight:700;cursor:pointer;">Print / Save as PDF</button>
  <button onclick="window.close()" style="padding:8px 18px;background:#e2e8f0;color:#334155;border:none;border-radius:6px;font-weight:700;cursor:pointer;">Close</button>
</div>

<div class="header">
  <div class="brand">
    <svg class="logoSvg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8Z"/></svg>
    <div>
      <h1 class="brandTitle">CardioVision AI</h1>
      <div class="brandSub">Multi-Vessel Risk Assessment &amp; Clinical Vector Evaluation</div>
      <div class="protoBadge">Research Prototype Evaluation Report — Not for Clinical Diagnosis</div>
    </div>
  </div>
  <div class="reportMeta">
    <div><b>Evaluation Date:</b> ${reportDate}</div>
    <div><b>Patient ID:</b> <span class="reportId">${pat.id}</span></div>
    <div><b>Architecture:</b> 57-Feature Four-Model Architecture</div>
  </div>
</div>

<div class="patientCard">
  <div class="metaItem">
    <label>Patient Name</label>
    <span>${pat.displayName}</span>
  </div>
  <div class="metaItem">
    <label>Patient ID</label>
    <span style="font-family:monospace;color:#1759e8;">${pat.id}</span>
  </div>
  <div class="metaItem">
    <label>Age / Biological Sex</label>
    <span>${age} years / ${sex}</span>
  </div>
  <div class="metaItem">
    <label>Height / Weight / BMI</label>
    <span>${length} cm / ${weight} kg (${bmi} kg/m²)</span>
  </div>
</div>

<h3>1. Machine Learning Multi-Vessel Risk Probabilities</h3>
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

<h3>2. Clinical Input Measurements Summary</h3>
<table>
  <thead>
    <tr><th>Parameter</th><th>Patient Value</th><th>Standard Clinical Reference</th><th>Informational Status</th></tr>
  </thead>
  <tbody>
    <tr><td><b>Blood Pressure (BP, Systolic)</b></td><td>${bp} mmHg</td><td>&lt; 120 mmHg (resting systolic only; diastolic not recorded)</td><td>${parseFloat(bp) >= 130 ? 'Above standard systolic reference (≥ 130 mmHg, Informational)' : parseFloat(bp) >= 120 ? 'Elevated systolic reference (120–129 mmHg, Informational)' : 'Within standard systolic reference'}</td></tr>
    <tr><td><b>Resting Pulse Rate (PR)</b></td><td>${pr} bpm</td><td>60 – 100 bpm</td><td>${parseFloat(pr) >= 60 && parseFloat(pr) <= 100 ? 'Within standard resting range' : 'Outside standard resting range (Informational)'}</td></tr>
    <tr><td><b>Left Ventricular EF (EF-TTE)</b></td><td>${ef}%</td><td>&ge; 50%</td><td>${parseFloat(ef) >= 50 ? 'Preserved EF' : 'Below standard reference (Informational)'}</td></tr>
    <tr><td><b>Fasting Blood Sugar (FBS)</b></td><td>${fbs} mg/dL</td><td>70 – 99 mg/dL</td><td>${parseFloat(fbs) >= 126 ? 'Above standard fasting threshold (≥ 126 mg/dL, Informational)' : parseFloat(fbs) >= 100 ? 'Above standard fasting range (100–125 mg/dL, Informational)' : 'Within standard fasting range'}</td></tr>
    <tr><td><b>Serum Creatinine (CR)</b></td><td>${cr} mg/dL</td><td>0.7 – 1.3 mg/dL</td><td>Renal clearance indicator (Informational)</td></tr>
    <tr><td><b>LDL Cholesterol</b></td><td>${ldl} mg/dL</td><td>&lt; 100 mg/dL</td><td>${parseFloat(ldl) >= 100 ? 'Above standard reference (≥ 100 mg/dL, Informational)' : 'Within standard reference'}</td></tr>
    <tr><td><b>HDL Cholesterol</b></td><td>${hdl} mg/dL</td><td>&gt; 40 mg/dL (M) / &gt; 50 mg/dL (F)</td><td>${parseFloat(hdl) < 40 ? 'Below standard reference (Informational)' : 'Within standard reference'}</td></tr>
    <tr><td><b>Triglycerides (TG)</b></td><td>${tg} mg/dL</td><td>&lt; 150 mg/dL</td><td>${parseFloat(tg) >= 150 ? 'Above standard reference (Informational)' : 'Within standard reference'}</td></tr>
    <tr><td><b>Evaluated Features</b></td><td>57 Model Inputs</td><td>Standardized 7-domain feature vector</td><td>Complete patient feature synchronization</td></tr>
  </tbody>
</table>

<h3>3. Model Validation Performance &amp; Reliability</h3>
<table>
  <thead>
    <tr><th>Model</th><th>Target Vascular Outcome</th><th>Accuracy</th><th>F1 Score</th><th>ROC-AUC</th></tr>
  </thead>
  <tbody>
    <tr><td><b>CAD Model</b></td><td>Overall Coronary Artery Disease</td><td>85.2%</td><td>89.7%</td><td>0.917</td></tr>
    <tr><td><b>LAD Model</b></td><td>Left Anterior Descending Stenosis</td><td>65.6%</td><td>67.7%</td><td>0.756</td></tr>
    <tr><td><b>LCX Model</b></td><td>Left Circumflex Stenosis</td><td>57.4%</td><td>53.6%</td><td>0.584</td></tr>
    <tr><td><b>RCA Model</b></td><td>Right Coronary Artery Stenosis</td><td>60.7%</td><td>50.0%</td><td>0.652</td></tr>
  </tbody>
</table>
<div class="perfNote">
  <b>Model Reliability Notice:</b> LCX and RCA models have limited predictive discrimination in current validation results (ROC-AUC 0.584 and 0.652). Predictions should be interpreted cautiously and must not guide clinical care independently.
</div>

<h3>4. Educational Guidance &amp; Interpretation</h3>
<div class="guidanceBox">
  <b>Scope of Evaluation &amp; Clinical Considerations:</b>
  <ul>
    <li>Predictions represent statistical model estimates derived from patient input vectors and are not clinical diagnoses.</li>
    <li>Results require interpretation by a qualified physician in full clinical context.</li>
    <li>Actual coronary anatomy and luminal patency cannot be confirmed from machine learning probabilities alone.</li>
    <li>Diagnostic testing and management decisions depend on patient symptoms, physical examination, comprehensive history, and professional medical assessment.</li>
  </ul>
</div>

<div class="disclaimer">
  <b>RESEARCH PROTOTYPE DISCLAIMER — NOT A MEDICAL DEVICE:</b><br>
  This report was generated by the CardioVision AI research prototype for educational and decision-support demonstration purposes only. The application is not certified for independent diagnostic use, treatment decision-making, or medication prescription. Model probabilities and classifications do not substitute for formal diagnostic coronary imaging, physician examination, or qualified medical judgment.
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
}"""

if old_export_fn in text:
    text = text.replace(old_export_fn, new_export_fn, 1)
    print("6. exportClinicalReport updated.")
else:
    print("WARNING: old_export_fn not matched.")

with open("cardiovision_exact_dashboard.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Part 2 JS updates completed.")
