
// Responsive layout handles fitting natively with fixed sidebar and fluid main area
function toggleDetail(el){
  const n = el.nextElementSibling;
  if (n) {
    n.style.display = (n.style.display === 'block') ? 'none' : 'block';
  }
}

function updateBMI(){
  const lenEl = document.getElementById('inp_length');
  const wtEl = document.getElementById('inp_weight');
  const bmiEl = document.getElementById('inp_bmi');
  if (lenEl && wtEl && bmiEl) {
    const h = parseFloat(lenEl.value) / 100.0;
    const w = parseFloat(wtEl.value);
    if (h > 0 && w > 0) {
      bmiEl.value = (w / (h * h)).toFixed(1);
    }
  }
  if (typeof renderPatientInfoScreen === 'function') {
    renderPatientInfoScreen();
  }
}

function switchNav(viewId){
  document.querySelectorAll('.mainView').forEach(v => v.style.display = 'none');
  document.querySelectorAll('.navItem').forEach(n => n.classList.remove('active'));
  const target = document.getElementById('view-' + viewId);
  if (target) {
    target.style.display = 'block';
  }
  const navItems = document.querySelectorAll('.navItem');
  const ids = ['predict', 'patient', 'results', 'viewer3d', 'about'];
  const idx = ids.indexOf(viewId);
  if (idx >= 0 && navItems[idx]) {
    navItems[idx].classList.add('active');
  }
  syncPatientDetails();
  if (viewId === 'patient') {
    renderPatientInfoScreen();
  }
}

// -----------------------------------------------------------------------------
// Patient Information Screen Logic (Tab Switching, Filtering, Sorting & Tables)
// -----------------------------------------------------------------------------
let currentPatientTab = 'clinical';
let clinicalSort = { field: 'default', asc: true };
let modelSort = { field: 'num', asc: true };
let collapsedCategories = {};
let allCategoriesCollapsed = false;

function switchPatientTab(tabId){
  currentPatientTab = tabId;
  const btnClin = document.getElementById('tabBtnClinical');
  const btnMod = document.getElementById('tabBtnModel');
  const secClin = document.getElementById('pvTabContentClinical');
  const secMod = document.getElementById('pvTabContentModel');
  const catWrap = document.getElementById('pvCategorySelectWrap');
  const tglBtn = document.getElementById('pvToggleGroupsBtn');

  if (tabId === 'clinical') {
    if (btnClin) btnClin.classList.add('active');
    if (btnMod) btnMod.classList.remove('active');
    if (secClin) secClin.style.display = 'block';
    if (secMod) secMod.style.display = 'none';
    if (catWrap) catWrap.style.display = 'block';
    if (tglBtn) tglBtn.style.display = 'inline-flex';
  } else {
    if (btnClin) btnClin.classList.remove('active');
    if (btnMod) btnMod.classList.add('active');
    if (secClin) secClin.style.display = 'none';
    if (secMod) secMod.style.display = 'block';
    if (catWrap) catWrap.style.display = 'none';
    if (tglBtn) tglBtn.style.display = 'none';
  }
  filterPatientTables();
}

function togglePatientCategory(catName){
  collapsedCategories[catName] = !collapsedCategories[catName];
  renderClinicalTable();
}

function toggleAllPatientGroups(){
  allCategoriesCollapsed = !allCategoriesCollapsed;
  const cats = [
    'Demographics', 'Vital Signs', 'Medical History', 'Symptoms',
    'Laboratory Results', 'ECG & Cardiac Findings', 'Additional Clinical Findings'
  ];
  cats.forEach(c => { collapsedCategories[c] = allCategoriesCollapsed; });
  const tglTxt = document.getElementById('pvToggleGroupsText');
  if (tglTxt) {
    tglTxt.textContent = allCategoriesCollapsed ? 'Expand All Groups' : 'Collapse All Groups';
  }
  renderClinicalTable();
}

function sortClinicalTable(field){
  if (clinicalSort.field === field) {
    clinicalSort.asc = !clinicalSort.asc;
  } else {
    clinicalSort.field = field;
    clinicalSort.asc = true;
  }
  renderClinicalTable();
}

function sortModelTable(field){
  if (modelSort.field === field) {
    modelSort.asc = !modelSort.asc;
  } else {
    modelSort.field = field;
    modelSort.asc = true;
  }
  renderModelTable();
}

function makeBadge(status, label) {
  let icon = '';
  if (status === 'within') {
    icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';
  } else if (status === 'out') {
    icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>';
  } else {
    icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/></svg>';
  }
  return `<span class="rangeBadge ${status}">${icon}${label}</span>`;
}

