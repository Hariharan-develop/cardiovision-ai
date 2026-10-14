"""
CardioVision AI — Regression Test Suite for Synthetic Patient Report & Edge Cases
Validates:
1. Exact extraction from 'CardioVision_Synthetic_Patient_Report_Test.pdf'
   - Patient Name = Aarav Kumar
   - Age = 58
   - Patient ID = CV-TEST-2026-001
   - Height = 170 cm
   - Weight = 72 kg
   - BMI = 24.9
   - CVA = N
   - Nonanginal Pain = N
   - Region RWMA = 0
   - All 17 Vitals / Biomarkers
2. Document with missing age (returns Not Found, value is None)
3. Document with conflicting ages (returns Needs Review with conflict note)
4. Document with multiple page numbers (ignores page numbers 1, 2, 3, 4 without false conflict)
5. Exact 57-feature matrix creation and feature ordering
6. REST API /api/upload-report validation
"""

import os
import sys
import io
import json
import base64
import urllib.request
import urllib.error

BASE_DIR = r"c:\Users\hario\Downloads\CardioVision-AI"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import pymupdf
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

from clinical_extractor import process_uploaded_document, parse_clinical_text
from patient_feature_snapshot import create_patient_feature_snapshot, FEATURE_COLUMNS

TEST_DIR = os.path.join(BASE_DIR, "test_output", "synthetic_regression")
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
        print(f"       Metrics: {metrics}")


# ==============================================================================
# TEST 1: Actual PDF Extraction (CardioVision_Synthetic_Patient_Report_Test.pdf)
# ==============================================================================
def run_test_1():
    pdf_path = os.path.join(BASE_DIR, "test_artifacts", "CardioVision_Synthetic_Patient_Report_Test.pdf")
    assert os.path.exists(pdf_path), f"Fixture not found at {pdf_path}"

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    res = process_uploaded_document(pdf_bytes, "CardioVision_Synthetic_Patient_Report_Test.pdf")
    assert res["success"] is True, f"Extraction failed: {res.get('error')}"

    p_info = res["patient_info"]
    f_dict = res["features"]
    items = {item["key"]: item for item in res["extracted_items"]}

    # 1. Patient Name
    assert p_info["name"] == "Aarav Kumar", f"Expected 'Aarav Kumar', got {repr(p_info['name'])}"
    assert items["patient_name"]["value"] == "Aarav Kumar"
    assert items["patient_name"]["status"] == "Extracted"

    # 2. Age
    assert f_dict["age"] == 58.0 or f_dict["age"] == 58, f"Expected 58, got {repr(f_dict['age'])}"
    assert items["age"]["value"] == 58.0
    assert items["age"]["status"] == "Extracted"
    assert "multiple" not in str(items["age"].get("notes") or "").lower()

    # 3. Patient ID
    assert p_info["id"] == "CV-TEST-2026-001", f"Expected 'CV-TEST-2026-001', got {repr(p_info['id'])}"
    assert items["patient_id"]["value"] == "CV-TEST-2026-001"

    # 4. Height
    assert f_dict["length"] == 170.0, f"Expected 170.0, got {repr(f_dict['length'])}"

    # 5. Weight
    assert f_dict["weight"] == 72.0, f"Expected 72.0, got {repr(f_dict['weight'])}"

    # 6. BMI
    assert f_dict["bmi"] == 24.9, f"Expected 24.9, got {repr(f_dict['bmi'])}"

    # 7. CVA
    assert f_dict["cva"] == "N", f"Expected 'N', got {repr(f_dict['cva'])}"
    assert items["cva"]["value"] == "N"
    assert items["cva"]["status"] == "Extracted"

    # 8. Nonanginal Pain
    assert f_dict["nonanginal"] == "N", f"Expected 'N', got {repr(f_dict['nonanginal'])}"
    assert items["nonanginal"]["value"] == "N"
    assert items["nonanginal"]["status"] == "Extracted"

    # 9. Region RWMA
    assert f_dict["region_rwma"] == 0 or f_dict["region_rwma"] == 0.0, f"Expected 0, got {repr(f_dict['region_rwma'])}"
    assert items["region_rwma"]["value"] == 0.0 or items["region_rwma"]["value"] == 0
    assert items["region_rwma"]["status"] == "Extracted"

    # 10. All Laboratory and Vitals values
    expected_labs = {
        "bp": 142.0,
        "pr": 78.0,
        "ef_tte": 54.0,
        "fbs": 112.0,
        "cr": 1.10,
        "tg": 185.0,
        "ldl": 130.0,
        "hdl": 45.0,
        "bun": 18.0,
        "esr": 18.0,
        "hb": 13.8,
        "k": 4.3,
        "na": 139.0,
        "wbc": 7400.0,
        "lymph": 31.0,
        "neut": 61.0,
        "plt": 235.0,
    }
    for k_lab, exp_val in expected_labs.items():
        act_val = f_dict.get(k_lab)
        assert act_val is not None, f"Lab {k_lab} was Not Found!"
        assert abs(act_val - exp_val) < 0.05, f"Lab {k_lab}: expected {exp_val}, got {act_val}"

    # Also check other key history & cardiac items
    assert f_dict["dm"] == 1
    assert f_dict["htn"] == 1
    assert f_dict["current_smoker"] == 0
    assert f_dict["ex_smoker"] == 1
    assert f_dict["fh"] == 0
    assert f_dict["obesity"] == "N"
    assert f_dict["crf"] == "N"
    assert f_dict["chest_pain"] == "Y"
    assert f_dict["dyspnea"] == "Y"
    assert f_dict["atypical"] == "N"
    assert f_dict["lowth_ang"] == "N"
    assert f_dict["q_wave"] == 0
    assert f_dict["st_elevation"] == 0
    assert f_dict["st_depression"] == 1
    assert f_dict["tinversion"] == 0
    assert f_dict["lvh"] == "N"
    assert f_dict["poor_r"] == "N"
    assert f_dict["bbb"] == "N"
    assert f_dict["vhd"] == "N"
    assert f_dict["function_class"] == 2

    record_test(
        1, "Synthetic PDF 10 Target Fields Verification", "PASS",
        "Aarav Kumar (Name), 58 (Age), CV-TEST-2026-001 (ID), 170 (Ht), 72 (Wt), 24.9 (BMI), N (CVA), N (Nonanginal), 0 (RWMA), and all 17 labs 100% matched.",
        {"extracted_count": res["extracted_count"], "name": p_info["name"], "age": f_dict["age"], "cva": f_dict["cva"], "nonanginal": f_dict["nonanginal"], "rwma": f_dict["region_rwma"]}
    )


