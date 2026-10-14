import os
import sys
import re

sys.path.insert(0, r"c:\Users\hario\Downloads\CardioVision-AI")

with open(r"c:\Users\hario\Downloads\CardioVision-AI\pdf_generator.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace PageBreak with nothing/Spacer
code_dynamic = code.replace("story.append(PageBreak())", "# story.append(PageBreak())")

# Save as test_dyn_gen.py
with open(r"c:\Users\hario\Downloads\CardioVision-AI\.gemini\test_dyn_gen.py", "w", encoding="utf-8") as f:
    f.write(code_dynamic)

import importlib
test_dyn_gen = importlib.import_module(".gemini.test_dyn_gen")

from api_server import compute_predictions
import pymupdf

preds = compute_predictions({})
patient_data = {
    "id": "CV-2026-8492",
    "displayName": "Alex Morgan (Demo Patient)",
    "age": 58,
    "sex": "Male",
    "length": 170,
    "weight": 72,
    "bp": 130,
    "pr": 70,
    "ef_tte": 50,
    "fbs": 98,
    "cr": 1.0,
    "ldl": 100,
    "hdl": 39,
    "tg": 122
}

out_pdf = r"c:\Users\hario\Downloads\CardioVision-AI\.gemini\test_dynamic.pdf"
pdf_bytes = test_dyn_gen.generate_pdf_report(
    patient_data=patient_data,
    predictions=preds,
    shap_explanations=preds.get("shap_explanations", {}),
    model_mode="standard",
    output_filename=out_pdf
)

doc = pymupdf.open(out_pdf)
print(f"Dynamic PDF total pages: {len(doc)}")
for i, page in enumerate(doc):
    print(f"Page {i+1} rect: {page.rect}")
    text = page.get_text()
    print(f"Page {i+1} lines count: {len(text.splitlines())} | sample: {text.splitlines()[:3]}")