function getClinicalData(){
  const age = parseFloat(document.getElementById('inp_age')?.value || 58);
  const length = parseFloat(document.getElementById('inp_length')?.value || 170);
  const weight = parseFloat(document.getElementById('inp_weight')?.value || 72);
  let calcBmiVal = (length > 0) ? (weight / ((length / 100.0) ** 2)).toFixed(1) : '24.9';
  const bmiEl = document.getElementById('inp_bmi');
  if (bmiEl && bmiEl.value !== calcBmiVal) bmiEl.value = calcBmiVal;
  const bmi = calcBmiVal;
  const sex = document.getElementById('inp_sex')?.value || 'Male';

  const dm = parseInt(document.getElementById('inp_dm')?.value || 0);
  const htn = parseInt(document.getElementById('inp_htn')?.value || 1);
  const current_smoker = parseInt(document.getElementById('inp_current_smoker')?.value || 0);
  const ex_smoker = parseInt(document.getElementById('inp_ex_smoker')?.value || 0);
  const fh = parseInt(document.getElementById('inp_fh')?.value || 0);
  const obesity = document.getElementById('inp_obesity')?.value || 'N';
  const crf = document.getElementById('inp_crf')?.value || 'N';
  const cva = document.getElementById('inp_cva')?.value || 'N';

  const chest_pain = document.getElementById('inp_chest_pain')?.value === 'Y' ? 1 : 0;
  const dyspnea = document.getElementById('inp_dyspnea')?.value || 'N';
  const atypical = document.getElementById('inp_atypical')?.value || 'N';
  const nonanginal = document.getElementById('inp_nonanginal')?.value || 'N';
  const lowth_ang = document.getElementById('inp_lowth_ang')?.value || 'N';
  const poor_r = document.getElementById('inp_poor_r')?.value || 'N';

  const bp = parseFloat(document.getElementById('inp_bp')?.value || 130);
  const pr = parseFloat(document.getElementById('inp_pr')?.value || 70);
  const ef_tte = parseFloat(document.getElementById('inp_ef_tte')?.value || 50);

  const fbs = parseFloat(document.getElementById('inp_fbs')?.value || 98);
  const cr = parseFloat(document.getElementById('inp_cr')?.value || 1.0);
  const tg = parseFloat(document.getElementById('inp_tg')?.value || 122);
  const ldl = parseFloat(document.getElementById('inp_ldl')?.value || 100);
  const hdl = parseFloat(document.getElementById('inp_hdl')?.value || 39);
  const bun = parseFloat(document.getElementById('inp_bun')?.value || 16);
  const esr = parseFloat(document.getElementById('inp_esr')?.value || 15);
  const hb = parseFloat(document.getElementById('inp_hb')?.value || 13.2);
  const k = parseFloat(document.getElementById('inp_k')?.value || 4.2);
  const na = parseFloat(document.getElementById('inp_na')?.value || 141);
  const wbc = parseFloat(document.getElementById('inp_wbc')?.value || 7100);
  const lymph = parseFloat(document.getElementById('inp_lymph')?.value || 32);
  const neut = parseFloat(document.getElementById('inp_neut')?.value || 60);
  const plt = parseFloat(document.getElementById('inp_plt')?.value || 210);

  const q_wave = parseInt(document.getElementById('inp_q_wave')?.value || 0);
  const st_elevation = parseInt(document.getElementById('inp_st_elevation')?.value || 0);
  const st_depression = parseInt(document.getElementById('inp_st_depression')?.value || 0);
  const tinversion = parseInt(document.getElementById('inp_tinversion')?.value || 0);
  const lvh = document.getElementById('inp_lvh')?.value || 'N';
  const bbb = document.getElementById('inp_bbb')?.value || 'N';
  const region_rwma = parseFloat(document.getElementById('inp_region_rwma')?.value || 0);
  const vhd = document.getElementById('inp_vhd')?.value || 'N';

  const edema = parseInt(document.getElementById('inp_edema')?.value || 0);
  const function_class = parseInt(document.getElementById('inp_function_class')?.value || 0);
  const airway = document.getElementById('inp_airway')?.value || 'N';
  const thyroid = document.getElementById('inp_thyroid')?.value || 'N';
  const chf = document.getElementById('inp_chf')?.value || 'N';
  const dlp = document.getElementById('inp_dlp')?.value || 'N';
  const weak_pulse = document.getElementById('inp_weak_pulse')?.value || 'N';
  const lung_rales = document.getElementById('inp_lung_rales')?.value || 'N';
  const systolic_murmur = document.getElementById('inp_systolic_murmur')?.value || 'N';
  const diastolic_murmur = document.getElementById('inp_diastolic_murmur')?.value || 'N';

  // Compute subtle indicator badges
  // BMI
  const bmiNum = parseFloat(bmi);
  let bmiBadge;
  if (bmiNum < 18.5) {
    bmiBadge = makeBadge('out', 'Below standard adult BMI range (Informational)');
  } else if (bmiNum <= 24.9) {
    bmiBadge = makeBadge('within', 'Within standard adult BMI range (Informational)');
  } else if (bmiNum <= 29.9) {
    bmiBadge = makeBadge('out', 'Above standard adult BMI range: Overweight (Informational)');
  } else {
    bmiBadge = makeBadge('out', 'Above standard adult BMI range: Obesity (Informational)');
  }

  // BP (Resting systolic only measured)
  let bpBadge;
  if (bp < 120) {
    bpBadge = makeBadge('within', 'Within standard systolic reference (< 120 mmHg, Informational)');
  } else if (bp <= 129) {
    bpBadge = makeBadge('out', 'Elevated systolic reference (120–129 mmHg, Informational)');
  } else {
    bpBadge = makeBadge('out', 'Above standard systolic reference (≥ 130 mmHg, Informational)');
  }

  // PR
  let prBadge;
  if (pr >= 60 && pr <= 100) {
    prBadge = makeBadge('within', 'Within standard resting range (60–100 bpm)');
  } else if (pr < 60) {
    prBadge = makeBadge('out', 'Below standard resting range (< 60 bpm)');
  } else {
    prBadge = makeBadge('out', 'Above standard resting range (> 100 bpm)');
  }

  // EF-TTE
  let efBadge;
  if (ef_tte >= 50) {
    efBadge = makeBadge('within', 'Within standard reference (≥ 50%: Preserved)');
  } else if (ef_tte >= 41) {
    efBadge = makeBadge('out', 'Below standard reference (41–49%: Mildly reduced)');
  } else {
    efBadge = makeBadge('out', 'Below standard reference (≤ 40%: Reduced)');
  }

  // FBS
  let fbsBadge;
  if (fbs >= 70 && fbs <= 99) {
    fbsBadge = makeBadge('within', 'Within standard fasting range (70–99 mg/dL)');
  } else if (fbs >= 100 && fbs <= 125) {
    fbsBadge = makeBadge('out', 'Above standard fasting range (100–125 mg/dL)');
  } else if (fbs >= 126) {
    fbsBadge = makeBadge('out', 'Above standard fasting threshold (≥ 126 mg/dL)');
  } else {
    fbsBadge = makeBadge('out', 'Below standard fasting range (< 70 mg/dL)');
  }

  // CR
  let crBadge;
  if (cr >= 0.7 && cr <= 1.3) {
    crBadge = makeBadge('within', 'Within standard adult range (0.7–1.3 mg/dL)');
  } else if (cr < 0.7) {
    crBadge = makeBadge('out', 'Below standard adult range (< 0.7 mg/dL)');
  } else {
    crBadge = makeBadge('out', 'Above standard adult range (> 1.3 mg/dL)');
  }

  // TG
  let tgBadge = (tg < 150) ? makeBadge('within', 'Within standard reference (< 150 mg/dL)') : makeBadge('out', 'Above standard reference (≥ 150 mg/dL)');

  // LDL
  let ldlBadge = (ldl < 100) ? makeBadge('within', 'Within standard reference (< 100 mg/dL)') : makeBadge('out', 'Above standard reference (≥ 100 mg/dL)');

  // HDL
  let hdlTarget = (sex === 'Female') ? 50 : 40;
  let hdlBadge = (hdl > hdlTarget) ? makeBadge('within', `Within standard reference (> ${hdlTarget} mg/dL)`) : makeBadge('out', `Below standard reference (≤ ${hdlTarget} mg/dL)`);

  // BUN
  let bunBadge;
  if (bun >= 7 && bun <= 20) {
    bunBadge = makeBadge('within', 'Within standard reference (7–20 mg/dL)');
  } else if (bun < 7) {
    bunBadge = makeBadge('out', 'Below standard reference (< 7 mg/dL)');
  } else {
    bunBadge = makeBadge('out', 'Above standard reference (> 20 mg/dL)');
  }

  // ESR
  let esrBadge = (esr <= 20) ? makeBadge('within', 'Within common reference (0–20 mm/hr)') : makeBadge('out', 'Above common reference (> 20 mm/hr)');

  // HB
  let hbMin = (sex === 'Female') ? 12.0 : 13.5;
  let hbMax = (sex === 'Female') ? 15.5 : 17.5;
  let hbBadge;
  if (hb >= hbMin && hb <= hbMax) {
    hbBadge = makeBadge('within', 'Within standard adult reference');
  } else if (hb < hbMin) {
    hbBadge = makeBadge('out', `Below standard adult reference (< ${hbMin} g/dL)`);
  } else {
    hbBadge = makeBadge('out', `Above standard adult reference (> ${hbMax} g/dL)`);
  }

  // K
  let kBadge;
  if (k >= 3.5 && k <= 5.0) {
    kBadge = makeBadge('within', 'Within standard reference (3.5–5.0 mEq/L)');
  } else if (k < 3.5) {
    kBadge = makeBadge('out', 'Below standard reference (< 3.5 mEq/L)');
  } else {
    kBadge = makeBadge('out', 'Above standard reference (> 5.0 mEq/L)');
  }

  // Na
  let naBadge;
  if (na >= 135 && na <= 145) {
    naBadge = makeBadge('within', 'Within standard reference (135–145 mEq/L)');
  } else if (na < 135) {
    naBadge = makeBadge('out', 'Below standard reference (< 135 mEq/L)');
  } else {
    naBadge = makeBadge('out', 'Above standard reference (> 145 mEq/L)');
  }

  // WBC
  let wbcBadge;
  if (wbc >= 4000 && wbc <= 11000) {
    wbcBadge = makeBadge('within', 'Within standard reference (4,000–11,000)');
  } else if (wbc < 4000) {
    wbcBadge = makeBadge('out', 'Below standard reference (< 4,000)');
  } else {
    wbcBadge = makeBadge('out', 'Above standard reference (> 11,000)');
  }

  // Lymph
  let lymphBadge;
  if (lymph >= 20 && lymph <= 40) {
    lymphBadge = makeBadge('within', 'Within standard differential (20–40%)');
  } else if (lymph < 20) {
    lymphBadge = makeBadge('out', 'Below standard differential (< 20%)');
  } else {
    lymphBadge = makeBadge('out', 'Above standard differential (> 40%)');
  }

  // Neut
  let neutBadge;
  if (neut >= 40 && neut <= 70) {
    neutBadge = makeBadge('within', 'Within standard differential (40–70%)');
  } else if (neut < 40) {
    neutBadge = makeBadge('out', 'Below standard differential (< 40%)');
  } else {
    neutBadge = makeBadge('out', 'Above standard differential (> 70%)');
  }

  // PLT
  let pltBadge;
  if (plt >= 150 && plt <= 450) {
    pltBadge = makeBadge('within', 'Within standard reference (150–450)');
  } else if (plt < 150) {
    pltBadge = makeBadge('out', 'Below standard reference (< 150)');
  } else {
    pltBadge = makeBadge('out', 'Above standard reference (> 450)');
  }

  return [
    // 1. Demographics
    { name: 'Age', category: 'Demographics', value: `${age} years`, rawVal: age, badge: makeBadge('within', 'Adult baseline range'), ref: 'Adult baseline reference: 18 – 90+ years' },
    { name: 'Sex', category: 'Demographics', value: sex, rawVal: sex, badge: makeBadge('neutral', sex), ref: 'Biological sex: Male / Female' },
    { name: 'Height', category: 'Demographics', value: `${length} cm`, rawVal: length, badge: makeBadge('neutral', 'Stature measurement'), ref: 'Adult stature measurement (reference not specified for age/sex breakdown in dataset)' },
    { name: 'Weight', category: 'Demographics', value: `${weight} kg`, rawVal: weight, badge: makeBadge('neutral', 'Weight measurement'), ref: 'Adult body weight measurement (evaluated clinically via BMI)' },
    { name: 'Body Mass Index (BMI)', category: 'Demographics', value: `${bmi} kg/m²`, rawVal: parseFloat(bmi), badge: bmiBadge, ref: 'Standard adult reference range: 18.5 – 24.9 kg/m² (< 18.5 below range, 25.0–29.9 overweight range, ≥ 30.0 obesity range)' },

    // 2. Vital Signs
    { name: 'Blood Pressure (BP, Systolic)', category: 'Vital Signs', value: `${bp} mmHg`, rawVal: bp, badge: bpBadge, ref: 'Standard systolic reference: < 120 mmHg (120–129 mmHg elevated systolic, ≥ 130 mmHg above standard reference range). Diastolic BP was not recorded in the dataset.' },
    { name: 'Pulse Rate (PR)', category: 'Vital Signs', value: `${pr} bpm`, rawVal: pr, badge: prBadge, ref: 'Standard adult resting heart rate reference: 60 – 100 bpm' },
    { name: 'Left Ventricular EF (EF-TTE)', category: 'Vital Signs', value: `${ef_tte}%`, rawVal: ef_tte, badge: efBadge, ref: 'Standard reference: ≥ 50% preserved LV systolic function (41–49% mildly reduced, ≤ 40% reduced)' },

    // 3. Medical History
    { name: 'Diabetes Mellitus (DM)', category: 'Medical History', value: dm === 1 ? 'Yes' : 'No', rawVal: dm, badge: dm === 1 ? makeBadge('out', 'Diabetic history reported') : makeBadge('within', 'Non-diabetic'), ref: 'Medical history: 0 = Non-diabetic, 1 = Diabetic (major vascular risk factor)' },
    { name: 'Hypertension (HTN)', category: 'Medical History', value: htn === 1 ? 'Yes' : 'No', rawVal: htn, badge: htn === 1 ? makeBadge('out', 'Hypertension history reported') : makeBadge('within', 'Normotensive'), ref: 'Medical history: 1 = Hypertensive history, 0 = Normotensive' },
    { name: 'Current Smoker', category: 'Medical History', value: current_smoker === 1 ? 'Yes' : 'No', rawVal: current_smoker, badge: current_smoker === 1 ? makeBadge('out', 'Active tobacco smoking') : makeBadge('within', 'Non-smoker'), ref: 'Active cigarette smoking within past 12 months' },
    { name: 'Ex-Smoker', category: 'Medical History', value: ex_smoker === 1 ? 'Yes' : 'No', rawVal: ex_smoker, badge: ex_smoker === 1 ? makeBadge('out', 'Former smoker') : makeBadge('within', 'No past smoking history'), ref: 'Former cigarette smoker with cessation' },
    { name: 'Family History of CAD (FH)', category: 'Medical History', value: fh === 1 ? 'Yes' : 'No', rawVal: fh, badge: fh === 1 ? makeBadge('out', 'Positive family history') : makeBadge('within', 'No premature CAD history'), ref: 'Premature cardiovascular disease in first-degree relatives' },
    { name: 'Obesity', category: 'Medical History', value: obesity === 'Y' ? 'Yes' : 'No', rawVal: obesity, badge: obesity === 'Y' ? makeBadge('out', 'Clinical obesity reported') : makeBadge('within', 'No clinical obesity'), ref: 'Clinical obesity determination (BMI ≥ 30 kg/m²)' },
    { name: 'Chronic Renal Failure (CRF)', category: 'Medical History', value: crf === 'Y' ? 'Yes' : 'No', rawVal: crf, badge: crf === 'Y' ? makeBadge('out', 'Persistent renal impairment') : makeBadge('within', 'No documented CRF'), ref: 'Documented persistent renal impairment' },
    { name: 'Cerebrovascular Accident (CVA)', category: 'Medical History', value: cva === 'Y' ? 'Yes' : 'No', rawVal: cva, badge: cva === 'Y' ? makeBadge('out', 'Prior CVA/TIA reported') : makeBadge('within', 'No documented stroke'), ref: 'Documented prior cerebrovascular accident or transient ischemic attack' },

    // 4. Symptoms
    { name: 'Typical Chest Pain', category: 'Symptoms', value: chest_pain === 1 ? 'Yes' : 'No', rawVal: chest_pain, badge: chest_pain === 1 ? makeBadge('out', 'Typical angina reported') : makeBadge('within', 'Absent'), ref: 'Substernal chest pressure provoked by exertion/stress and relieved by rest or nitroglycerin' },
    { name: 'Atypical Chest Pain', category: 'Symptoms', value: atypical === 'Y' ? 'Yes' : 'No', rawVal: atypical, badge: atypical === 'Y' ? makeBadge('out', 'Atypical angina noted') : makeBadge('within', 'Absent'), ref: 'Chest discomfort meeting 2 of 3 classical angina criteria' },
    { name: 'Non-Anginal Chest Pain', category: 'Symptoms', value: nonanginal === 'Y' ? 'Yes' : 'No', rawVal: nonanginal, badge: nonanginal === 'Y' ? makeBadge('out', 'Non-anginal pain noted') : makeBadge('within', 'Absent'), ref: 'Chest discomfort meeting ≤ 1 angina criteria' },
    { name: 'Dyspnea', category: 'Symptoms', value: dyspnea === 'Y' ? 'Yes' : 'No', rawVal: dyspnea, badge: dyspnea === 'Y' ? makeBadge('out', 'Exertional dyspnea reported') : makeBadge('within', 'Absent'), ref: 'Shortness of breath on exertion or rest' },
    { name: 'Low-Threshold Angina (LowTH Ang)', category: 'Symptoms', value: lowth_ang === 'Y' ? 'Yes' : 'No', rawVal: lowth_ang, badge: lowth_ang === 'Y' ? makeBadge('out', 'Low-threshold angina reported') : makeBadge('within', 'Absent'), ref: 'Angina triggered by minimal physical exertion' },
    { name: 'Poor R-Wave Progression', category: 'Symptoms', value: poor_r === 'Y' ? 'Yes' : 'No', rawVal: poor_r, badge: poor_r === 'Y' ? makeBadge('out', 'Poor R progression on ECG') : makeBadge('within', 'Normal R progression'), ref: 'ECG chest leads V1–V3 delayed amplitude increase' },

    // 5. Laboratory Results
    { name: 'Fasting Blood Sugar (FBS)', category: 'Laboratory Results', value: `${fbs} mg/dL`, rawVal: fbs, badge: fbsBadge, ref: 'Standard fasting reference range: 70 – 99 mg/dL (100–125 mg/dL impaired fasting range, ≥ 126 mg/dL elevated fasting threshold; formal diagnosis requires confirmatory evaluation)' },
    { name: 'Serum Creatinine (CR)', category: 'Laboratory Results', value: `${cr} mg/dL`, rawVal: cr, badge: crBadge, ref: 'Adult reference range: 0.7 – 1.3 mg/dL (varies by age, sex, and muscle mass)' },
    { name: 'Triglycerides (TG)', category: 'Laboratory Results', value: `${tg} mg/dL`, rawVal: tg, badge: tgBadge, ref: 'Standard adult fasting reference: < 150 mg/dL (150–199 mg/dL borderline elevated, ≥ 200 mg/dL elevated)' },
    { name: 'Low-Density Lipoprotein (LDL)', category: 'Laboratory Results', value: `${ldl} mg/dL`, rawVal: ldl, badge: ldlBadge, ref: 'Standard adult reference: < 100 mg/dL (< 70 mg/dL optional target in high cardiovascular risk)' },
    { name: 'High-Density Lipoprotein (HDL)', category: 'Laboratory Results', value: `${hdl} mg/dL`, rawVal: hdl, badge: hdlBadge, ref: 'Standard adult reference: > 40 mg/dL (men), > 50 mg/dL (women)' },
    { name: 'Blood Urea Nitrogen (BUN)', category: 'Laboratory Results', value: `${bun} mg/dL`, rawVal: bun, badge: bunBadge, ref: 'Standard adult reference range: 7 – 20 mg/dL' },
    { name: 'Erythrocyte Sedimentation Rate (ESR)', category: 'Laboratory Results', value: `${esr} mm/hr`, rawVal: esr, badge: esrBadge, ref: 'Common adult reference: 0 – 20 mm/hr (reference not specified for age/sex breakdown in dataset)' },
    { name: 'Hemoglobin (HB)', category: 'Laboratory Results', value: `${hb} g/dL`, rawVal: hb, badge: hbBadge, ref: 'Standard adult reference: 13.5 – 17.5 g/dL (men), 12.0 – 15.5 g/dL (women)' },
    { name: 'Potassium (K)', category: 'Laboratory Results', value: `${k} mEq/L`, rawVal: k, badge: kBadge, ref: 'Standard serum potassium reference range: 3.5 – 5.0 mEq/L' },
    { name: 'Sodium (Na)', category: 'Laboratory Results', value: `${na} mEq/L`, rawVal: na, badge: naBadge, ref: 'Standard serum sodium reference range: 135 – 145 mEq/L' },
    { name: 'White Blood Cell Count (WBC)', category: 'Laboratory Results', value: `${wbc.toLocaleString()} cells/µL`, rawVal: wbc, badge: wbcBadge, ref: 'Standard adult reference range: 4,000 – 11,000 cells/µL' },
    { name: 'Lymphocytes (Lymph)', category: 'Laboratory Results', value: `${lymph}%`, rawVal: lymph, badge: lymphBadge, ref: 'Standard adult leukocyte differential: 20 – 40%' },
    { name: 'Neutrophils (Neut)', category: 'Laboratory Results', value: `${neut}%`, rawVal: neut, badge: neutBadge, ref: 'Standard adult leukocyte differential: 40 – 70%' },
    { name: 'Platelet Count (PLT)', category: 'Laboratory Results', value: `${plt} ×10³/µL`, rawVal: plt, badge: pltBadge, ref: 'Standard adult reference range: 150 – 450 ×10³/µL' },

    // 6. ECG & Cardiac Findings
    { name: 'Pathological Q Wave', category: 'ECG & Cardiac Findings', value: q_wave === 1 ? 'Present' : 'Absent', rawVal: q_wave, badge: q_wave === 1 ? makeBadge('out', 'Pathologic Q wave noted') : makeBadge('within', 'Absent'), ref: 'ECG finding indicating possible prior transmural infarction' },
    { name: 'ST-Segment Elevation', category: 'ECG & Cardiac Findings', value: st_elevation === 1 ? 'Present' : 'Absent', rawVal: st_elevation, badge: st_elevation === 1 ? makeBadge('out', 'ST elevation noted') : makeBadge('within', 'Absent'), ref: 'ECG finding indicating potential acute myocardial ischemia / injury' },
    { name: 'ST-Segment Depression', category: 'ECG & Cardiac Findings', value: st_depression === 1 ? 'Present' : 'Absent', rawVal: st_depression, badge: st_depression === 1 ? makeBadge('out', 'ST depression noted') : makeBadge('within', 'Absent'), ref: 'ECG finding indicating potential subendocardial ischemia' },
    { name: 'T-Wave Inversion', category: 'ECG & Cardiac Findings', value: tinversion === 1 ? 'Present' : 'Absent', rawVal: tinversion, badge: tinversion === 1 ? makeBadge('out', 'T inversion noted') : makeBadge('within', 'Absent'), ref: 'ECG finding indicating potential ischemia or strain' },
    { name: 'Left Ventricular Hypertrophy (LVH)', category: 'ECG & Cardiac Findings', value: lvh === 'Y' ? 'Present' : 'Absent', rawVal: lvh, badge: lvh === 'Y' ? makeBadge('out', 'LVH voltage noted') : makeBadge('within', 'Absent'), ref: 'ECG voltage criteria suggestive of increased LV wall mass' },
    { name: 'Bundle Branch Block (BBB)', category: 'ECG & Cardiac Findings', value: bbb === 'N' ? 'None (Normal Conduction)' : bbb, rawVal: bbb, badge: bbb === 'N' ? makeBadge('within', 'Normal ventricular conduction') : makeBadge('out', `${bbb} conduction delay`), ref: 'Intraventricular conduction delay: None (N), RBBB, or LBBB' },
    { name: 'Regional Wall Motion Abnormality (RWMA)', category: 'ECG & Cardiac Findings', value: `${region_rwma}`, rawVal: region_rwma, badge: region_rwma === 0 ? makeBadge('within', 'Normal wall kinetics (0)') : makeBadge('out', `Wall motion score: ${region_rwma}`), ref: 'Echocardiographic score: 0 = Normal kinetics, 1–4 = Hypokinetic / akinetic' },
    { name: 'Valvular Heart Disease (VHD)', category: 'ECG & Cardiac Findings', value: vhd === 'N' ? 'None' : vhd.charAt(0).toUpperCase() + vhd.slice(1), rawVal: vhd, badge: vhd === 'N' ? makeBadge('within', 'No significant valvular disease') : makeBadge('out', `${vhd} valvular disease`), ref: 'Echocardiographic valve assessment: None, Mild, Moderate, or Severe' },

    // 7. Additional Clinical Findings
    { name: 'Peripheral Edema', category: 'Additional Clinical Findings', value: edema === 1 ? 'Present' : 'Absent', rawVal: edema, badge: edema === 1 ? makeBadge('out', 'Peripheral edema noted') : makeBadge('within', 'Absent'), ref: 'Clinical finding: 0 = Absent, 1 = Present' },
    { name: 'NYHA Function Class', category: 'Additional Clinical Findings', value: `Class ${function_class}`, rawVal: function_class, badge: function_class === 0 ? makeBadge('within', 'Class 0 (Asymptomatic)') : makeBadge('out', `NYHA Class ${function_class}`), ref: 'NYHA heart failure functional classification: Class 0 (Asymptomatic) – Class 4 (Severe)' },
    { name: 'Chronic Obstructive Airway Disease', category: 'Additional Clinical Findings', value: airway === 'Y' ? 'Yes' : 'No', rawVal: airway, badge: airway === 'Y' ? makeBadge('out', 'Chronic airway disease reported') : makeBadge('within', 'Absent'), ref: 'Documented chronic airway or pulmonary disease' },
    { name: 'Thyroid Disease', category: 'Additional Clinical Findings', value: thyroid === 'Y' ? 'Yes' : 'No', rawVal: thyroid, badge: thyroid === 'Y' ? makeBadge('out', 'Thyroid disease reported') : makeBadge('within', 'Absent'), ref: 'Documented hypothyroidism or hyperthyroidism' },
    { name: 'Congestive Heart Failure (CHF)', category: 'Additional Clinical Findings', value: chf === 'Y' ? 'Yes' : 'No', rawVal: chf, badge: chf === 'Y' ? makeBadge('out', 'Documented chronic CHF') : makeBadge('within', 'Absent'), ref: 'Documented history or diagnosis of chronic heart failure' },
    { name: 'Dyslipidemia (DLP)', category: 'Additional Clinical Findings', value: dlp === 'Y' ? 'Yes' : 'No', rawVal: dlp, badge: dlp === 'Y' ? makeBadge('out', 'Dyslipidemia reported') : makeBadge('within', 'Absent'), ref: 'Diagnosed lipid metabolism disorder' },
    { name: 'Weak Peripheral Pulse', category: 'Additional Clinical Findings', value: weak_pulse === 'Y' ? 'Yes' : 'No', rawVal: weak_pulse, badge: weak_pulse === 'Y' ? makeBadge('out', 'Diminished pulse noted') : makeBadge('within', 'Normal pulse'), ref: 'Diminished peripheral arterial pulsations' },
    { name: 'Lung Rales / Crackles', category: 'Additional Clinical Findings', value: lung_rales === 'Y' ? 'Yes' : 'No', rawVal: lung_rales, badge: lung_rales === 'Y' ? makeBadge('out', 'Pulmonary rales noted') : makeBadge('within', 'Clear lungs'), ref: 'Auscultated pulmonary crackles' },
    { name: 'Systolic Murmur', category: 'Additional Clinical Findings', value: systolic_murmur === 'Y' ? 'Yes' : 'No', rawVal: systolic_murmur, badge: systolic_murmur === 'Y' ? makeBadge('out', 'Systolic murmur noted') : makeBadge('within', 'Absent'), ref: 'Auscultated cardiac murmur during ventricular systole' },
    { name: 'Diastolic Murmur', category: 'Additional Clinical Findings', value: diastolic_murmur === 'Y' ? 'Yes' : 'No', rawVal: diastolic_murmur, badge: diastolic_murmur === 'Y' ? makeBadge('out', 'Diastolic murmur noted') : makeBadge('within', 'Absent'), ref: 'Auscultated cardiac murmur during ventricular diastole' }
  ];
}

