# Python script to apply patient UI fixes cleanly to cardiovision_exact_dashboard.html
import re

html_path = "cardiovision_exact_dashboard.html"
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add CSS for .pvSummaryExplainer and .rangeBadge
css_needle = ".pvSummaryMeta { display: flex; flex-direction: column; }"
new_css = """.pvSummaryMeta { display: flex; flex-direction: column; }

/* Summary Explainer */
.pvSummaryExplainer {
  background: #f0f6fd;
  border: 1px solid #cce0f5;
  border-radius: 9px;
  padding: 10px 14px;
  margin-top: -4px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12.5px;
  color: #174276;
  font-weight: 550;
  line-height: 1.4;
}
.pvSummaryExplainer svg {
  width: 17px;
  height: 17px;
  color: #1759e8;
  flex-shrink: 0;
}

/* Subtle Out-of-Range and Reference Status Indicators */
.rangeBadge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 7.5px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 650;
  line-height: 1.25;
  margin-top: 3px;
  vertical-align: middle;
}
.rangeBadge svg {
  width: 11.5px;
  height: 11.5px;
  flex-shrink: 0;
}
.rangeBadge.within {
  background: #f0fdf4;
  color: #15803d;
  border: 1px solid #bbf7d0;
}
.rangeBadge.out {
  background: #fffbeb;
  color: #b45309;
  border: 1px solid #fde68a;
}
.rangeBadge.neutral {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
}"""

if css_needle in content:
    content = content.replace(css_needle, new_css, 1)
    print("1. CSS added successfully.")
else:
    print("ERROR: css_needle not found.")

# 2. Add Explainer HTML below .pvSummaryGrid in #view-patient
grid_end = """      <!-- Three Compact Summary Cards -->
      <div class="pvSummaryGrid">
        <div class="pvSummaryCard">
          <div class="pvSummaryIcon blue">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          </div>
          <div class="pvSummaryMeta">
            <span class="pvSummaryLabel">Model Input Features</span>
            <span class="pvSummaryValue" id="pvStatTotalFeatures">57</span>
            <span class="pvSummarySub">Total Quad-Ensemble Vector</span>
          </div>
        </div>

        <div class="pvSummaryCard">
          <div class="pvSummaryIcon green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
          </div>
          <div class="pvSummaryMeta">
            <span class="pvSummaryLabel">Numeric Features</span>
            <span class="pvSummaryValue" id="pvStatNumericFeatures">34</span>
            <span class="pvSummarySub">Continuous &amp; Discrete Measurements</span>
          </div>
        </div>

        <div class="pvSummaryCard">
          <div class="pvSummaryIcon purple">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="5" width="22" height="14" rx="7"/><circle cx="16" cy="12" r="3"/></svg>
          </div>
          <div class="pvSummaryMeta">
            <span class="pvSummaryLabel">One-Hot Encoded Features</span>
            <span class="pvSummaryValue" id="pvStatEncodedFeatures">23</span>
            <span class="pvSummarySub">Binary &amp; Multi-Class Indicators</span>
          </div>
        </div>
      </div>"""

new_grid_with_explainer = grid_end + """

      <!-- Attribute & Feature Transformation Explanation -->
      <div class="pvSummaryExplainer">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        <span>54 clinical attributes are collected through the patient form and transformed into 57 model input features, including 34 numeric and 23 one-hot encoded features.</span>
      </div>"""

if grid_end in content:
    content = content.replace(grid_end, new_grid_with_explainer, 1)
    print("2. Explainer HTML added successfully.")
else:
    print("ERROR: grid_end not found.")

# 3. Update updateBMI() function to trigger renderPatientInfoScreen
old_bmi_fn = """function updateBMI(){
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
}"""

new_bmi_fn = """function updateBMI(){
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
}"""

if old_bmi_fn in content:
    content = content.replace(old_bmi_fn, new_bmi_fn, 1)
    print("3. updateBMI() updated successfully.")
else:
    print("ERROR: old_bmi_fn not found.")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Batch 1 applied.")
