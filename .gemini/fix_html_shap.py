import re

with open('cardiovision_exact_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add <meta charset="utf-8"> at the very top if not present
if '<meta charset="utf-8">' not in content:
    content = '<meta charset="utf-8">\n' + content

# 2. Fix mojibake and special characters
content = content.replace('—', '&mdash;')
content = content.replace('â€”', '&mdash;')
content = content.replace('Δ', '&Delta;')
content = content.replace('Î”', '&Delta;')
content = content.replace('◄', '&larr;')
content = content.replace('►', '&rarr;')

# 3. Replace {RCA_PERF_ACC} etc defaults in static table with standard mode defaults
content = content.replace('<td id="tableLcxAcc">{LCX_PERF_ACC}</td>', '<td id="tableLcxAcc">{LCX_PERF_ACC}</td>')
content = content.replace('<td id="printLcxAcc">{LCX_PERF_ACC}</td>', '<td id="printLcxAcc">{LCX_PERF_ACC}</td>')

# Ensure the caution text fallback is clean
content = content.replace(
    '<div id="perfCautionText">{PERF_CAUTION_TEXT}</div>',
    '<div id="perfCautionText">{PERF_CAUTION_TEXT}</div>'
)

# 4. Insert <script id="initialShapDataJson" type="application/json"> right before </head> or before main script
if '<script id="initialShapDataJson"' not in content:
    json_script = '\n<script id="initialShapDataJson" type="application/json">{SHAP_DATA_JSON}</script>\n'
    # Place right before the script tag containing updateModeUI
    target_pos = content.find('let currentModelMode =')
    if target_pos != -1:
        content = content[:target_pos] + json_script + content[target_pos:]

# 5. Fix JS initialization of INITIAL_SHAP_DATA to be robust
old_shap_init = """window.INITIAL_SHAP_DATA = {SHAP_DATA_JSON};
let currentExplainVessel = 'cad';
let currentShapData = window.INITIAL_SHAP_DATA || {};
let waterfallExpanded = false;"""

new_shap_init = """let initialShapData = null;
try {
  const shapScriptEl = document.getElementById('initialShapDataJson');
  if (shapScriptEl && shapScriptEl.textContent && !shapScriptEl.textContent.includes('SHAP_DATA_JSON')) {
    initialShapData = JSON.parse(shapScriptEl.textContent);
  }
} catch(e) {
  console.warn('Initial SHAP parse error:', e);
}
window.INITIAL_SHAP_DATA = initialShapData;
let currentExplainVessel = 'cad';
let currentShapData = window.INITIAL_SHAP_DATA || {};
let waterfallExpanded = false;"""

if old_shap_init in content:
    content = content.replace(old_shap_init, new_shap_init, 1)

# 6. Add loadInitialShapIfEmpty function and call on load
old_hash_init = """window.addEventListener('hashchange', handleHashRoute);
  if (typeof renderActiveVesselExplanation === 'function') {
    renderActiveVesselExplanation();
  }"""

new_hash_init = """window.addEventListener('hashchange', handleHashRoute);
  if (typeof updateModeUI === 'function') {
    updateModeUI(currentModelMode);
  }
  if (typeof renderActiveVesselExplanation === 'function') {
    renderActiveVesselExplanation();
  }
  if (!currentShapData || !currentShapData.cad) {
    fetch('http://127.0.0.1:8502/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_mode: currentModelMode })
    })
    .then(r => r.json())
    .then(d => {
      if (d && d.shap_explanations) {
        currentShapData = d.shap_explanations;
        renderActiveVesselExplanation();
      }
    })
    .catch(e => console.log('Background SHAP fetch skipped:', e));
  }"""

if old_hash_init in content:
    content = content.replace(old_hash_init, new_hash_init, 1)

# 7. In renderActiveVesselExplanation, ensure clean entity rendering
content = content.replace('Log-odds scale (Î” log-odds)', 'Log-odds scale (&Delta; log-odds)')

with open('cardiovision_exact_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated cardiovision_exact_dashboard.html successfully!")
