import sys
import os

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".gemini"))

import test_dyn_gen
import pymupdf
import api_server

preds = api_server.compute_predictions({})
pdf = test_dyn_gen.generate_pdf_report(
    patient_data={"id": "CV-2026-8492", "length": 170, "weight": 72, "age": 58, "sex": "Male"},
    predictions=preds,
    shap_explanations=preds.get("shap_explanations"),
    model_mode="standard",
    output_filename=".gemini/test_dynamic.pdf"
)

doc = pymupdf.open(".gemini/test_dynamic.pdf")
print("Total pages:", len(doc))
for i, page in enumerate(doc):
    lines = page.get_text().splitlines()
    print(f"Page {i+1} has {len(lines)} text lines. First line: {lines[:2]}")