# ==============================================================================
# TEST 2: Document With Missing Age
# ==============================================================================
def run_test_2():
    pdf_path = os.path.join(TEST_DIR, "test_missing_age.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("<b>PATIENT MEDICAL INTAKE</b>", styles["Title"]),
        Paragraph("<b>Patient Name:</b> Priya Sharma &nbsp;&nbsp;&nbsp; <b>ID:</b> CV-NO-AGE-001", styles["Normal"]),
        Spacer(1, 10),
        Paragraph("<b>Clinical Notes:</b> Patient reports with elevated blood pressure and palpitations. Age is not documented on the intake sheet.", styles["Normal"]),
        Paragraph("BP: 135/85 mmHg, Pulse Rate: 76 bpm, FBS: 98 mg/dL", styles["Normal"]),
    ]
    doc.build(story)

    with open(pdf_path, "rb") as f:
        res = process_uploaded_document(f.read(), "test_missing_age.pdf")

    assert res["success"] is True
    assert res["features"].get("age") is None
    items = {item["key"]: item for item in res["extracted_items"]}
    assert items["age"]["status"] == "Not Found"
    assert items["age"]["value"] is None

    record_test(
        2, "Document With Missing Age", "PASS",
        "Correctly returned status='Not Found' and value=None without inventing or guessing patient age.",
        {"age_status": items["age"]["status"], "age_value": items["age"]["value"]}
    )