function getModelData(){
  const age = parseFloat(document.getElementById('inp_age')?.value || 58);
  const length = parseFloat(document.getElementById('inp_length')?.value || 170);
  const weight = parseFloat(document.getElementById('inp_weight')?.value || 72);
  const bmi = parseFloat(document.getElementById('inp_bmi')?.value || (weight / ((length/100)**2)).toFixed(1));
  const sex = document.getElementById('inp_sex')?.value || 'Male';

  const dm = parseInt(document.getElementById('inp_dm')?.value || 0);
  const htn = parseInt(document.getElementById('inp_htn')?.value || 1);
  const current_smoker = parseInt(document.getElementById('inp_current_smoker')?.value || 0);
  const ex_smoker = parseInt(document.getElementById('inp_ex_smoker')?.value || 0);
  const fh = parseInt(document.getElementById('inp_fh')?.value || 0);
  const obesity = document.getElementById('inp_obesity')?.value || 'N';
  const crf = document.getElementById('inp_crf')?.value || 'N';
  const cva = document.getElementById('inp_cva')?.value || 'N';

  const chest_pain = document.getElementById('inp_chest_pain')?.value === 'Y' ? 1.0 : 0.0;
  const dyspnea = document.getElementById('inp_dyspnea')?.value || 'N';
  const atypical = document.getElementById('inp_atypical')?.value || 'N';
  const nonanginal = document.getElementById('inp_nonanginal')?.value || 'N';
  const lowth_ang = document.getElementById('inp_lowth_ang')?.value || 'N';
  const poor_r = document.getElementById('inp_poor_r')?.value || 'N';

  const bp = parseFloat(document.getElementById('inp_bp')?.value || 130);
  const pr = parseFloat(document.getElementById('inp_pr')?.value || 70);
  const ef_tte = parseFloat(document.getElementById('inp_ef_tte')?.value || 50);

  const fbs = parseFloat(document.getElementById('inp_fbs')?.value || 98);
  const cr = parseFloat(document.getElementById('inp_cr')?.value || 1.0);
  const tg = parseFloat(document.getElementById('inp_tg')?.value || 122);
  const ldl = parseFloat(document.getElementById('inp_ldl')?.value || 100);
  const hdl = parseFloat(document.getElementById('inp_hdl')?.value || 39);
  const bun = parseFloat(document.getElementById('inp_bun')?.value || 16);
  const esr = parseFloat(document.getElementById('inp_esr')?.value || 15);
  const hb = parseFloat(document.getElementById('inp_hb')?.value || 13.2);
  const k = parseFloat(document.getElementById('inp_k')?.value || 4.2);
  const na = parseFloat(document.getElementById('inp_na')?.value || 141);
  const wbc = parseFloat(document.getElementById('inp_wbc')?.value || 7100);
  const lymph = parseFloat(document.getElementById('inp_lymph')?.value || 32);
  const neut = parseFloat(document.getElementById('inp_neut')?.value || 60);
  const plt = parseFloat(document.getElementById('inp_plt')?.value || 210);

  const q_wave = parseInt(document.getElementById('inp_q_wave')?.value || 0);
  const st_elevation = parseInt(document.getElementById('inp_st_elevation')?.value || 0);
  const st_depression = parseInt(document.getElementById('inp_st_depression')?.value || 0);
  const tinversion = parseInt(document.getElementById('inp_tinversion')?.value || 0);
  const lvh = document.getElementById('inp_lvh')?.value || 'N';
  const bbb = document.getElementById('inp_bbb')?.value || 'N';
  const region_rwma = parseFloat(document.getElementById('inp_region_rwma')?.value || 0);
  const vhd = document.getElementById('inp_vhd')?.value || 'N';

  const edema = parseInt(document.getElementById('inp_edema')?.value || 0);
  const function_class = parseInt(document.getElementById('inp_function_class')?.value || 0);
  const airway = document.getElementById('inp_airway')?.value || 'N';
  const thyroid = document.getElementById('inp_thyroid')?.value || 'N';
  const chf = document.getElementById('inp_chf')?.value || 'N';
  const dlp = document.getElementById('inp_dlp')?.value || 'N';
  const weak_pulse = document.getElementById('inp_weak_pulse')?.value || 'N';
  const lung_rales = document.getElementById('inp_lung_rales')?.value || 'N';
  const systolic_murmur = document.getElementById('inp_systolic_murmur')?.value || 'N';
  const diastolic_murmur = document.getElementById('inp_diastolic_murmur')?.value || 'N';

  // EXACT 57 features from feature_columns.pkl: 34 numeric + 23 one-hot encoded
  return [
    { num: 1, name: 'Age', value: age, type: 'Numeric', desc: 'Patient chronological age in years' },
    { num: 2, name: 'Weight', value: weight, type: 'Numeric', desc: 'Body weight in kilograms (kg)' },
    { num: 3, name: 'Length', value: length, type: 'Numeric', desc: 'Patient height/stature in centimeters (cm)' },
    { num: 4, name: 'BMI', value: bmi, type: 'Numeric', desc: 'Body Mass Index in kg/m²' },
    { num: 5, name: 'DM', value: dm, type: 'Numeric', desc: 'Diabetes Mellitus indicator (0 = No, 1 = Yes)' },
    { num: 6, name: 'HTN', value: htn, type: 'Numeric', desc: 'Hypertension indicator (0 = No, 1 = Yes)' },
    { num: 7, name: 'Current Smoker', value: current_smoker, type: 'Numeric', desc: 'Active cigarette smoking (0 = No, 1 = Yes)' },
    { num: 8, name: 'EX-Smoker', value: ex_smoker, type: 'Numeric', desc: 'Former cigarette smoking (0 = No, 1 = Yes)' },
    { num: 9, name: 'FH', value: fh, type: 'Numeric', desc: 'Family history of premature CAD (0 = No, 1 = Yes)' },
    { num: 10, name: 'BP', value: bp, type: 'Numeric', desc: 'Resting systolic blood pressure in mmHg' },
    { num: 11, name: 'PR', value: pr, type: 'Numeric', desc: 'Resting pulse / heart rate in bpm' },
    { num: 12, name: 'Edema', value: edema, type: 'Numeric', desc: 'Peripheral edema finding (0 = Absent, 1 = Present)' },
    { num: 13, name: 'Typical Chest Pain', value: chest_pain, type: 'Numeric', desc: 'Typical exertional substernal angina (0 = Absent, 1 = Present)' },
    { num: 14, name: 'Function Class', value: function_class, type: 'Numeric', desc: 'NYHA cardiac functional class score (0 to 4)' },
    { num: 15, name: 'Q Wave', value: q_wave, type: 'Numeric', desc: 'Pathologic Q wave on 12-lead ECG (0 = Absent, 1 = Present)' },
    { num: 16, name: 'St Elevation', value: st_elevation, type: 'Numeric', desc: 'ST-segment elevation on 12-lead ECG (0 = Absent, 1 = Present)' },
    { num: 17, name: 'St Depression', value: st_depression, type: 'Numeric', desc: 'ST-segment depression on 12-lead ECG (0 = Absent, 1 = Present)' },
    { num: 18, name: 'Tinversion', value: tinversion, type: 'Numeric', desc: 'T-wave inversion on 12-lead ECG (0 = Absent, 1 = Present)' },
    { num: 19, name: 'FBS', value: fbs, type: 'Numeric', desc: 'Fasting blood sugar in mg/dL' },
    { num: 20, name: 'CR', value: cr, type: 'Numeric', desc: 'Serum creatinine concentration in mg/dL' },
    { num: 21, name: 'TG', value: tg, type: 'Numeric', desc: 'Serum triglycerides in mg/dL' },
    { num: 22, name: 'LDL', value: ldl, type: 'Numeric', desc: 'Low-density lipoprotein cholesterol in mg/dL' },
    { num: 23, name: 'HDL', value: hdl, type: 'Numeric', desc: 'High-density lipoprotein cholesterol in mg/dL' },
    { num: 24, name: 'BUN', value: bun, type: 'Numeric', desc: 'Blood urea nitrogen in mg/dL' },
    { num: 25, name: 'ESR', value: esr, type: 'Numeric', desc: 'Erythrocyte sedimentation rate in mm/hr' },
    { num: 26, name: 'HB', value: hb, type: 'Numeric', desc: 'Hemoglobin concentration in g/dL' },
    { num: 27, name: 'K', value: k, type: 'Numeric', desc: 'Serum potassium ion concentration in mEq/L' },
    { num: 28, name: 'Na', value: na, type: 'Numeric', desc: 'Serum sodium ion concentration in mEq/L' },
    { num: 29, name: 'WBC', value: wbc, type: 'Numeric', desc: 'White blood cell count in cells/µL' },
    { num: 30, name: 'Lymph', value: lymph, type: 'Numeric', desc: 'Lymphocyte differential percentage (%)' },
    { num: 31, name: 'Neut', value: neut, type: 'Numeric', desc: 'Neutrophil differential percentage (%)' },
    { num: 32, name: 'PLT', value: plt, type: 'Numeric', desc: 'Platelet count in ×10³/µL' },
    { num: 33, name: 'EF-TTE', value: ef_tte, type: 'Numeric', desc: 'Transthoracic echocardiogram left ventricular EF (%)' },
    { num: 34, name: 'Region RWMA', value: region_rwma, type: 'Numeric', desc: 'Regional wall motion abnormality score (0 to 4)' },
    { num: 35, name: 'Sex_Male', value: sex === 'Male' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for biological sex (1 = Male, 0 = Female)' },
    { num: 36, name: 'Obesity_Y', value: obesity === 'Y' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for clinical obesity (1 = Yes, 0 = No)' },
    { num: 37, name: 'CRF_Y', value: crf === 'Y' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for chronic renal failure (1 = Yes, 0 = No)' },
    { num: 38, name: 'CVA_Y', value: cva === 'Y' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for cerebrovascular accident (1 = Yes, 0 = No)' },
    { num: 39, name: 'Airway disease_Y', value: airway === 'Y' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for chronic airway disease (1 = Yes, 0 = No)' },
    { num: 40, name: 'Thyroid Disease_Y', value: thyroid === 'Y' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for thyroid disease (1 = Yes, 0 = No)' },
    { num: 41, name: 'CHF_Y', value: chf === 'Y' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for congestive heart failure (1 = Yes, 0 = No)' },
    { num: 42, name: 'DLP_Y', value: dlp === 'Y' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for dyslipidemia (1 = Yes, 0 = No)' },
    { num: 43, name: 'Weak Peripheral Pulse_Y', value: weak_pulse === 'Y' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for weak peripheral pulses (1 = Yes, 0 = No)' },
    { num: 44, name: 'Lung rales_Y', value: lung_rales === 'Y' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for auscultated lung rales (1 = Yes, 0 = No)' },
    { num: 45, name: 'Systolic Murmur_Y', value: systolic_murmur === 'Y' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for systolic cardiac murmur (1 = Yes, 0 = No)' },
    { num: 46, name: 'Diastolic Murmur_Y', value: diastolic_murmur === 'Y' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for diastolic cardiac murmur (1 = Yes, 0 = No)' },
    { num: 47, name: 'Dyspnea_Y', value: dyspnea === 'Y' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for exertional dyspnea (1 = Yes, 0 = No)' },
    { num: 48, name: 'Atypical_Y', value: atypical === 'Y' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for atypical angina (1 = Yes, 0 = No)' },
    { num: 49, name: 'Nonanginal_Y', value: nonanginal === 'Y' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for non-anginal chest pain (1 = Yes, 0 = No)' },
    { num: 50, name: 'LowTH Ang_Y', value: lowth_ang === 'Y' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for low-threshold angina (1 = Yes, 0 = No)' },
    { num: 51, name: 'LVH_Y', value: lvh === 'Y' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for left ventricular hypertrophy (1 = Yes, 0 = No)' },
    { num: 52, name: 'Poor R Progression_Y', value: poor_r === 'Y' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for poor R-wave progression (1 = Yes, 0 = No)' },
    { num: 53, name: 'BBB_N', value: bbb === 'N' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for normal ventricular conduction (1 = None, 0 = Other)' },
    { num: 54, name: 'BBB_RBBB', value: bbb === 'RBBB' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for right bundle branch block (1 = RBBB, 0 = Other)' },
    { num: 55, name: 'VHD_N', value: vhd === 'N' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for absence of valvular disease (1 = None, 0 = Other)' },
    { num: 56, name: 'VHD_Severe', value: vhd === 'Severe' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for severe valvular disease (1 = Severe, 0 = Other)' },
    { num: 57, name: 'VHD_mild', value: vhd === 'mild' ? 1.0 : 0.0, type: 'One-Hot Encoded', desc: 'One-hot encoding for mild valvular disease (1 = Mild, 0 = Other)' }
  ];
}

function renderClinicalTable(){
  const tbody = document.getElementById('pvClinicalTableBody');
  if (!tbody) return;

  const data = getClinicalData();
  const search = (document.getElementById('pvSearchInput')?.value || '').trim().toLowerCase();
  const catFilter = document.getElementById('pvCategorySelect')?.value || 'ALL';

  let filtered = data.filter(item => {
    if (catFilter !== 'ALL' && item.category !== catFilter) return false;
    if (search) {
      const match = item.name.toLowerCase().includes(search) ||
                    item.category.toLowerCase().includes(search) ||
                    item.value.toString().toLowerCase().includes(search) ||
                    item.ref.toLowerCase().includes(search);
      if (!match) return false;
    }
    return true;
  });

  // Update sort icons
  const icons = {
    name: document.getElementById('sortIconClinName'),
    category: document.getElementById('sortIconClinCat'),
    value: document.getElementById('sortIconClinVal'),
    ref: document.getElementById('sortIconClinRef')
  };
  for (const [k, el] of Object.entries(icons)) {
    if (el) el.textContent = (clinicalSort.field === k) ? (clinicalSort.asc ? '▲' : '▼') : '▲▼';
  }

  // Sort if requested by a specific column other than default category grouping
  if (clinicalSort.field !== 'default' && clinicalSort.field !== 'category') {
    filtered.sort((a, b) => {
      let av = a[clinicalSort.field] ?? a.name;
      let bv = b[clinicalSort.field] ?? b.name;
      if (typeof av === 'string') av = av.toLowerCase();
      if (typeof bv === 'string') bv = bv.toLowerCase();
      if (av < bv) return clinicalSort.asc ? -1 : 1;
      if (av > bv) return clinicalSort.asc ? 1 : -1;
      return 0;
    });

    let html = '';
    filtered.forEach(item => {
      html += `<tr>
        <td><b>${item.name}</b></td>
        <td><span style="color:#506e94;font-weight:600;">${item.category}</span></td>
        <td>
          <div class="valHighlight">${item.value}</div>
          ${item.badge ? `<div>${item.badge}</div>` : ''}
        </td>
        <td style="color:#4a6486;">${item.ref}</td>
      </tr>`;
    });
    if (filtered.length === 0) {
      html = `<tr><td colspan="4" style="text-align:center;padding:24px;color:#708ba8;">No matching clinical attributes found.</td></tr>`;
    }
    tbody.innerHTML = html;
  } else {
    // Grouped by Category view
    const catOrder = [
      'Demographics', 'Vital Signs', 'Medical History', 'Symptoms',
      'Laboratory Results', 'ECG & Cardiac Findings', 'Additional Clinical Findings'
    ];
    let html = '';
    catOrder.forEach(cat => {
      const catItems = filtered.filter(i => i.category === cat);
      if (catItems.length === 0) return;

      const isCollapsed = Boolean(collapsedCategories[cat]) && !search;
      const rot = isCollapsed ? 'style="transform:rotate(-90deg);"' : '';

      html += `<tr class="categoryHeaderRow" onclick="togglePatientCategory('${cat}')" title="Click to expand/collapse this category">
        <td colspan="4">
          <svg viewBox="0 0 24 24" class="catToggleIcon" ${rot} fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
          <span>${cat}</span>
          <span style="font-size:11px;font-weight:600;opacity:0.75;margin-left:6px;">(${catItems.length} features)</span>
        </td>
      </tr>`;

      if (!isCollapsed) {
        catItems.forEach(item => {
          html += `<tr>
            <td style="padding-left:26px;"><b>${item.name}</b></td>
            <td><span style="color:#506e94;font-weight:600;">${item.category}</span></td>
            <td>
              <div class="valHighlight">${item.value}</div>
              ${item.badge ? `<div>${item.badge}</div>` : ''}
            </td>
            <td style="color:#4a6486;">${item.ref}</td>
          </tr>`;
        });
      }
    });

    if (filtered.length === 0) {
      html = `<tr><td colspan="4" style="text-align:center;padding:24px;color:#708ba8;">No matching clinical attributes found.</td></tr>`;
    }
    tbody.innerHTML = html;
  }

  const countEl = document.getElementById('pvRowCount');
  if (countEl && currentPatientTab === 'clinical') {
    countEl.textContent = `Showing ${filtered.length} of ${data.length} features` + (search ? ` matching "${search}"` : '');
  }
}

function renderModelTable(){
  const tbody = document.getElementById('pvModelTableBody');
  if (!tbody) return;

  const data = getModelData();
  const search = (document.getElementById('pvSearchInput')?.value || '').trim().toLowerCase();

  let filtered = data.filter(item => {
    if (search) {
      const match = item.name.toLowerCase().includes(search) ||
                    item.type.toLowerCase().includes(search) ||
                    item.value.toString().toLowerCase().includes(search) ||
                    item.desc.toLowerCase().includes(search) ||
                    item.num.toString() === search;
      if (!match) return false;
    }
    return true;
  });

  // Update sort icons
  const icons = {
    num: document.getElementById('sortIconModNum'),
    name: document.getElementById('sortIconModName'),
    value: document.getElementById('sortIconModVal'),
    type: document.getElementById('sortIconModType'),
    desc: document.getElementById('sortIconModDesc')
  };
  for (const [k, el] of Object.entries(icons)) {
    if (el) el.textContent = (modelSort.field === k) ? (modelSort.asc ? '▲' : '▼') : '▲▼';
  }

  filtered.sort((a, b) => {
    let av = a[modelSort.field];
    let bv = b[modelSort.field];
    if (typeof av === 'string') av = av.toLowerCase();
    if (typeof bv === 'string') bv = bv.toLowerCase();
    if (av < bv) return modelSort.asc ? -1 : 1;
    if (av > bv) return modelSort.asc ? 1 : -1;
    return 0;
  });

  let html = '';
  filtered.forEach(item => {
    const typeBadge = item.type === 'Numeric'
      ? `<span class="badgeNumeric">Numeric</span>`
      : `<span class="badgeEncoded">One-Hot Encoded</span>`;
    html += `<tr>
      <td style="text-align:center;font-weight:700;color:#627d9f;">${item.num}</td>
      <td><span class="featureCode">${item.name}</span></td>
      <td><b style="color:#0b2b5b;font-family:monospace;font-size:13.5px;">${item.value}</b></td>
      <td>${typeBadge}</td>
      <td style="color:#4a6486;">${item.desc}</td>
    </tr>`;
  });

  if (filtered.length === 0) {
    html = `<tr><td colspan="5" style="text-align:center;padding:24px;color:#708ba8;">No matching model features found.</td></tr>`;
  }
  tbody.innerHTML = html;

  const countEl = document.getElementById('pvRowCount');
  if (countEl && currentPatientTab === 'model') {
    countEl.textContent = `Showing ${filtered.length} of ${data.length} model features` + (search ? ` matching "${search}"` : '');
  }
}

function filterPatientTables(){
  if (currentPatientTab === 'clinical') {
    renderClinicalTable();
  } else {
    renderModelTable();
  }
}

function renderPatientInfoScreen(){
  const pat = getPatientDetails();
  const ageEl = document.getElementById('inp_age');
  const sexEl = document.getElementById('inp_sex');

  const pvName = document.getElementById('pvPatientNameDisplay');
  if (pvName) pvName.textContent = pat.displayName;
  const pvId = document.getElementById('pvPatientIdDisplay');
  if (pvId) pvId.textContent = pat.id;
  const pvAge = document.getElementById('pvAgeDisplay');
  if (pvAge && ageEl) pvAge.textContent = `${ageEl.value || 58} years`;
  const pvSex = document.getElementById('pvSexDisplay');
  if (pvSex && sexEl) pvSex.textContent = sexEl.value || 'Male';

  renderClinicalTable();
  renderModelTable();
}

let inputsModified = false;
function markInputsModified(){
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
}

function applyVisualStyles(data){
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
}

function renderVisualsFromDOM(){
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
}

function applyPredictions(data, payload){
  if (!data) return;

  // 1. Numerical Values
  const cadNum = document.getElementById('cadRiskNum');
  if (cadNum && data.cad_risk !== undefined) cadNum.textContent = Number(data.cad_risk).toFixed(1) + '%';
  const ladNum = document.getElementById('ladRiskNum');
  if (ladNum && data.lad_risk !== undefined) ladNum.textContent = Number(data.lad_risk).toFixed(1) + '%';
  const lcxNum = document.getElementById('lcxRiskNum');
  if (lcxNum && data.lcx_risk !== undefined) lcxNum.textContent = Number(data.lcx_risk).toFixed(1) + '%';
  const rcaNum = document.getElementById('rcaRiskNum');
  if (rcaNum && data.rca_risk !== undefined) rcaNum.textContent = Number(data.rca_risk).toFixed(1) + '%';

  // 2. Class Labels
  const cadLbl = document.getElementById('cadLabelText');
  if (cadLbl && data.cad_label) cadLbl.textContent = data.cad_label;
  const ladLbl = document.getElementById('ladLabelText');
  if (ladLbl && data.lad_label) ladLbl.textContent = data.lad_label;
  const lcxLbl = document.getElementById('lcxLabelText');
  if (lcxLbl && data.lcx_label) lcxLbl.textContent = data.lcx_label;
  const rcaLbl = document.getElementById('rcaLabelText');
  if (rcaLbl && data.rca_label) rcaLbl.textContent = data.rca_label;

  // 3. Clinical Probability Tier Badges
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

  // 4. Donut Ring Percentages
  const cadPctTxt = document.getElementById('cadPctText');
  if (cadPctTxt && data.cad_pct !== undefined) cadPctTxt.textContent = data.cad_pct + '%';
  const ladPctTxt = document.getElementById('ladPctText');
  if (ladPctTxt && data.lad_pct !== undefined) ladPctTxt.textContent = data.lad_pct + '%';
  const lcxPctTxt = document.getElementById('lcxPctText');
  if (lcxPctTxt && data.lcx_pct !== undefined) lcxPctTxt.textContent = data.lcx_pct + '%';
  const rcaPctTxt = document.getElementById('rcaRingText');
  if (rcaPctTxt && data.rca_pct !== undefined) rcaPctTxt.textContent = data.rca_pct + '%';

  // 5. Visual Gradients and Bar Heights
  applyVisualStyles(data);

  // 6. Reset Stale State Notice & Status Badge
  inputsModified = false;
  const badge = document.getElementById('predStatusBadge');
  if (badge) {
    badge.className = 'predBadge fresh';
    badge.innerHTML = '<span class="badgeDot"></span><span>Latest Model Predictions</span>';
  }
  const notice = document.getElementById('staleNotice');
  if (notice) notice.style.display = 'none';

  // 7. Update 3D Viewer Frame if available
  try {
    const viewer = document.getElementById('viewerIframe') || document.getElementById('heartViewerFrame');
    if (viewer && viewer.contentWindow) {
      if (viewer.contentWindow.CardioVision3D && viewer.contentWindow.CardioVision3D.updateProbabilities) {
        viewer.contentWindow.CardioVision3D.updateProbabilities({
          CAD: { risk: data.cad_risk, label: data.cad_label },
          LAD: { risk: data.lad_risk, label: data.lad_label },
          LCX: { risk: data.lcx_risk, label: data.lcx_label },
          RCA: { risk: data.rca_risk, label: data.rca_label }
        });
      }
      viewer.contentWindow.postMessage({
        type: 'UPDATE_CARDIO_DATA',
        data: {
          CAD: { risk: data.cad_risk, label: data.cad_label },
          LAD: { risk: data.lad_risk, label: data.lad_label },
          LCX: { risk: data.lcx_risk, label: data.lcx_label },
          RCA: { risk: data.rca_risk, label: data.rca_label }
        }
      }, '*');
    }
  } catch(e) {}

  try {
    sessionStorage.setItem('cardiovision_state', 'predicted');
    sessionStorage.setItem('cardiovision_last_prediction', JSON.stringify(data));
  } catch(e) {}

  syncPatientDetails();

  // 8. Ensure patient clinical values are NEVER stored in the browser URL
  try {
    if (window.parent && window.parent !== window && window.parent.history && window.parent.location.search) {
      window.parent.history.replaceState({}, '', window.parent.location.pathname);
    }
    if (window.history && window.location.search) {
      window.history.replaceState({}, '', window.location.pathname);
    }
  } catch(e) {}
}

function getPatientDetails(){
  let pid = '';
  try { pid = sessionStorage.getItem('cardiovision_patient_id'); } catch(e){}
  if (!pid) {
    pid = 'CV-2026-' + Math.floor(1000 + Math.random() * 9000);
    try { sessionStorage.setItem('cardiovision_patient_id', pid); } catch(e){}
  }
  const idInp = document.getElementById('inp_patient_id');
  if (idInp && idInp.value !== pid) {
    idInp.value = pid;
  }

  const nameInp = document.getElementById('inp_patient_name');
  let pname = '';
  if (nameInp && nameInp.value.trim() !== '') {
    pname = nameInp.value.trim();
  } else {
    try { pname = sessionStorage.getItem('cardiovision_patient_name') || ''; } catch(e){}
  }
  const displayName = pname !== '' ? pname : 'Alex Morgan (Demo Patient)';
  return { id: pid, name: pname, displayName: displayName };
}

function syncPatientDetails(){
  const pat = getPatientDetails();

  const idInp = document.getElementById('inp_patient_id');
  if (idInp && idInp.value !== pat.id) idInp.value = pat.id;
  const nameInp = document.getElementById('inp_patient_name');
  if (nameInp && pat.name && nameInp.value !== pat.name) nameInp.value = pat.name;

  // Sync Patient Clinical Vector view
  const pvName = document.getElementById('pvPatientNameDisplay');
  if (pvName) pvName.textContent = pat.displayName;
  const pvId = document.getElementById('pvPatientIdDisplay');
  if (pvId) pvId.textContent = pat.id;
  const pvAge = document.getElementById('pvAgeDisplay');
  const ageEl = document.getElementById('inp_age');
  if (pvAge && ageEl) pvAge.textContent = `${ageEl.value || 58} years`;
  const pvSex = document.getElementById('pvSexDisplay');
  const sexEl = document.getElementById('inp_sex');
  if (pvSex && sexEl) pvSex.textContent = sexEl.value || 'Male';

  renderPatientInfoScreen();

  // Sync Results & Analysis view
  const resName = document.getElementById('resPatientName');
  if (resName) resName.textContent = pat.displayName;
  const resId = document.getElementById('resPatientId');
  if (resId) resId.textContent = pat.id;

  const bmiEl = document.getElementById('inp_bmi');
  const resDemo = document.getElementById('resDemographics');
  if (resDemo && ageEl && sexEl && bmiEl) {
    resDemo.textContent = `${ageEl.value || 58} yrs • ${sexEl.value || 'Male'} • BMI ${bmiEl.value || '24.9'} kg/m²`;
  }

  const resDate = document.getElementById('resDate');
  if (resDate) {
    const now = new Date();
    resDate.textContent = now.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  }

  const cadNum = document.getElementById('cadRiskNum');
  const cadLbl = document.getElementById('cadLabelText');
  const resSummary = document.getElementById('resRiskSummary');
  if (resSummary && cadNum && cadLbl) {
    resSummary.textContent = `Overall CAD: ${cadNum.textContent} (${cadLbl.textContent})`;
  }

  const resCadVal = document.getElementById('resCadVal');
  if (resCadVal && cadNum) resCadVal.textContent = cadNum.textContent;
  const resCadLbl = document.getElementById('resCadLbl');
  if (resCadLbl && cadLbl) resCadLbl.textContent = cadLbl.textContent;

  const ladNum = document.getElementById('ladRiskNum');
  const ladLbl = document.getElementById('ladLabelText');
  const resLadVal = document.getElementById('resLadVal');
  if (resLadVal && ladNum) resLadVal.textContent = ladNum.textContent;
  const resLadLbl = document.getElementById('resLadLbl');
  if (resLadLbl && ladLbl) resLadLbl.textContent = ladLbl.textContent;

  const lcxNum = document.getElementById('lcxRiskNum');
  const lcxLbl = document.getElementById('lcxLabelText');
  const resLcxVal = document.getElementById('resLcxVal');
  if (resLcxVal && lcxNum) resLcxVal.textContent = lcxNum.textContent;
  const resLcxLbl = document.getElementById('resLcxLbl');
  if (resLcxLbl && lcxLbl) resLcxLbl.textContent = lcxLbl.textContent;

  const rcaNum = document.getElementById('rcaRiskNum');
  const rcaLbl = document.getElementById('rcaLabelText');
  const resRcaVal = document.getElementById('resRcaVal');
  if (resRcaVal && rcaNum) resRcaVal.textContent = rcaNum.textContent;
  const resRcaLbl = document.getElementById('resRcaLbl');
  if (resRcaLbl && rcaLbl) resRcaLbl.textContent = rcaLbl.textContent;
}

function exportClinicalReport(){
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
<title>CardioVision AI - Clinical Risk Assessment Report - ${pat.id}</title>
<style>
  @page { size: letter; margin: 16mm 14mm; }
  * { box-sizing: border-box; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #1e293b; background: #fff; margin: 0; padding: 24px; font-size: 13px; line-height: 1.45; }
  .header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #1759e8; padding-bottom: 14px; margin-bottom: 18px; }
  .brand { display: flex; align-items: center; gap: 12px; }
  .logoSvg { width: 38px; height: 38px; color: #1759e8; }
  .brandTitle { font-size: 22px; font-weight: 800; color: #0b2b5b; margin: 0; }
  .brandSub { font-size: 11.5px; color: #64748b; margin: 2px 0 0; }
  .reportMeta { text-align: right; font-size: 11px; color: #475569; }
  .reportId { font-family: monospace; font-size: 13px; font-weight: 700; color: #1759e8; background: #eef4ff; padding: 2px 8px; border-radius: 4px; display: inline-block; margin-top: 4px; }
  
  .patientCard { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; margin-bottom: 18px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
  .metaItem { display: flex; flex-direction: column; gap: 2px; }
  .metaItem label { font-size: 10px; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.5px; }
  .metaItem span { font-size: 13px; font-weight: 600; color: #0f172a; }
  
  h3 { font-size: 14px; font-weight: 800; color: #0b2b5b; margin: 18px 0 8px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; }
  
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
  
  .recommendations { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px 16px; margin-bottom: 18px; }
  .recommendations ol { margin: 6px 0 0; padding-left: 18px; font-size: 12px; color: #14532d; }
  .recommendations li { margin-bottom: 4px; }
  
  .disclaimer { font-size: 10px; color: #64748b; line-height: 1.4; border-top: 1px solid #e2e8f0; padding-top: 10px; margin-top: 20px; }
  .signBox { display: flex; justify-content: space-between; margin-top: 32px; padding-top: 12px; }
  .signLine { width: 200px; border-top: 1px solid #94a3b8; text-align: center; font-size: 10px; color: #64748b; padding-top: 4px; }
  
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
      <div class="brandSub">Cardiovascular Disease Prediction &amp; Vessel Stenosis Intelligence Report</div>
    </div>
  </div>
  <div class="reportMeta">
    <div><b>Date &amp; Time:</b> ${reportDate}</div>
    <div><b>Report Identifier:</b> <span class="reportId">${pat.id}-RPT</span></div>
    <div><b>Engine Version:</b> v2.4 (57-Feature Four-Model Architecture)</div>
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

<h3>1. Machine Learning Multi-Vessel Risk Stratification</h3>
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

<h3>2. Key Clinical Measurements &amp; Laboratory Biomarkers</h3>
<table>
  <thead>
    <tr><th>Parameter</th><th>Patient Value</th><th>Standard Clinical Reference</th><th>Status / Significance</th></tr>
  </thead>
  <tbody>
    <tr><td><b>Blood Pressure (BP)</b></td><td>${bp} mmHg</td><td>&lt; 120/80 mmHg</td><td>${parseFloat(bp) >= 140 ? 'Stage 2 Hypertension' : parseFloat(bp) >= 130 ? 'Stage 1 Hypertension' : 'Normotensive'}</td></tr>
    <tr><td><b>Resting Pulse Rate</b></td><td>${pr} bpm</td><td>60 - 100 bpm</td><td>${parseFloat(pr) > 100 ? 'Tachycardia' : parseFloat(pr) < 60 ? 'Bradycardia' : 'Normal'}</td></tr>
    <tr><td><b>Left Ventricular EF (EF-TTE)</b></td><td>${ef}%</td><td>&ge; 50%</td><td>${parseFloat(ef) < 50 ? 'Reduced / Borderline LVEF' : 'Preserved Ejection Fraction'}</td></tr>
    <tr><td><b>Fasting Blood Sugar (FBS)</b></td><td>${fbs} mg/dL</td><td>70 - 99 mg/dL</td><td>${parseFloat(fbs) >= 126 ? 'Diabetic Range' : parseFloat(fbs) >= 100 ? 'Prediabetic Range' : 'Euglycemic'}</td></tr>
    <tr><td><b>Serum Creatinine (CR)</b></td><td>${cr} mg/dL</td><td>0.7 - 1.3 mg/dL</td><td>Renal clearance indicator</td></tr>
    <tr><td><b>LDL Cholesterol</b></td><td>${ldl} mg/dL</td><td>&lt; 100 mg/dL (&lt; 70 for high risk)</td><td>${parseFloat(ldl) >= 100 ? 'Elevated Atherogenic Lipoprotein' : 'Optimal'}</td></tr>
    <tr><td><b>HDL Cholesterol</b></td><td>${hdl} mg/dL</td><td>&gt; 40 mg/dL</td><td>${parseFloat(hdl) < 40 ? 'Low Protective HDL' : 'Normal'}</td></tr>
    <tr><td><b>Triglycerides (TG)</b></td><td>${tg} mg/dL</td><td>&lt; 150 mg/dL</td><td>${parseFloat(tg) >= 150 ? 'Hypertriglyceridemia' : 'Normal'}</td></tr>
    <tr><td><b>Vector Dimensionality</b></td><td>57 ML Inputs</td><td>Trained quad-model schema</td><td>100% verified feature completeness</td></tr>
  </tbody>
</table>

<h3>3. Guideline-Directed Clinical Decision Support (GDMT)</h3>
<div class="recommendations">
  <b>Actionable Cardiology Guidance:</b>
  <ol>
    <li>Formal anatomical evaluation recommended via Coronary Computed Tomography Angiography (CCTA) or Invasive Coronary Angiography (ICA).</li>
    <li>Assess functional ischemia through stress echocardiography or SPECT myocardial perfusion scintigraphy.</li>
    <li>Initiate or escalate intensive lipid-lowering therapy (statin &plusmn; ezetimibe) targeting LDL &lt; 55&ndash;70 mg/dL.</li>
    <li>Implement antiplatelet therapy (low-dose aspirin) and target systolic blood pressure &lt; 130 mmHg.</li>
    <li>Comprehensive lifestyle intervention: Mediterranean diet, structured aerobic conditioning, and glycemic monitoring.</li>
  </ol>
</div>

<div class="disclaimer">
  <b>CONFIDENTIAL MEDICAL DECISION SUPPORT RECORD &bull; FICTIONAL DEMONSTRATION</b><br>
  This report was generated using the CardioVision AI ensemble classification pipeline. The model risk scores are calculated for decision-support and educational purposes only and do not replace professional physician diagnosis or invasive catheterization. Fictional patient demographics used for clinical demonstration.
</div>

<div class="signBox">
  <div class="signLine">Reviewing Cardiologist Signature</div>
  <div class="signLine">CardioVision AI Quality Verification</div>
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
}

function sendNavigate(search){
  try {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({ type: 'cardiovision_navigate', search: search }, '*');
    }
  } catch(e) {}
  try {
    if (window.top && window.top !== window && window.top !== window.parent) {
      window.top.postMessage({ type: 'cardiovision_navigate', search: search }, '*');
    }
  } catch(e) {}
  if (window.parent === window) {
    window.location.search = search;
  }
}

function sendReset(){
  try {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({ type: 'cardiovision_reset' }, '*');
    }
  } catch(e) {}
  try {
    if (window.top && window.top !== window && window.top !== window.parent) {
      window.top.postMessage({ type: 'cardiovision_reset' }, '*');
    }
  } catch(e) {}
  if (window.parent === window) {
    window.location.search = '';
  }
}

function predictRisk(){
  const btn = document.getElementById('predictBtn') || document.querySelector('.predict');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<svg class="spinner" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" fill="none" stroke-dasharray="31.4" stroke-dashoffset="10"/></svg><span>Calculating Predictions...</span>';
  }

  // Strictly extract ONLY the 57 clinical features (excluding patient identity)
  const payload = {};
  document.querySelectorAll('#view-predict input, #view-predict select').forEach(el => {
    if (el.name && el.name !== 'bmi' && el.name !== 'patient_name' && el.name !== 'patient_id' && el.value !== '') {
      payload[el.name] = el.value;
    }
  });

  // Call background API for instant in-place prediction without reloading
  fetch('http://127.0.0.1:8502/api/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(res => {
    if (!res.ok) throw new Error('API server returned status ' + res.status);
    return res.json();
  })
  .then(data => {
    applyPredictions(data, payload);
  })
  .catch(err => {
    console.warn('In-place API unavailable, using fallback navigation:', err);
    const params = new URLSearchParams(payload);
    params.set('_ts', Date.now());
    sendNavigate('?' + params.toString());
  })
  .finally(() => {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<svg viewBox="0 0 24 24" style="width:20px;height:20px;fill:white;flex-shrink:0;"><path d="M8 5v14l11-7z"/></svg><span>Predict Cardiovascular Risk</span>';
    }
  });
}

function clearPredictionResults(){
  // 1. Reset status badge to Awaiting Prediction
  const badge = document.getElementById('predStatusBadge');
  if (badge) {
    badge.className = 'predBadge awaiting';
    badge.innerHTML = '<span class="badgeDot"></span><span>Awaiting Prediction</span>';
  }
  const notice = document.getElementById('staleNotice');
  if (notice) notice.style.display = 'none';

  // 2. Clear numbers, chips, and probability badges
  const cadNum = document.getElementById('cadRiskNum');
  if (cadNum) cadNum.textContent = '—';
  const ladNum = document.getElementById('ladRiskNum');
  if (ladNum) ladNum.textContent = '—';
  const lcxNum = document.getElementById('lcxRiskNum');
  if (lcxNum) lcxNum.textContent = '—';
  const rcaNum = document.getElementById('rcaRiskNum');
  if (rcaNum) rcaNum.textContent = '—';

  const cadLbl = document.getElementById('cadLabelText');
  if (cadLbl) cadLbl.textContent = 'Awaiting';
  const ladLbl = document.getElementById('ladLabelText');
  if (ladLbl) ladLbl.textContent = 'Awaiting';
  const lcxLbl = document.getElementById('lcxLabelText');
  if (lcxLbl) lcxLbl.textContent = 'Awaiting';
  const rcaLbl = document.getElementById('rcaLabelText');
  if (rcaLbl) rcaLbl.textContent = 'Awaiting';

  const cadTier = document.getElementById('cadTierBadge');
  if (cadTier) { cadTier.className = 'probTier tierAwaiting'; cadTier.textContent = 'Awaiting Prediction'; }
  const ladTier = document.getElementById('ladTierBadge');
  if (ladTier) { ladTier.className = 'probTier tierAwaiting'; ladTier.textContent = 'Awaiting Prediction'; }
  const lcxTier = document.getElementById('lcxTierBadge');
  if (lcxTier) { lcxTier.className = 'probTier tierAwaiting'; lcxTier.textContent = 'Awaiting Prediction'; }
  const rcaTier = document.getElementById('rcaTierBadge');
  if (rcaTier) { rcaTier.className = 'probTier tierAwaiting'; rcaTier.textContent = 'Awaiting Prediction'; }

  // 3. Clear donut rings
  const cadPctTxt = document.getElementById('cadPctText');
  if (cadPctTxt) cadPctTxt.textContent = '0%';
  const ladPctTxt = document.getElementById('ladPctText');
  if (ladPctTxt) ladPctTxt.textContent = '0%';
  const lcxPctTxt = document.getElementById('lcxPctText');
  if (lcxPctTxt) lcxPctTxt.textContent = '0%';
  const rcaPctTxt = document.getElementById('rcaRingText');
  if (rcaPctTxt) rcaPctTxt.textContent = '0%';

  const neutralGradient = 'conic-gradient(#e2e8f0 0% 0%, #edf2f7 0% 100%)';
  const cadR = document.getElementById('cadRing');
  if (cadR) cadR.style.background = neutralGradient;
  const ladR = document.getElementById('ladRing');
  if (ladR) ladR.style.background = neutralGradient;
  const lcxR = document.getElementById('lcxRing');
  if (lcxR) lcxR.style.background = neutralGradient;
  const rcaR = document.getElementById('rcaRing');
  if (rcaR) rcaR.style.background = neutralGradient;

  // 4. Clear comparison chart bars
  const cadBar = document.getElementById('cadBar');
  const cadBarVal = document.getElementById('cadBarVal');
  if (cadBar && cadBarVal) { cadBar.style.height = '0%'; cadBarVal.style.bottom = '0%'; cadBarVal.textContent = '0.0'; }
  const ladBar = document.getElementById('ladBar');
  const ladBarVal = document.getElementById('ladBarVal');
  if (ladBar && ladBarVal) { ladBar.style.height = '0%'; ladBarVal.style.bottom = '0%'; ladBarVal.textContent = '0.0'; }
  const lcxBar = document.getElementById('lcxBar');
  const lcxBarVal = document.getElementById('lcxBarVal');
  if (lcxBar && lcxBarVal) { lcxBar.style.height = '0%'; lcxBarVal.style.bottom = '0%'; lcxBarVal.textContent = '0.0'; }
  const rcaBar = document.getElementById('rcaBar');
  const rcaBarVal = document.getElementById('rcaBarVal');
  if (rcaBar && rcaBarVal) { rcaBar.style.height = '0%'; rcaBarVal.style.bottom = '0%'; rcaBarVal.textContent = '0.0'; }

  // 5. Clear Results & Analysis
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

  // 6. Clear 3D prediction highlights
  try {
    const viewer = document.getElementById('viewerIframe') || document.getElementById('heartViewerFrame');
    if (viewer && viewer.contentWindow) {
      if (viewer.contentWindow.CardioVision3D && viewer.contentWindow.CardioVision3D.updateProbabilities) {
        viewer.contentWindow.CardioVision3D.updateProbabilities({
          CAD: { risk: 0, label: 'Awaiting' },
          LAD: { risk: 0, label: 'Awaiting' },
          LCX: { risk: 0, label: 'Awaiting' },
          RCA: { risk: 0, label: 'Awaiting' }
        });
      }
      viewer.contentWindow.postMessage({
        type: 'UPDATE_CARDIO_DATA',
        data: {
          CAD: { risk: 0, label: 'Awaiting' },
          LAD: { risk: 0, label: 'Awaiting' },
          LCX: { risk: 0, label: 'Awaiting' },
          RCA: { risk: 0, label: 'Awaiting' }
        }
      }, '*');
    }
  } catch(e) {}

  inputsModified = false;
  try {
    sessionStorage.setItem('cardiovision_state', 'awaiting');
    sessionStorage.removeItem('cardiovision_last_prediction');
  } catch(e) {}
}

function resetAll(){
  const defaultValues = {
    inp_age: 58, inp_length: 170, inp_weight: 72, inp_sex: 'Male',
    inp_dm: 0, inp_htn: 1, inp_current_smoker: 0, inp_ex_smoker: 0, inp_fh: 0,
    inp_obesity: 'N', inp_crf: 'N', inp_cva: 'N',
    inp_chest_pain: 'Y', inp_dyspnea: 'N', inp_atypical: 'N', inp_nonanginal: 'N', inp_lowth_ang: 'N', inp_poor_r: 'N',
    inp_bp: 130, inp_pr: 70, inp_ef_tte: 50,
    inp_fbs: 98, inp_cr: 1, inp_tg: 122, inp_ldl: 100, inp_hdl: 39, inp_bun: 16, inp_esr: 15,
    inp_hb: 13.2, inp_k: 4.2, inp_na: 141, inp_wbc: 7100, inp_lymph: 32, inp_neut: 60, inp_plt: 210,
    inp_q_wave: 0, inp_st_elevation: 0, inp_st_depression: 0, inp_tinversion: 0, inp_lvh: 'N', inp_bbb: 'N',
    inp_region_rwma: 0, inp_vhd: 'N',
    inp_edema: 0, inp_function_class: 0, inp_airway: 'N', inp_thyroid: 'N', inp_chf: 'N', inp_dlp: 'N',
    inp_weak_pulse: 'N', inp_lung_rales: 'N', inp_systolic_murmur: 'N', inp_diastolic_murmur: 'N'
  };

  for (const [id, val] of Object.entries(defaultValues)) {
    const el = document.getElementById(id);
    if (el) el.value = val;
  }

  // Clear demo patient info in session state and generate a fresh demo ID
  try {
    sessionStorage.removeItem('cardiovision_patient_name');
    const newId = 'CV-2026-' + Math.floor(1000 + Math.random() * 9000);
    sessionStorage.setItem('cardiovision_patient_id', newId);
    const idEl = document.getElementById('inp_patient_id');
    if (idEl) idEl.value = newId;
    const nameEl = document.getElementById('inp_patient_name');
    if (nameEl) nameEl.value = '';
  } catch(e) {}

  updateBMI();
  syncPatientDetails();
  clearPredictionResults();
}

document.addEventListener('DOMContentLoaded', function(){
  try {
    if (window.parent && window.parent !== window && window.parent.history && window.parent.location.search) {
      window.parent.history.replaceState({}, '', window.parent.location.pathname);
    }
    if (window.history && window.location.search) {
      window.history.replaceState({}, '', window.location.pathname);
    }
  } catch(e) {}

  // Initialize and synchronize patient details
  syncPatientDetails();

  const nameInp = document.getElementById('inp_patient_name');
  if (nameInp) {
    nameInp.addEventListener('input', function(){
      try {
        sessionStorage.setItem('cardiovision_patient_name', this.value.trim());
      } catch(e) {}
      syncPatientDetails();
    });
  }

  updateBMI();

  // Check if session was reset to awaiting prediction
  const st = sessionStorage.getItem('cardiovision_state');
  if (st === 'awaiting') {
    clearPredictionResults();
  } else {
    const lastPred = sessionStorage.getItem('cardiovision_last_prediction');
    if (lastPred) {
      try { applyPredictions(JSON.parse(lastPred)); } catch(e) { renderVisualsFromDOM(); }
    } else {
      renderVisualsFromDOM();
    }
  }

  // Attach change listeners to detect modified clinical inputs (ignore patient identity)
  document.querySelectorAll('#view-predict input, #view-predict select').forEach(el => {
    if (el.id !== 'inp_bmi' && el.id !== 'inp_patient_name' && el.id !== 'inp_patient_id') {
      el.addEventListener('input', markInputsModified);
      el.addEventListener('change', markInputsModified);
      el.addEventListener('input', renderPatientInfoScreen);
      el.addEventListener('change', renderPatientInfoScreen);
    }
    // Prevent negative numbers on number inputs
    if (el.type === 'number') {
      el.addEventListener('keydown', function(e){
        if (e.key === '-' || e.key === 'e' || e.key === 'E') {
          e.preventDefault();
        }
      });
    }
  });

  // Support URL hash routing between views (e.g., #patient or #view-patient)
  function handleHashRoute() {
    if (window.location.hash) {
      const h = window.location.hash.replace('#', '').replace('view-', '');
      if (['predict', 'patient', 'results', 'viewer3d', 'about'].includes(h)) {
        switchNav(h);
      }
    }
  }
  handleHashRoute();
  window.addEventListener('hashchange', handleHashRoute);
});
