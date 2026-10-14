# Script to apply Part 2: getClinicalData updates and badge rendering in renderClinicalTable
with open("cardiovision_exact_dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

# Let's locate getClinicalData() definition up to function getModelData()
start_marker = "function getClinicalData(){\n  const age = parseFloat(document.getElementById('inp_age')?.value || 58);"
end_marker = "function getModelData(){\n  const age = parseFloat(document.getElementById('inp_age')?.value || 58);"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print(f"ERROR: Markers not found: start_idx={start_idx}, end_idx={end_idx}")
    exit(1)

new_getClinicalData = """function makeBadge(status, label) {
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
    bmiBadge = makeBadge('out', 'Below standard adult BMI range');
  } else if (bmiNum <= 24.9) {
    bmiBadge = makeBadge('within', 'Within standard adult BMI range');
  } else if (bmiNum <= 29.9) {
    bmiBadge = makeBadge('out', 'Above standard adult BMI range (Overweight)');
  } else {
    bmiBadge = makeBadge('out', 'Above standard adult BMI range (Obesity)');
  }

  // BP (Resting systolic only measured)
  let bpBadge;
  if (bp < 120) {
    bpBadge = makeBadge('within', 'Within standard systolic reference (< 120 mmHg)');
  } else if (bp <= 129) {
    bpBadge = makeBadge('out', 'Elevated systolic reference (120–129 mmHg)');
  } else {
    bpBadge = makeBadge('out', 'Above standard systolic reference (≥ 130 mmHg)');
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

"""

content = content[:start_idx] + new_getClinicalData + content[end_idx:]
print("getClinicalData updated successfully.")

# Now update renderClinicalTable to include item.badge
old_row1 = """    filtered.forEach(item => {
      html += `<tr>
        <td><b>${item.name}</b></td>
        <td><span style="color:#506e94;font-weight:600;">${item.category}</span></td>
        <td><span class="valHighlight">${item.value}</span></td>
        <td style="color:#4a6486;">${item.ref}</td>
      </tr>`;
    });"""

new_row1 = """    filtered.forEach(item => {
      html += `<tr>
        <td><b>${item.name}</b></td>
        <td><span style="color:#506e94;font-weight:600;">${item.category}</span></td>
        <td>
          <div class="valHighlight">${item.value}</div>
          ${item.badge ? `<div>${item.badge}</div>` : ''}
        </td>
        <td style="color:#4a6486;">${item.ref}</td>
      </tr>`;
    });"""

old_row2 = """        catItems.forEach(item => {
          html += `<tr>
            <td style="padding-left:26px;"><b>${item.name}</b></td>
            <td><span style="color:#506e94;font-weight:600;">${item.category}</span></td>
            <td><span class="valHighlight">${item.value}</span></td>
            <td style="color:#4a6486;">${item.ref}</td>
          </tr>`;
        });"""

new_row2 = """        catItems.forEach(item => {
          html += `<tr>
            <td style="padding-left:26px;"><b>${item.name}</b></td>
            <td><span style="color:#506e94;font-weight:600;">${item.category}</span></td>
            <td>
              <div class="valHighlight">${item.value}</div>
              ${item.badge ? `<div>${item.badge}</div>` : ''}
            </td>
            <td style="color:#4a6486;">${item.ref}</td>
          </tr>`;
        });"""

if old_row1 in content and old_row2 in content:
    content = content.replace(old_row1, new_row1, 1)
    content = content.replace(old_row2, new_row2, 1)
    print("renderClinicalTable row templates updated successfully.")
else:
    print("ERROR: old_row1 or old_row2 not found.")

with open("cardiovision_exact_dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Batch 2 applied successfully.")
