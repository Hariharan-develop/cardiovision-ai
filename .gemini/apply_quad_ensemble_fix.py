# Script to update Quad-Ensemble to Four-Model Input Vector and ensure badges are clearly informational
with open("cardiovision_exact_dashboard.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Replace Quad-Ensemble references
text = text.replace(
    "<p>Complete clinical profile, biomarker measurements, and quad-ensemble model input vector.</p>",
    "<p>Complete clinical profile, biomarker measurements, and four-model input vector.</p>"
)

text = text.replace(
    '<span class="pvSummarySub">Total Quad-Ensemble Vector</span>',
    '<span class="pvSummarySub">Four-Model Input Vector</span>'
)

text = text.replace(
    '<li><b>Quad-Ensemble Machine Learning:</b> 4 independent models predicting overall coronary artery disease (<code>cad_model.pkl</code>) and vessel-specific significant stenosis for Left Anterior Descending (<code>lad_model.pkl</code>), Left Circumflex (<code>lcx_model.pkl</code>), and Right Coronary Artery (<code>rca_model.pkl</code>).</li>',
    '<li><b>Four-Model Machine Learning Architecture:</b> 4 independent specialized models predicting overall coronary artery disease (<code>cad_model.pkl</code>) and vessel-specific significant stenosis for Left Anterior Descending (<code>lad_model.pkl</code>), Left Circumflex (<code>lcx_model.pkl</code>), and Right Coronary Artery (<code>rca_model.pkl</code>).</li>'
)

text = text.replace(
    '<div><b>Engine Version:</b> v2.4 (57-Feature Quad-Ensemble)</div>',
    '<div><b>Engine Version:</b> v2.4 (57-Feature Four-Model Architecture)</div>'
)

# 2. Update notice box in #view-patient
old_notice = """        <div>
          <b>Clinical Reference Range &amp; Measurement Notice:</b> Standard clinical reference ranges and descriptions displayed above are informational medical benchmarks for evaluation context and do not constitute stand-alone diagnostic criteria. The clinical training dataset records a single resting blood pressure value representing resting systolic blood pressure (BP, Systolic); diastolic blood pressure was not separately measured. All 57 model feature values synchronize dynamically with the active input parameters.
        </div>"""

new_notice = """        <div>
          <b>Clinical Reference Range &amp; Measurement Notice:</b> Status badges and reference intervals are strictly informational medical benchmarks for evaluation context, not diagnostic determinations or clinical diagnoses. The clinical dataset records resting systolic blood pressure only (diastolic blood pressure was not recorded). All 57 model feature values synchronize dynamically with the active input parameters.
        </div>"""

if old_notice in text:
    text = text.replace(old_notice, new_notice, 1)
    print("Notice box updated successfully.")

# 3. Ensure badges in getClinicalData() are explicitly labeled informational
# Specifically for BMI and BP and other attributes
text = text.replace(
    "makeBadge('out', 'Below standard adult BMI range')",
    "makeBadge('out', 'Below standard adult BMI range (Informational)')"
)
text = text.replace(
    "makeBadge('within', 'Within standard adult BMI range')",
    "makeBadge('within', 'Within standard adult BMI range (Informational)')"
)
text = text.replace(
    "makeBadge('out', 'Above standard adult BMI range (Overweight)')",
    "makeBadge('out', 'Above standard adult BMI range: Overweight (Informational)')"
)
text = text.replace(
    "makeBadge('out', 'Above standard adult BMI range (Obesity)')",
    "makeBadge('out', 'Above standard adult BMI range: Obesity (Informational)')"
)

text = text.replace(
    "makeBadge('within', 'Within standard systolic reference (< 120 mmHg)')",
    "makeBadge('within', 'Within standard systolic reference (< 120 mmHg, Informational)')"
)
text = text.replace(
    "makeBadge('out', 'Elevated systolic reference (120–129 mmHg)')",
    "makeBadge('out', 'Elevated systolic reference (120–129 mmHg, Informational)')"
)
text = text.replace(
    "makeBadge('out', 'Above standard systolic reference (≥ 130 mmHg)')",
    "makeBadge('out', 'Above standard systolic reference (≥ 130 mmHg, Informational)')"
)

with open("cardiovision_exact_dashboard.html", "w", encoding="utf-8") as f:
    f.write(text)

print("cardiovision_exact_dashboard.html updated.")
