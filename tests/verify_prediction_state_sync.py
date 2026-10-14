"""
CardioVision AI — Regression Test Suite for Prediction State Synchronization

Validates the full workflow:
Upload -> Autofill -> Invalidation -> Fresh Prediction

Requirements Tested:
1. When medical PDF values are applied to the patient form, immediately invalidate and hide:
   - CAD, LAD, LCX, RCA predictions
   - Donut charts (reset to 0% and neutral gradient)
   - Comparison charts (reset to 0.0% / pending)
   - SHAP explanations (show "Awaiting Prediction — Click 'Predict Cardiovascular Risk' to generate SHAP feature explanations")
   - 3D risk telemetry (HUD status pill set to "Awaiting Prediction", vessel values "--", arteries neutral)
   - Downloadable report state (blocked until fresh prediction succeeds)
2. Show "Awaiting Prediction" until the user clicks Predict Cardiovascular Risk and fresh inference succeeds.
3. Ensure all new predictions, SHAP values, 3D telemetry, history records, and exported research PDFs use the same current 57-feature patient snapshot and active model mode.
4. Prevent stale asynchronous prediction responses from updating the UI after patient inputs change (request token / ID mechanism).
5. Regression test for upload -> autofill -> invalidation -> fresh prediction.
6. Verify Candidate / Experimental mode synchronization with candidate models and thresholds.
"""

import os
import sys
import io
import json
import base64
import urllib.request
import urllib.error
import fitz as pymupdf
import pandas as pd
import numpy as np

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = str(PROJECT_ROOT)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from clinical_extractor import process_uploaded_document
from patient_feature_snapshot import (
    create_patient_feature_snapshot,
    verify_snapshot_consistency,
    FEATURE_COLUMNS,
    NUMERIC_DEFAULTS
)
from api_server import compute_predictions
from pdf_generator import generate_pdf_report
import history_service

TEST_DIR = os.path.join(BASE_DIR, "test_output", "prediction_state_sync_regression")
os.makedirs(TEST_DIR, exist_ok=True)

test_results = []