# ==============================================================================
# TEST 3: Document With Conflicting Ages Across Pages
# ==============================================================================
def run_test_3():
    pdf_path = os.path.join(TEST_DIR, "test_conflicting_ages.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("<b>PAGE 1 — CLINICAL EVALUATION</b>", styles["Title"]),
        Paragraph("<b>Patient Name:</b> Vikram Patel &nbsp;&nbsp;&nbsp; <b>Age:</b> 58 years", styles["Normal"]),
        Spacer(1, 15),
        Paragraph("Initial examination notes: Resting BP 130/80 mmHg.", styles["Normal"]),
        PageBreak(),
        Paragraph("<b>PAGE 2 — FOLLOW-UP VISIT SUMMARY</b>", styles["Title"]),
        Paragraph("<b>Patient:</b> Vikram Patel &nbsp;&nbsp;&nbsp; <b>Age:</b> 62 years", styles["Normal"]),
        Spacer(1, 15),
        Paragraph("Follow-up laboratory assessment: FBS 105 mg/dL.", styles["Normal"]),
    ]
    doc.build(story)

    with open(pdf_path, "rb") as f:
        res = process_uploaded_document(f.read(), "test_conflicting_ages.pdf")

    assert res["success"] is True
    items = {item["key"]: item for item in res["extracted_items"]}
    age_item = items["age"]
    assert age_item["status"] == "Needs Review", f"Expected 'Needs Review', got {age_item['status']}"
    assert "Multiple readings found" in str(age_item["notes"]), f"Expected conflict notes, got {age_item['notes']}"
    assert "58.0" in age_item["notes"] and "62.0" in age_item["notes"]

    record_test(
        3, "Document With Conflicting Ages", "PASS",
        f"Correctly flagged conflict: status='Needs Review' with note '{age_item['notes']}'.",
        {"age_status": age_item["status"], "confidence": age_item["confidence"], "notes": age_item["notes"]}
    )


# ==============================================================================
# TEST 4: Document With Multiple Page Numbers (No False Conflicts)
# ==============================================================================
def run_test_4():
    pdf_path = os.path.join(TEST_DIR, "test_page_numbers_no_conflict.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("<b>HOSPITAL MEDICAL RECORD — Page 1</b>", styles["Title"]),
        Paragraph("Document Header | Page 1 of 4 | Section 1", styles["Normal"]),
        Paragraph("<b>Patient Name:</b> Aarav Kumar &nbsp;&nbsp;&nbsp; <b>Age:</b> 58 years", styles["Normal"]),
        Paragraph("Page 1 Notes: Normal sinus rhythm.", styles["Normal"]),
        PageBreak(),
        Paragraph("<b>HOSPITAL MEDICAL RECORD — Page 2</b>", styles["Title"]),
        Paragraph("Document Header | Page 2 of 4 | Section 2", styles["Normal"]),
        Paragraph("Page 2 Clinical Findings: Fasting blood glucose 112 mg/dL.", styles["Normal"]),
        PageBreak(),
        Paragraph("<b>HOSPITAL MEDICAL RECORD — Page 3</b>", styles["Title"]),
        Paragraph("Document Header | Page 3 of 4 | Section 3", styles["Normal"]),
        Paragraph("Page 3 Echo Report: LVEF 54%.", styles["Normal"]),
        PageBreak(),
        Paragraph("<b>HOSPITAL MEDICAL RECORD — Page 4</b>", styles["Title"]),
        Paragraph("Document Header | Page 4 of 4 | Section 4", styles["Normal"]),
        Paragraph("Page 4 Discharge Summary: Prescriptions given.", styles["Normal"]),
    ]
    doc.build(story)

    with open(pdf_path, "rb") as f:
        res = process_uploaded_document(f.read(), "test_page_numbers_no_conflict.pdf")

    assert res["success"] is True
    items = {item["key"]: item for item in res["extracted_items"]}
    age_item = items["age"]
    assert age_item["status"] == "Extracted", f"Expected 'Extracted', got {age_item['status']}"
    assert age_item["value"] == 58.0, f"Expected 58.0, got {age_item['value']}"
    assert age_item["notes"] is None, f"Expected no conflict notes from page numbers, got {age_item['notes']}"

    record_test(
        4, "Document With Multiple Page Numbers", "PASS",
        "Disregarded page numbers 1, 2, 3, 4 without triggering false age conflicts. Extracted Age=58 with status='Extracted'.",
        {"age_status": age_item["status"], "age_value": age_item["value"], "notes": age_item["notes"]}
    )


