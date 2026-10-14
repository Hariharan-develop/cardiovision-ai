import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_server import compute_predictions
from pdf_generator import generate_pdf_report
import fitz

print("--- Testing compute_predictions (Standard Mode) ---")
res = compute_predictions({"model_mode": "standard"})
print(f"Success: {res.get('success')}")
print(f"CAD: {res.get('cad_risk')}% ({res.get('cad_label')})")
print(f"LAD: {res.get('lad_risk')}% ({res.get('lad_label')})")
print(f"LCX: {res.get('lcx_risk')}% ({res.get('lcx_label')})")
print(f"RCA: {res.get('rca_risk')}% ({res.get('rca_label')})")

shap_res = res.get('shap_explanations', {})
for k in ['cad', 'lad', 'lcx', 'rca']:
    s = shap_res.get(k, {})
    print(f"  SHAP {k.upper()}: avail={s.get('available')}, scale={s.get('scale')}, base={s.get('base_value')}, output={s.get('model_output')}")

print("\n--- Generating Standard Mode PDF ---")
pdf_bytes = generate_pdf_report(
    patient_data={
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
    },
    predictions=res,
    shap_explanations=shap_res,
    model_mode="standard",
    output_filename="test_output_standard.pdf"
)

doc = fitz.open("test_output_standard.pdf")
print(f"Standard PDF generated! Page count: {len(doc)}, size: {len(pdf_bytes)} bytes")
for i in range(len(doc)):
    page = doc[i]
    pix = page.get_pixmap(dpi=150)
    pix.save(f"test_standard_page_{i+1}.png")
print(f"Rendered {len(doc)} pages as PNGs.")

print("\n--- Testing compute_predictions (Experimental Mode) ---")
res_exp = compute_predictions({"model_mode": "candidate"})
print(f"Success: {res_exp.get('success')}")
print(f"CAD: {res_exp.get('cad_risk')}% ({res_exp.get('cad_label')})")
print(f"LAD: {res_exp.get('lad_risk')}% ({res_exp.get('lad_label')})")
print(f"LCX: {res_exp.get('lcx_risk')}% ({res_exp.get('lcx_label')}) [thresh: {res_exp.get('lcx_threshold')}]")
print(f"RCA: {res_exp.get('rca_risk')}% ({res_exp.get('rca_label')}) [thresh: {res_exp.get('rca_threshold')}]")

shap_exp = res_exp.get('shap_explanations', {})
pdf_bytes_exp = generate_pdf_report(
    patient_data={
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
    },
    predictions=res_exp,
    shap_explanations=shap_exp,
    model_mode="candidate",
    output_filename="test_output_experimental.pdf"
)

doc_exp = fitz.open("test_output_experimental.pdf")
print(f"Experimental PDF generated! Page count: {len(doc_exp)}, size: {len(pdf_bytes_exp)} bytes")
for i in range(len(doc_exp)):
    page = doc_exp[i]
    pix = page.get_pixmap(dpi=150)
    pix.save(f"test_experimental_page_{i+1}.png")
print(f"Rendered {len(doc_exp)} experimental pages as PNGs.")