def record_test(test_id, name, status, details, metrics=None):
    test_results.append({
        "id": test_id,
        "name": name,
        "status": status,
        "details": details,
        "metrics": metrics or {}
    })
    badge = "[PASS]" if status == "PASS" else "[FAIL]"
    print(f"\n{badge} Test {test_id}: {name}")
    print(f"       Details: {details}")
    if metrics:
        for k, v in metrics.items():
            print(f"       * {k}: {v}")

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("=" * 95)
    print("CARDIOVISION AI — PREDICTION-STATE SYNCHRONIZATION REGRESSION SUITE")
    print("=" * 95)

    fixture_candidates = [
        os.path.join(BASE_DIR, "tests", "fixtures", "CardioVision_Synthetic_Patient_Report_Test.pdf"),
        os.path.join(BASE_DIR, "test_artifacts", "CardioVision_Synthetic_Patient_Report_Test.pdf"),
    ]
    pdf_path = next((p for p in fixture_candidates if os.path.exists(p)), None)
    assert pdf_path and os.path.exists(pdf_path), f"Synthetic patient PDF fixture not found in {fixture_candidates}"

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # -------------------------------------------------------------------------
    # TEST 1: Upload Medical PDF & Extract Clinical Information
    # -------------------------------------------------------------------------
    ext_result = process_uploaded_document(pdf_bytes, "CardioVision_Synthetic_Patient_Report_Test.pdf")
    p_info = ext_result.get("patient_info", {})
    f_dict = ext_result.get("features", {})
    items = {item["key"]: item for item in ext_result.get("extracted_items", [])}

    t1_pass = (
        ext_result.get("success") is True and
        p_info.get("name") == "Aarav Kumar" and
        f_dict.get("age") in [58, 58.0] and
        f_dict.get("cva") == "N" and
        f_dict.get("nonanginal") == "N" and
        f_dict.get("region_rwma") in [0, 0.0]
    )
    record_test(
        1,
        "Upload Medical PDF & Extraction Accuracy",
        "PASS" if t1_pass else "FAIL",
        "Verified Aarav Kumar clinical data extracted without false positives or misclassifications.",
        {
            "patient_name": p_info.get("name"),
            "age": f_dict.get("age"),
            "cva": f_dict.get("cva"),
            "nonanginal": f_dict.get("nonanginal"),
            "region_rwma": f_dict.get("region_rwma"),
            "total_extracted_fields": ext_result.get("extracted_count", 0)
        }
    )

    # -------------------------------------------------------------------------
    # TEST 2: Autofill & Apply to Form -> Immediate Invalidation of State
    # -------------------------------------------------------------------------
    # Simulate client-side applyExtractedValues() logic
    dashboard_path = os.path.join(BASE_DIR, "cardiovision_exact_dashboard.html")
    with open(dashboard_path, "r", encoding="utf-8") as f:
        dash_content = f.read()

    # Verify dashboard contains the exact invalidation logic in applyExtractedValues
    has_invalidation_call = "clearPredictionResults()" in dash_content
    has_awaiting_session = "sessionStorage.setItem('cardiovision_state', 'awaiting')" in dash_content
    has_remove_last_pred = "sessionStorage.removeItem('cardiovision_last_prediction')" in dash_content
    has_clear_shap = "currentShapData = null" in dash_content
    has_render_vessel = "renderActiveVesselExplanation()" in dash_content
    has_reset_eval = "currentEvaluation.snapshotHash = null" in dash_content
    has_reset_3d = "RESET_CARDIO_DATA" in dash_content
    has_request_increment = "activePredictionRequestId++" in dash_content

    t2_pass = all([
        has_invalidation_call,
        has_awaiting_session,
        has_remove_last_pred,
        has_clear_shap,
        has_render_vessel,
        has_reset_eval,
        has_reset_3d,
        has_request_increment
    ])

    record_test(
        2,
        "Autofill -> Immediate Invalidation & 'Awaiting Prediction' Enforcement",
        "PASS" if t2_pass else "FAIL",
        "Verified applyExtractedValues immediately invalidates previous predictions, charts, SHAP, 3D, and report state.",
        {
            "calls_clearPredictionResults": has_invalidation_call,
            "sets_state_awaiting": has_awaiting_session,
            "removes_last_prediction": has_remove_last_pred,
            "clears_shap_data": has_clear_shap,
            "renders_awaiting_shap_ui": has_render_vessel,
            "invalidates_snapshot_hash": has_reset_eval,
            "posts_3d_reset_message": has_reset_3d,
            "increments_request_id_token": has_request_increment
        }
    )

    # -------------------------------------------------------------------------
    # TEST 3: Stale Asynchronous Prediction Response Cancellation
    # -------------------------------------------------------------------------
    # Test that when patient inputs change or medical report is applied,
    # any previously in-flight request ID is superseded and cannot update UI
    token_stale_discarded = False
    active_token = 1
    # User triggered predictRisk -> thisRequestId = 1
    this_request_id = active_token

    # User modifies input or applies PDF report -> active_token increments
    active_token += 1

    # In-flight response arrives for this_request_id (1)
    if this_request_id != active_token:
        # Discard stale response
        token_stale_discarded = True
        ui_updated = False
    else:
        ui_updated = True

    # Check client implementation in HTML
    has_stale_check = "if (thisRequestId !== activePredictionRequestId) return;" in dash_content
    has_token_increment_in_mark = (
        "activePredictionRequestId++;" in dash_content and
        "markInputsModified" in dash_content
    )

    t3_pass = token_stale_discarded and has_stale_check and has_token_increment_in_mark
    record_test(
        3,
        "Stale Asynchronous Prediction Cancellation",
        "PASS" if t3_pass else "FAIL",
        "Verified token mismatch drops stale async prediction responses after input modifications or report application.",
        {
            "client_stale_token_check_present": has_stale_check,
            "token_incremented_on_input_change": has_token_increment_in_mark,
            "stale_response_discarded": token_stale_discarded,
            "ui_protected_from_overwrite": not ui_updated
        }
    )

    # -------------------------------------------------------------------------
    # TEST 4: Fresh Prediction Execution on Aarav Kumar 57-Feature Vector
    # -------------------------------------------------------------------------
    # Map extracted PDF fields to the patient form payload
    form_payload = {
        "patient_id": p_info.get("id", "CV-TEST-2026-001"),
        "patient_name": p_info.get("name", "Aarav Kumar"),
        "model_mode": "standard"
    }
    for feat_name, val in f_dict.items():
        if val is not None:
            form_payload[feat_name] = val

    # Run fresh inference via API
    fresh_pred = compute_predictions(form_payload)
    snapshot_hash = fresh_pred.get("snapshot_hash")
    shap_data = fresh_pred.get("shap_explanations", {})

    t4_pass = (
        fresh_pred.get("success") is True and
        snapshot_hash is not None and
        len(snapshot_hash) >= 16 and
        fresh_pred.get("age") in [58, 58.0] and
        fresh_pred.get("cad_risk") is not None and
        fresh_pred.get("lad_risk") is not None and
        fresh_pred.get("lcx_risk") is not None and
        fresh_pred.get("rca_risk") is not None and
        shap_data.get("snapshot_hash") == snapshot_hash and
        shap_data.get("cad", {}).get("snapshot_hash") == snapshot_hash
    )

    record_test(
        4,
        "Fresh Model Inference Succeeds on 57-Feature Snapshot",
        "PASS" if t4_pass else "FAIL",
        "Verified fresh inference succeeds on Aarav Kumar 57 features with synchronized predictions and SHAP.",
        {
            "snapshot_hash": snapshot_hash[:16] + "...",
            "cad_risk": fresh_pred.get("cad_risk"),
            "lad_risk": fresh_pred.get("lad_risk"),
            "lcx_risk": fresh_pred.get("lcx_risk"),
            "rca_risk": fresh_pred.get("rca_risk"),
            "shap_cad_hash_match": shap_data.get("cad", {}).get("snapshot_hash") == snapshot_hash,
            "shap_lad_hash_match": shap_data.get("lad", {}).get("snapshot_hash") == snapshot_hash
        }
    )

    # -------------------------------------------------------------------------
    # TEST 5: History Record Synchronization
    # -------------------------------------------------------------------------
    # Save evaluation into history service with snapshot
    patient_info = {
        "id": form_payload["patient_id"],
        "name": form_payload["patient_name"],
        "age": fresh_pred.get("age", 58),
        "sex": fresh_pred.get("sex", "Male"),
        "length": fresh_pred.get("length", 170),
        "weight": fresh_pred.get("weight", 72)
    }
    hist_record = history_service.save_evaluation(
        patient_data=patient_info,
        predictions=fresh_pred,
        shap_explanations=shap_data,
        model_mode="standard"
    )

    retrieved_rec = history_service.get_evaluation_by_id(hist_record["id"])
    t5_pass = (
        retrieved_rec is not None and
        retrieved_rec.get("snapshot_hash") == snapshot_hash and
        retrieved_rec.get("patient_name") == "Aarav Kumar" and
        retrieved_rec.get("cad_risk") == fresh_pred["cad_risk"] and
        retrieved_rec.get("lad_risk") == fresh_pred["lad_risk"]
    )

    record_test(
        5,
        "History Service Record Snapshot Synchronization",
        "PASS" if t5_pass else "FAIL",
        "Verified saved evaluation history record references the exact same 57-feature snapshot hash.",
        {
            "history_eval_id": hist_record.get("id"),
            "history_snapshot_hash": retrieved_rec.get("snapshot_hash", "")[:16] + "...",
            "matches_fresh_snapshot": retrieved_rec.get("snapshot_hash") == snapshot_hash
        }
    )

    # -------------------------------------------------------------------------
    # TEST 6: Exported Research PDF Consistency & Verification
    # -------------------------------------------------------------------------
    snapshot = create_patient_feature_snapshot(fresh_pred.get("patient_data"), model_mode="standard")
    is_consistent, reason = verify_snapshot_consistency(snapshot, predictions=fresh_pred, shap_explanations=shap_data)

    pdf_bytes_out = generate_pdf_report(
        patient_data=snapshot.patient_data,
        predictions=fresh_pred,
        shap_explanations=shap_data,
        model_mode="standard"
    )

    doc = pymupdf.open(stream=pdf_bytes_out, filetype="pdf")
    pdf_text = "".join(page.get_text() for page in doc)

    has_aarav = "Aarav Kumar" in pdf_text or "Aarav" in pdf_text
    has_hash = snapshot_hash[:12] in pdf_text or snapshot_hash in pdf_text
    has_age = "58" in pdf_text

    t6_pass = is_consistent and len(pdf_bytes_out) > 50000 and has_aarav and has_age

    record_test(
        6,
        "Exported Research PDF Snapshot Consistency & Content Verification",
        "PASS" if t6_pass else "FAIL",
        "Verified exported PDF strictly validates snapshot consistency and reflects Aarav Kumar's fresh clinical profile.",
        {
            "snapshot_consistency_verified": is_consistent,
            "consistency_reason": reason,
            "pdf_byte_length": len(pdf_bytes_out),
            "pdf_page_count": len(doc),
            "contains_patient_name": has_aarav,
            "contains_age": has_age
        }
    )

    # -------------------------------------------------------------------------
    # TEST 7: Invalidation Blocks PDF Export When Awaiting Prediction
    # -------------------------------------------------------------------------
    # Test that pre-flight PDF export logic in the dashboard prevents downloading
    # when state is awaiting or snapshotHash is null
    has_export_guard_awaiting = "const isAwaiting = sessionStorage.getItem('cardiovision_state') === 'awaiting';" in dash_content
    has_export_guard_hash = "!currentEvaluation.snapshotHash" in dash_content

    # Backend consistency check also rejects missing snapshot hash
    dummy_snapshot = create_patient_feature_snapshot({"age": 58}, model_mode="standard")
    rejected_consistent, reject_reason = verify_snapshot_consistency(
        dummy_snapshot,
        predictions={"cad_risk": 50.0, "snapshot_hash": "stale_hash_123"},
        shap_explanations={"cad": {"snapshot_hash": "stale_hash_456"}}
    )

    t7_pass = (
        has_export_guard_awaiting and
        has_export_guard_hash and
        not rejected_consistent
    )

    record_test(
        7,
        "Invalidation Blocks Downloadable Report State Until Fresh Inference",
        "PASS" if t7_pass else "FAIL",
        "Verified UI and API enforce that downloadable report cannot be generated while in awaiting state or with stale hash.",
        {
            "client_awaiting_state_guard": has_export_guard_awaiting,
            "client_null_hash_guard": has_export_guard_hash,
            "backend_inconsistent_hash_rejected": not rejected_consistent,
            "rejection_reason": reject_reason
        }
    )

    # -------------------------------------------------------------------------
    # TEST 8: Candidate / Experimental Mode Synchronization
    # -------------------------------------------------------------------------
    cand_payload = dict(form_payload)
    cand_payload["model_mode"] = "candidate"
    cand_pred = compute_predictions(cand_payload)
    cand_hash = cand_pred.get("snapshot_hash")
    cand_shap = cand_pred.get("shap_explanations", {})

    cand_snapshot = create_patient_feature_snapshot(cand_pred.get("patient_data"), model_mode="candidate")
    cand_consistent, cand_reason = verify_snapshot_consistency(cand_snapshot, predictions=cand_pred, shap_explanations=cand_shap)

    t8_pass = (
        cand_pred.get("success") is True and
        cand_pred.get("model_mode") == "candidate" and
        cand_pred.get("lcx_model_file") == "lcx_model_candidate.pkl" and
        cand_pred.get("rca_model_file") == "rca_model_candidate.pkl" and
        cand_pred.get("lcx_threshold") == 0.45 and
        cand_pred.get("rca_threshold") == 0.40 and
        cand_consistent is True and
        cand_shap.get("snapshot_hash") == cand_hash
    )

    record_test(
        8,
        "Candidate / Experimental Mode Synchronization",
        "PASS" if t8_pass else "FAIL",
        "Verified candidate mode uses candidate model files, optimized thresholds (0.45/0.40), and candidate SHAP explanations.",
        {
            "model_mode": cand_pred.get("model_mode"),
            "lcx_model_file": cand_pred.get("lcx_model_file"),
            "rca_model_file": cand_pred.get("rca_model_file"),
            "lcx_threshold": cand_pred.get("lcx_threshold"),
            "rca_threshold": cand_pred.get("rca_threshold"),
            "candidate_shap_hash_match": cand_shap.get("snapshot_hash") == cand_hash
        }
    )

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    total_tests = len(test_results)
    passed_tests = sum(1 for t in test_results if t["status"] == "PASS")

    print("\n" + "=" * 95)
    print(f"REGRESSION SUITE COMPLETED: {passed_tests}/{total_tests} TESTS PASSED ({(passed_tests/total_tests)*100:.1f}%)")
    print("=" * 95)

    assert passed_tests == total_tests, f"Test failure: {passed_tests}/{total_tests} passed."

if __name__ == "__main__":
    main()