# ==============================================================================
# TEST 5: Exact 57-Feature Canonical Ordering & Form Autofill Sync
# ==============================================================================
def run_test_5():
    pdf_path = os.path.join(BASE_DIR, "test_artifacts", "CardioVision_Synthetic_Patient_Report_Test.pdf")
    with open(pdf_path, "rb") as f:
        res = process_uploaded_document(f.read(), "CardioVision_Synthetic_Patient_Report_Test.pdf")

    f_dict = res["features"]
    snapshot = create_patient_feature_snapshot(f_dict, model_mode="standard", strict=False)

    assert len(snapshot.X.columns) == 57, f"Expected 57 features, got {len(snapshot.X.columns)}"
    assert list(snapshot.X.columns) == FEATURE_COLUMNS, "Feature order does not match FEATURE_COLUMNS"
    
    # Check key features in matrix
    assert snapshot.X["Age"].iloc[0] == 58.0
    assert snapshot.X["Length"].iloc[0] == 170.0
    assert snapshot.X["Weight"].iloc[0] == 72.0
    assert snapshot.X["BMI"].iloc[0] == 24.9
    assert snapshot.X["BP"].iloc[0] == 142.0
    assert snapshot.X["PR"].iloc[0] == 78.0
    assert snapshot.X["FBS"].iloc[0] == 112.0
    assert snapshot.X["CR"].iloc[0] == 1.10
    assert snapshot.X["TG"].iloc[0] == 185.0
    assert snapshot.X["LDL"].iloc[0] == 130.0
    assert snapshot.X["HDL"].iloc[0] == 45.0
    assert snapshot.X["EF-TTE"].iloc[0] == 54.0
    assert snapshot.X["Region RWMA"].iloc[0] == 0.0

    record_test(
        5, "57-Feature Canonical Ordering Sync", "PASS",
        f"Snapshot validated with exact 57 canonical features in precise schema order. Age=58, Length=170, Weight=72, BMI=24.9, RWMA=0.0.",
        {"features_count": len(snapshot.X.columns), "exact_canonical_order": True}
    )


# ==============================================================================
# TEST 6: REST API /api/upload-report Endpoint Integration
# ==============================================================================
def run_test_6():
    pdf_path = os.path.join(BASE_DIR, "test_artifacts", "CardioVision_Synthetic_Patient_Report_Test.pdf")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    b64_data = base64.b64encode(pdf_bytes).decode("utf-8")
    api_url = "http://127.0.0.1:8502/api/upload-report"
    req = urllib.request.Request(
        api_url,
        data=json.dumps({"filename": "CardioVision_Synthetic_Patient_Report_Test.pdf", "file_data": b64_data}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        body = json.loads(resp.read().decode("utf-8"))

    assert body["success"] is True
    assert body["patient_info"]["name"] == "Aarav Kumar"
    assert body["patient_info"]["id"] == "CV-TEST-2026-001"
    assert body["features"]["age"] == 58.0
    assert body["features"]["cva"] == "N"
    assert body["features"]["nonanginal"] == "N"
    assert body["features"]["region_rwma"] == 0.0 or body["features"]["region_rwma"] == 0

    record_test(
        6, "REST API /api/upload-report Integration", "PASS",
        "REST API returned HTTP 200 with success=True, Name='Aarav Kumar', ID='CV-TEST-2026-001', Age=58, CVA='N', Nonanginal='N', RWMA=0.",
        {"http_status": 200, "name": body["patient_info"]["name"], "extracted_count": body["extracted_count"]}
    )


def main():
    print("================================================================================")
    print("      CARDIOVISION AI — SYNTHETIC PATIENT REPORT REGRESSION TEST SUITE         ")
    print("================================================================================")
    run_test_1()
    run_test_2()
    run_test_3()
    run_test_4()
    run_test_5()
    run_test_6()

    total = len(test_results)
    passed = sum(1 for t in test_results if t["status"] == "PASS")
    print("\n" + "="*80)
    print(f"REGRESSION SUITE COMPLETED: {passed}/{total} TESTS PASSED (100%)")
    print("="*80)

if __name__ == "__main__":
    main()
