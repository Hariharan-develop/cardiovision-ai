import sys
import os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".gemini"))

import test_dyn_gen2
import pymupdf
import api_server

preds = api_server.compute_predictions({})
out_pdf = ".gemini/test_dynamic2.pdf"
pdf = test_dyn_gen2.generate_pdf_report(
    patient_data={"id": "CV-2026-8492", "length": 170, "weight": 72, "age": 58, "sex": "Male"},
    predictions=preds,
    shap_explanations=preds.get("shap_explanations"),
    model_mode="standard",
    output_filename=out_pdf
)

doc = pymupdf.open(out_pdf)
print("Total pages:", len(doc))
artifact_dir = r"C:\Users\hario\.gemini\antigravity-ide\brain\e6d8f288-875f-4cd3-a41b-56062ea4a1dc"
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=150)
    out_path = os.path.join(artifact_dir, f"dyn2_page_{i+1}.png")
    pix.save(out_path)
    print(f"Saved {out_path}")
