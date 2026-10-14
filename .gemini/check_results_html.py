with open("cardiovision_exact_dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

idx1 = html.find('id="view-results"')
idx2 = html.find('id="view-viewer3d"')
res_section = html[idx1:idx2]

print("Length of res_section:", len(res_section))

# Now let's check each requirement on res_section
import re

def has(pattern, text=res_section):
    return bool(re.search(pattern, text, re.IGNORECASE))

checks = [
    ("1. Heading: Coronary Artery Risk & Prediction Analysis", 
     bool(re.search(r"Coronary Artery Risk\s*(&amp;|&)\s*Prediction Analysis", res_section))),
    
    ("1. Subtitle: Multi-vessel model probability assessment...",
     "Multi-vessel model probability assessment and explainable cardiovascular risk visualization." in res_section),
    
    ("1. Export Clinical Report button",
     "Export Clinical Report" in res_section and "exportClinicalReport" in res_section),
    
    ("2. Patient Summary Bar: Patient Name, ID, Age, Sex, BMI, Date, CAD Pred",
     "resPatientName" in res_section and "resPatientId" in res_section and "resPatientCad" in res_section and "resPatientMeta" in res_section),
    
    ("3. 2x2 cards layout (resCardsGrid)",
     "resCardsGrid" in res_section and "resPredCard" in res_section),
    
    ("3. Four Cards: CAD, LAD, LCX, RCA with colors",
     "#ff4054" in res_section and "#2a86ef" in res_section and "#0fb77d" in res_section and "#ff9900" in res_section),
     
    ("3. Circular SVG probability indicators",
     "resCadCircleBar" in res_section and "resLadCircleBar" in res_section and "resLcxCircleBar" in res_section and "resRcaCircleBar" in res_section),
     
    ("3. Visualization category badges (Low/Mod/High)",
     "resCadTierBadge" in res_section and "resLadTierBadge" in res_section and "resLcxTierBadge" in res_section and "resRcaTierBadge" in res_section),
     
    ("3. Threshold disclaimer (not validated clinical cutoffs)",
     has(r"visualization categor(?:y|ies).*not validated clinical (?:threshold|cutoff)s?")),
     
    ("4. Coronary Probability Comparison Bar Chart",
     "resChartCard" in res_section and "chartCadBar" in res_section and "chartLadBar" in res_section and "chartLcxBar" in res_section and "chartRcaBar" in res_section),
     
    ("5. 57 model input features (not clinical biomarkers)",
     "57 model input features" in res_section and "57 clinical biomarkers" not in res_section),
     
    ("5. Stenosis probability not diameter narrowing",
     has(r"not (?:the same as|equivalent to) (?:percentage )?diameter narrowing")),
     
    ("5. Anatomical territory descriptions",
     has(r"anterior.*myocardium") and has(r"circumflex|lateral") and has(r"right.*ventricle")),
     
    ("6. Panel: Clinical Interpretation & Next Steps",
     bool(re.search(r"Clinical Interpretation\s*(&amp;|&)\s*Next Steps", res_section))),
     
    ("6. Elevated Model-Estimated Probabilities Across Multiple Vessels",
     "Elevated Model-Estimated Probabilities Across Multiple Vessels" in res_section),
     
    ("6. Educational Guidance (no prescriptions/angiography)",
     has(r"statistical model estimate") and "invasive coronary angiography" not in res_section.lower() and "revascularization" not in res_section.lower()),
     
    ("7. Model Performance & Reliability Table with CAD/LAD/LCX/RCA metrics",
     "85.2%" in res_section and "65.6%" in res_section and "57.4%" in res_section and "60.7%" in res_section and "0.917" in res_section),
     
    ("7. Caution notice on LCX and RCA",
     has(r"LCX and RCA have limited predictive discrimination")),
     
    ("8. Understanding the Prediction section",
     "Understanding the Prediction" in res_section),
     
    ("8. Transparent 'Explanation not available' state (no fabricated SHAP)",
     "Explanation not available" in res_section),
     
    ("10. Inputs Modified warning banner",
     "resStaleNotice" in res_section and has(r"Inputs Modified.*Click Predict to Recalculate")),
]

print("=== DETAILED RESULTS SCREEN COMPLIANCE ===")
for name, passed in checks:
    print(f"[{'PASS' if passed else 'FAIL'}] {name}")
