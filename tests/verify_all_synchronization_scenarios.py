"""
Comprehensive Verification Suite for CardioVision AI Prediction & SHAP Synchronization

Scenarios tested:
1. Change height from 172 cm to 170 cm and export (verifying fresh SHAP explanation has Length 170.0 and export succeeds).
2. Change height repeatedly before exporting (165 -> 175 -> 172 -> 170) and verify complete clean sync.
3. Switch Standard and Experimental modes (verifying threshold and candidate model isolation: LCX 0.45, RCA 0.40).
4. Export PDFs for two different patients consecutively (Alex Morgan vs Eleanor Vance) with no cross-talk or stale leakage.
5. Submit an intentionally mismatched payload (stale SHAP Length=172 vs snapshot Length=170, and tampered CAD probability) and verify strict HTTP 400.
6. Confirm a valid synchronized export returns HTTP 200 and a readable, valid 3-page PDF with identical patient data and probabilities.
"""

import os
import json
import urllib.request
import urllib.error
import fitz  # PyMuPDF
import joblib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = str(PROJECT_ROOT)
BACKEND_DIR = str(PROJECT_ROOT / "backend")
for p in [BASE_DIR, BACKEND_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

BASE_URL = "http://127.0.0.1:8502"
TEST_DIR = os.path.join(BASE_DIR, "test_output", "sync_reports")
os.makedirs(TEST_DIR, exist_ok=True)

test_results = []

def record(name, passed, details):
    test_results.append({
        "name": name,
        "status": "PASS" if passed else "FAIL",
        "details": details
    })
    status_str = "[PASS]" if passed else "[FAIL]"
    print(f"{status_str} {name}: {details}")

def post_json(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    return urllib.request.urlopen(req)

print("=" * 80)
print("STARTING CARDIOVISION AI SYNCHRONIZATION VERIFICATION SUITE")
print("=" * 80)

# -----------------------------------------------------------------------------
# Scenario 1: Change height from 172 cm to 170 cm and export
# -----------------------------------------------------------------------------
try:
    # 1a. First evaluate at 172 cm
    res_172 = json.loads(post_json("/api/predict", {"length": 172, "weight": 72, "age": 58, "model_mode": "standard"}).read().decode("utf-8"))
    hash_172 = res_172["snapshot_hash"]
    lcx_feat_172 = next(f for f in res_172["shap_explanations"]["lcx"]["top_features"] if f["feature_col"] == "Length")
    val_172 = lcx_feat_172["raw_value"]

    # 1b. Now user changes height to 170 cm (synchronize/predict)
    res_170 = json.loads(post_json("/api/predict", {"length": 170, "weight": 72, "age": 58, "model_mode": "standard"}).read().decode("utf-8"))
    hash_170 = res_170["snapshot_hash"]
    lcx_feat_170 = next(f for f in res_170["shap_explanations"]["lcx"]["top_features"] if f["feature_col"] == "Length")
    val_170 = lcx_feat_170["raw_value"]

    # 1c. Export PDF with matching 170 cm evaluation
    export_payload_170 = {
        "patient_data": res_170["patient_data"],
        "predictions": {
            "cad_risk": res_170["cad_risk"], "cad_label": res_170["cad_label"],
            "lad_risk": res_170["lad_risk"], "lad_label": res_170["lad_label"],
            "lcx_risk": res_170["lcx_risk"], "lcx_label": res_170["lcx_label"],
            "rca_risk": res_170["rca_risk"], "rca_label": res_170["rca_label"],
            "snapshot_hash": hash_170,
            "model_mode": "standard"
        },
        "shap_explanations": res_170["shap_explanations"],
        "model_mode": "standard",
        "snapshot_hash": hash_170
    }
    pdf_resp = post_json("/api/generate-pdf", export_payload_170)
    pdf_bytes = pdf_resp.read()
    pdf_path_1 = os.path.join(TEST_DIR, "scenario1_height_170.pdf")
    with open(pdf_path_1, "wb") as f:
        f.write(pdf_bytes)

    doc = fitz.open(pdf_path_1)
    text_p1 = doc[0].get_text()
    text_p2 = doc[1].get_text()
    doc.close()

    s1_pass = (
        val_172 == 172.0 and
        val_170 == 170.0 and
        hash_172 != hash_170 and
        pdf_resp.status == 200 and
        "170 cm" in text_p1 and
        "172 cm" not in text_p1 and
        f"{res_170['lcx_risk']:.1f}%" in text_p1 and
        f"{res_170['lcx_risk']:.1f}%" in text_p2
    )
    record(
        "Scenario 1: Change height 172 cm -> 170 cm and export",
        s1_pass,
        f"Length 172.0 -> 170.0 correctly recomputed, snapshot hashes distinct ({hash_172} vs {hash_170}), PDF generated with 170.0 cm and identical LCX probability {res_170['lcx_risk']:.1f}%."
    )
except Exception as e:
    record("Scenario 1: Change height 172 cm -> 170 cm and export", False, f"Exception: {e}")

# -----------------------------------------------------------------------------
# Scenario 2: Change height repeatedly before exporting (165 -> 175 -> 172 -> 170)
# -----------------------------------------------------------------------------
try:
    height_sequence = [165, 175, 172, 170]
    last_res = None
    for h in height_sequence:
        resp = post_json("/api/predict", {"length": h, "weight": 70, "age": 60, "model_mode": "standard"})
        last_res = json.loads(resp.read().decode("utf-8"))

    final_feat = next(f for f in last_res["shap_explanations"]["lcx"]["top_features"] if f["feature_col"] == "Length")
    final_val = final_feat["raw_value"]

    export_payload_seq = {
        "patient_data": last_res["patient_data"],
        "predictions": {
            "cad_risk": last_res["cad_risk"], "cad_label": last_res["cad_label"],
            "lad_risk": last_res["lad_risk"], "lad_label": last_res["lad_label"],
            "lcx_risk": last_res["lcx_risk"], "lcx_label": last_res["lcx_label"],
            "rca_risk": last_res["rca_risk"], "rca_label": last_res["rca_label"],
            "snapshot_hash": last_res["snapshot_hash"],
            "model_mode": "standard"
        },
        "shap_explanations": last_res["shap_explanations"],
        "model_mode": "standard",
        "snapshot_hash": last_res["snapshot_hash"]
    }
    pdf_resp = post_json("/api/generate-pdf", export_payload_seq)
    pdf_path_2 = os.path.join(TEST_DIR, "scenario2_repeated_changes.pdf")
    with open(pdf_path_2, "wb") as f:
        f.write(pdf_resp.read())

    doc = fitz.open(pdf_path_2)
    text_p1 = doc[0].get_text()
    doc.close()

    s2_pass = (
        final_val == 170.0 and
        pdf_resp.status == 200 and
        "170 cm" in text_p1 and
        "165 cm" not in text_p1 and
        "175 cm" not in text_p1
    )
    record(
        "Scenario 2: Repeated height changes (165 -> 175 -> 172 -> 170) before export",
        s2_pass,
        f"Final height stabilized at 170.0 cm, SHAP explanation matches 170.0 cm, PDF matches final profile."
    )
except Exception as e:
    record("Scenario 2: Repeated height changes", False, f"Exception: {e}")

# -----------------------------------------------------------------------------
# Scenario 3: Switch Standard and Experimental modes
# -----------------------------------------------------------------------------
try:
    std_data = json.loads(post_json("/api/predict", {"length": 170, "weight": 72, "age": 58, "model_mode": "standard"}).read().decode("utf-8"))
    exp_data = json.loads(post_json("/api/predict", {"length": 170, "weight": 72, "age": 58, "model_mode": "experimental"}).read().decode("utf-8"))

    # Export both
    pdf_std = post_json("/api/generate-pdf", {
        "patient_data": std_data["patient_data"],
        "predictions": std_data,
        "shap_explanations": std_data["shap_explanations"],
        "model_mode": "standard"
    }).read()
    pdf_exp = post_json("/api/generate-pdf", {
        "patient_data": exp_data["patient_data"],
        "predictions": exp_data,
        "shap_explanations": exp_data["shap_explanations"],
        "model_mode": "experimental"
    }).read()

    doc_std = fitz.open(stream=pdf_std, filetype="pdf")
    doc_exp = fitz.open(stream=pdf_exp, filetype="pdf")
    text_std = doc_std[0].get_text()
    text_exp = doc_exp[0].get_text()
    doc_std.close()
    doc_exp.close()

    s3_pass = (
        std_data["model_mode"] == "standard" and
        exp_data["model_mode"] == "candidate" and
        std_data["lcx_model_file"] == "lcx_model.pkl" and
        exp_data["lcx_model_file"] == "lcx_model_candidate.pkl" and
        abs(exp_data["lcx_threshold"] - 0.45) < 1e-4 and
        abs(exp_data["rca_threshold"] - 0.40) < 1e-4 and
        "Standard" in text_std and
        "Experimental" in text_exp
    )
    record(
        "Scenario 3: Switch Standard and Experimental modes",
        s3_pass,
        f"Standard mode uses lcx_model.pkl (50.0% thresh); Experimental mode uses lcx_model_candidate.pkl (LCX thresh 45.0%, RCA thresh 40.0%). PDFs reflect distinct modes."
    )
except Exception as e:
    record("Scenario 3: Switch Standard and Experimental modes", False, f"Exception: {e}")

# -----------------------------------------------------------------------------
# Scenario 4: Export PDFs for two different patients consecutively
# -----------------------------------------------------------------------------
try:
    alex_params = {"id": "CV-2026-8492", "displayName": "Alex Morgan (Demo Patient)", "age": 58, "sex": "Male", "length": 170, "weight": 72}
    eleanor_params = {"id": "CV-2026-9014", "displayName": "Eleanor Vance", "age": 64, "sex": "Female", "length": 162, "weight": 68}

    alex_eval = json.loads(post_json("/api/predict", alex_params).read().decode("utf-8"))
    eleanor_eval = json.loads(post_json("/api/predict", eleanor_params).read().decode("utf-8"))

    pdf_alex = post_json("/api/generate-pdf", {
        "patient_data": {**alex_eval["patient_data"], **alex_params},
        "predictions": alex_eval,
        "shap_explanations": alex_eval["shap_explanations"],
        "model_mode": "standard"
    }).read()

    pdf_eleanor = post_json("/api/generate-pdf", {
        "patient_data": {**eleanor_eval["patient_data"], **eleanor_params},
        "predictions": eleanor_eval,
        "shap_explanations": eleanor_eval["shap_explanations"],
        "model_mode": "standard"
    }).read()

    doc_alex = fitz.open(stream=pdf_alex, filetype="pdf")
    doc_eleanor = fitz.open(stream=pdf_eleanor, filetype="pdf")

    text_alex = "".join([page.get_text() for page in doc_alex])
    text_eleanor = "".join([page.get_text() for page in doc_eleanor])
    doc_alex.close()
    doc_eleanor.close()

    s4_pass = (
        "Alex Morgan" in text_alex and
        "Eleanor Vance" not in text_alex and
        "CV-2026-8492" in text_alex and
        "CV-2026-9014" not in text_alex and
        "Eleanor Vance" in text_eleanor and
        "Alex Morgan" not in text_eleanor and
        "CV-2026-9014" in text_eleanor and
        "CV-2026-8492" not in text_eleanor and
        alex_eval["snapshot_hash"] != eleanor_eval["snapshot_hash"]
    )
    record(
        "Scenario 4: Export PDFs for two different patients consecutively",
        s4_pass,
        f"Alex Morgan and Eleanor Vance PDFs are completely isolated with distinct snapshot hashes ({alex_eval['snapshot_hash']} vs {eleanor_eval['snapshot_hash']}) and zero data leakage."
    )
except Exception as e:
    record("Scenario 4: Export PDFs for two different patients consecutively", False, f"Exception: {e}")

# -----------------------------------------------------------------------------
# Scenario 5: Submit intentionally mismatched payload and verify HTTP 400
# -----------------------------------------------------------------------------
try:
    # 5a. Mismatched SHAP: Patient snapshot has length 170, but SHAP explanation has stale length 172
    res_170 = json.loads(post_json("/api/predict", {"length": 170, "weight": 72, "age": 58}).read().decode("utf-8"))
    res_172 = json.loads(post_json("/api/predict", {"length": 172, "weight": 72, "age": 58}).read().decode("utf-8"))

    mismatched_payload_1 = {
        "patient_data": res_170["patient_data"],  # length 170
        "predictions": res_170,
        "shap_explanations": res_172["shap_explanations"],  # Stale SHAP with length 172!
        "model_mode": "standard"
    }

    status_code_1 = None
    err_msg_1 = ""
    try:
        post_json("/api/generate-pdf", mismatched_payload_1)
    except urllib.error.HTTPError as e:
        status_code_1 = e.code
        err_msg_1 = e.read().decode("utf-8")

    # 5b. Mismatched Prediction: Tampered CAD probability (50% higher than ground truth)
    tampered_predictions = dict(res_170)
    tampered_predictions["cad_risk"] = round(res_170["cad_risk"] + 25.0, 1)

    mismatched_payload_2 = {
        "patient_data": res_170["patient_data"],
        "predictions": tampered_predictions,
        "shap_explanations": res_170["shap_explanations"],
        "model_mode": "standard"
    }

    status_code_2 = None
    err_msg_2 = ""
    try:
        post_json("/api/generate-pdf", mismatched_payload_2)
    except urllib.error.HTTPError as e:
        status_code_2 = e.code
        err_msg_2 = e.read().decode("utf-8")

    s5_pass = (
        status_code_1 == 400 and
        "Stale/cached explanation detected" in err_msg_1 and
        status_code_2 == 400 and
        "CAD prediction mismatch" in err_msg_2
    )
    record(
        "Scenario 5: Submit intentionally mismatched payloads (stale SHAP & tampered risk)",
        s5_pass,
        f"Stale SHAP rejected with HTTP {status_code_1} ('{err_msg_1[:75]}...'); Tampered CAD risk rejected with HTTP {status_code_2} ('{err_msg_2[:75]}...'). Strict validation fully preserved."
    )
except Exception as e:
    record("Scenario 5: Submit intentionally mismatched payloads", False, f"Exception: {e}")

# -----------------------------------------------------------------------------
# Scenario 6: Confirm valid synchronized export returns HTTP 200 and readable PDF
# -----------------------------------------------------------------------------
try:
    valid_eval = json.loads(post_json("/api/predict", {"length": 170, "weight": 72, "age": 58, "bp": 130, "pr": 70, "model_mode": "standard"}).read().decode("utf-8"))
    valid_payload = {
        "patient_data": valid_eval["patient_data"],
        "predictions": valid_eval,
        "shap_explanations": valid_eval["shap_explanations"],
        "model_mode": "standard",
        "snapshot_hash": valid_eval["snapshot_hash"]
    }
    resp = post_json("/api/generate-pdf", valid_payload)
    pdf_bytes = resp.read()

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_count = len(doc)
    p1_text = doc[0].get_text()
    p2_text = doc[1].get_text()
    p3_text = doc[2].get_text() if page_count >= 3 else ""
    doc.close()

    # Check identical probabilities across pages
    cad_val_str = f"{valid_eval['cad_risk']:.1f}%"
    lad_val_str = f"{valid_eval['lad_risk']:.1f}%"
    lcx_val_str = f"{valid_eval['lcx_risk']:.1f}%"
    rca_val_str = f"{valid_eval['rca_risk']:.1f}%"

    s6_pass = (
        resp.status == 200 and
        page_count == 3 and
        cad_val_str in p1_text and
        lad_val_str in p1_text and lad_val_str in p2_text and
        lcx_val_str in p1_text and lcx_val_str in p2_text and
        rca_val_str in p1_text and rca_val_str in p2_text and
        "CardioVision AI" in p1_text and
        "Page 1 of 3" in p1_text
    )
    record(
        "Scenario 6: Valid synchronized export returns HTTP 200 and readable 3-page PDF",
        s6_pass,
        f"HTTP 200 returned, 3 pages generated. CAD ({cad_val_str}), LAD ({lad_val_str}), LCX ({lcx_val_str}), RCA ({rca_val_str}) verified identical across pages."
    )
except Exception as e:
    record("Scenario 6: Valid synchronized export", False, f"Exception: {e}")

print("=" * 80)
total_tests = len(test_results)
passed_tests = sum(1 for t in test_results if t["status"] == "PASS")
print(f"SUMMARY: {passed_tests}/{total_tests} SCENARIOS PASSED")
print("=" * 80)

if passed_tests == total_tests:
    exit(0)
else:
    exit(1)
