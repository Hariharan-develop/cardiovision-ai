import os
import sys
import json

# Ensure project directory is in path
sys.path.insert(0, r"c:\Users\hario\Downloads\CardioVision-AI")

from api_server import compute_predictions
from pdf_generator import generate_pdf_report
import fitz  # PyMuPDF

print("1. Computing test predictions...")
preds = compute_predictions({})
print(f"Predictions computed. CAD risk: {preds['cad_risk']}%, LAD risk: {preds['lad_risk']}%")
print(f"SHAP available models: {list(preds.get('shap_explanations', {}).keys())}")

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

print("2. Generating PDF with existing generator...")
out_pdf = r"c:\Users\hario\Downloads\CardioVision-AI\.gemini\test_existing.pdf"
os.makedirs(os.path.dirname(out_pdf), exist_ok=True)
pdf_bytes = generate_pdf_report(
    patient_data=patient_data,
    predictions=preds,
    shap_explanations=preds.get("shap_explanations", {}),
    model_mode="standard",
    output_filename=out_pdf
)

doc = fitz.open(out_pdf)
print(f"Existing PDF generated. Total pages: {len(doc)}")
for i, page in enumerate(doc):
    text = page.get_text()
    print(f"Page {i+1} text length: {len(text)} chars | First line: {text.splitlines()[:2]}")
