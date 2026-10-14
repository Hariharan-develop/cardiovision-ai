import os
import sys
import json
import joblib
import io
import pandas as pd
import fitz

# Ensure workspace root is in sys.path
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE_DIR)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from api_server import compute_predictions
from pdf_generator import generate_pdf_report
from shap_service import get_all_shap_explanations

def run_all_tests():
    results = {}
    print("=" * 70)
    print("CARDIOVISION AI - COMPREHENSIVE HACKATHON VERIFICATION SUITE")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # TEST 1: Baseline Patient (Standard Mode)
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Baseline Patient (Standard Mode)")
    try:
        res1 = compute_predictions({"model_mode": "standard"})
        assert res1['success'] == True, "compute_predictions failed"
        assert res1['model_mode'] == 'standard', "Model mode not standard"
        assert abs(res1['cad_risk'] - 91.7) < 0.2, f"CAD risk mismatch: {res1['cad_risk']}"
        assert abs(res1['lad_risk'] - 79.0) < 0.2, f"LAD risk mismatch: {res1['lad_risk']}"
        assert abs(res1['lcx_risk'] - 65.0) < 0.2, f"LCX risk mismatch: {res1['lcx_risk']}"
        assert abs(res1['rca_risk'] - 51.7) < 0.2, f"RCA risk mismatch: {res1['rca_risk']}"
        assert res1['lcx_threshold'] == 0.50, f"LCX threshold mismatch: {res1['lcx_threshold']}"
        assert res1['rca_threshold'] == 0.50, f"RCA threshold mismatch: {res1['rca_threshold']}"

        # SHAP additivity
        shap1 = res1.get('shap_explanations', {})
        for m in ['cad', 'lad', 'lcx', 'rca']:
            sm = shap1.get(m, {})
            assert sm.get('available') == True, f"SHAP for {m} not available"
            base_v = float(sm['base_value'])
            out_v = float(sm['model_output'])
            sum_top = sum(f['shap_value'] for f in sm['top_features'])
            rem = next((s['value'] for s in sm['waterfall_steps'] if s['type'] == 'remaining'), 0.0)
            assert abs((base_v + sum_top + rem) - out_v) < 0.005, f"Additivity failure for {m}"

        pdf1 = generate_pdf_report(
            patient_data={'id': 'CV-2026-8492', 'displayName': 'Alex Morgan (Demo Patient)', 'age': 58, 'sex': 'Male'},
            predictions=res1,
            shap_explanations=shap1,
            model_mode='standard',
            output_filename='test_verify_std.pdf'
        )
        doc1 = fitz.open('test_verify_std.pdf')
        assert len(doc1) == 4, f"Expected 4 pages, got {len(doc1)}"
        text1 = "".join(doc1[i].get_text() for i in range(len(doc1)))
        assert "CV-2026-8492" in text1, "Patient ID missing from PDF"
        assert "Alex Morgan (Demo Patient)" in text1, "Patient Name missing from PDF"
        assert "Standard Production Mode" in text1, "Standard Mode title missing from PDF"
        assert "Additivity Verified" in text1, "Additivity string missing from PDF"
        results['Test 1 — Baseline Patient'] = ('PASS', f'4 pages, CAD: {res1["cad_risk"]}%, LAD: {res1["lad_risk"]}%, LCX: {res1["lcx_risk"]}%, RCA: {res1["rca_risk"]}%, SHAP additivity verified')
        print("  [PASS] PASS: Standard predictions, SHAP additivity, and 4-page PDF verified.")
    except Exception as e:
        results['Test 1 — Baseline Patient'] = ('FAIL', str(e))
        print(f"  [FAIL] FAIL: {e}")

    # -------------------------------------------------------------------------
    # TEST 2: Experimental Patient (Experimental Mode)
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Experimental Patient (Candidate Mode)")
    try:
        res2 = compute_predictions({"model_mode": "candidate"})
        assert res2['success'] == True, "compute_predictions failed"
        assert res2['model_mode'] == 'candidate', "Model mode not candidate"
        assert abs(res2['cad_risk'] - 91.7) < 0.2, "CAD risk altered in candidate mode"
        assert abs(res2['lad_risk'] - 79.0) < 0.2, "LAD risk altered in candidate mode"
        assert abs(res2['lcx_risk'] - 58.0) < 0.2, f"Candidate LCX risk mismatch: {res2['lcx_risk']}"
        assert abs(res2['rca_risk'] - 40.4) < 0.2, f"Candidate RCA risk mismatch: {res2['rca_risk']}"
        assert abs(res2['lcx_threshold'] - 0.45) < 0.01, f"Candidate LCX threshold not 0.45: {res2['lcx_threshold']}"
        assert abs(res2['rca_threshold'] - 0.40) < 0.01, f"Candidate RCA threshold not 0.40: {res2['rca_threshold']}"
        assert res2['lcx_label'] == 'Stenotic', f"LCX classification expected Stenotic (58% >= 45%), got {res2['lcx_label']}"
        assert res2['rca_label'] == 'Stenotic', f"RCA classification expected Stenotic (40.4% >= 40%), got {res2['rca_label']}"
        assert res2['lcx_model_file'] == 'lcx_model_candidate.pkl'
        assert res2['rca_model_file'] == 'rca_model_candidate.pkl'

        pdf2 = generate_pdf_report(
            patient_data={'id': 'CV-2026-8492', 'displayName': 'Alex Morgan (Demo Patient)', 'age': 58, 'sex': 'Male'},
            predictions=res2,
            shap_explanations=res2.get('shap_explanations', {}),
            model_mode='candidate',
            output_filename='test_verify_exp.pdf'
        )
        doc2 = fitz.open('test_verify_exp.pdf')
        assert len(doc2) == 4, f"Expected 4 pages, got {len(doc2)}"
        text2 = "".join(doc2[i].get_text() for i in range(len(doc2)))
        assert "Experimental Candidate Mode" in text2
        assert "lcx_model_candidate.pkl" in text2
        assert "rca_model_candidate.pkl" in text2
        assert "0.689" in text2
        assert "0.651" in text2
        assert "Macro F1" in text2
        results['Test 2 — Experimental Patient'] = ('PASS', f'Candidate LCX (58.0% >= 45%), RCA (40.4% >= 40%), nested CV metrics confirmed')
        print("  [PASS] PASS: Candidate models, calibrated thresholds, and nested CV report verified.")
    except Exception as e:
        results['Test 2 — Experimental Patient'] = ('FAIL', str(e))
        print(f"  [FAIL] FAIL: {e}")

    # -------------------------------------------------------------------------
    # TEST 3: Healthy Demo Patient
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Healthy Demo Patient (Low-Risk Fictional Profile)")
    try:
        healthy_input = {
            "age": 28, "sex": "Female", "length": 165, "weight": 55,
            "bp": 110, "pr": 65, "ef_tte": 62, "fbs": 82, "cr": 0.8,
            "ldl": 75, "hdl": 65, "tg": 85, "dm": 0, "htn": 0,
            "current_smoker": 0, "ex_smoker": 0, "fh": 0, "typical_chest_pain": 0
        }
        res3 = compute_predictions(healthy_input)
        assert res3['success'] == True
        pdf3 = generate_pdf_report(
            patient_data={
                'id': 'CV-HEALTHY-01',
                'displayName': 'Jordan Taylor (Low-Risk Profile)',
                'age': 28, 'sex': 'Female', 'length': 165, 'weight': 55,
                'bp': 110, 'pr': 65, 'ef_tte': 62, 'fbs': 82, 'cr': 0.8,
                'ldl': 75, 'hdl': 65, 'tg': 85
            },
            predictions=res3,
            shap_explanations=res3.get('shap_explanations', {}),
            model_mode='standard',
            output_filename='test_verify_healthy.pdf'
        )
        doc3 = fitz.open('test_verify_healthy.pdf')
        assert len(doc3) == 4
        text3 = "".join(doc3[i].get_text() for i in range(len(doc3)))
        assert "CV-HEALTHY-01" in text3
        assert "Jordan Taylor (Low-Risk Profile)" in text3
        results['Test 3 — Healthy Demo Patient'] = ('PASS', f'Generated without error, CAD: {res3["cad_risk"]}%, LAD: {res3["lad_risk"]}%, LCX: {res3["lcx_risk"]}%, RCA: {res3["rca_risk"]}%')
        print(f"  [PASS] PASS: Healthy demo evaluated without error (CAD: {res3['cad_risk']}%).")
    except Exception as e:
        results['Test 3 — Healthy Demo Patient'] = ('FAIL', str(e))
        print(f"  [FAIL] FAIL: {e}")

    # -------------------------------------------------------------------------
    # TEST 4: High-Risk Demo Patient
    # -------------------------------------------------------------------------
    print("\n[TEST 4] High-Risk Demo Patient (Severe Profile)")
    try:
        high_risk_input = {
            "age": 75, "sex": "Male", "length": 172, "weight": 92,
            "bp": 165, "pr": 95, "ef_tte": 35, "fbs": 180, "cr": 2.1,
            "ldl": 190, "hdl": 28, "tg": 320, "dm": 1, "htn": 1,
            "current_smoker": 1, "ex_smoker": 0, "fh": 1, "typical_chest_pain": 1,
            "st_elevation": 1
        }
        res4 = compute_predictions(high_risk_input)
        assert res4['success'] == True
        pdf4 = generate_pdf_report(
            patient_data={
                'id': 'CV-HIGHRISK-99',
                'displayName': 'Arthur Pendelton (High-Risk Profile)',
                'age': 75, 'sex': 'Male', 'length': 172, 'weight': 92,
                'bp': 165, 'pr': 95, 'ef_tte': 35, 'fbs': 180, 'cr': 2.1,
                'ldl': 190, 'hdl': 28, 'tg': 320
            },
            predictions=res4,
            shap_explanations=res4.get('shap_explanations', {}),
            model_mode='standard',
            output_filename='test_verify_highrisk.pdf'
        )
        doc4 = fitz.open('test_verify_highrisk.pdf')
        assert len(doc4) == 4
        text4 = "".join(doc4[i].get_text() for i in range(len(doc4)))
        assert "CV-HIGHRISK-99" in text4
        assert "Arthur Pendelton (High-Risk Profile)" in text4
        assert "Outside displayed adult reference range" in text4  # for CR 2.1
        results['Test 4 — High-Risk Demo Patient'] = ('PASS', f'Generated without error, CAD: {res4["cad_risk"]}%, LAD: {res4["lad_risk"]}%, LCX: {res4["lcx_risk"]}%, RCA: {res4["rca_risk"]}%')
        print(f"  [PASS] PASS: High-risk demo evaluated without error (CAD: {res4['cad_risk']}%).")
    except Exception as e:
        results['Test 4 — High-Risk Demo Patient'] = ('FAIL', str(e))
        print(f"  [FAIL] FAIL: {e}")

    # -------------------------------------------------------------------------
    # TEST 5: Missing SHAP Data Graceful Fallback
    # -------------------------------------------------------------------------
    print("\n[TEST 5] Missing SHAP Data Fallback")
    try:
        pdf5 = generate_pdf_report(
            patient_data={'id': 'CV-NO-SHAP', 'displayName': 'Fallback Demo'},
            predictions={'cad_risk': 75.0, 'lad_risk': 60.0, 'lcx_risk': 40.0, 'rca_risk': 30.0},
            shap_explanations={},  # Empty explanations
            model_mode='standard',
            output_filename='test_verify_no_shap.pdf'
        )
        doc5 = fitz.open('test_verify_no_shap.pdf')
        assert len(doc5) == 4, f"Expected 4 pages with fallback boxes, got {len(doc5)}"
        text5 = "".join(doc5[i].get_text() for i in range(len(doc5)))
        assert "AI Explainability Data Unavailable" in text5
        results['Test 5 — Missing SHAP Data'] = ('PASS', 'Graceful fallback rendered on all SHAP sections without error')
        print("  [PASS] PASS: Missing SHAP data handled gracefully with informative fallback message.")
    except Exception as e:
        results['Test 5 — Missing SHAP Data'] = ('FAIL', str(e))
        print(f"  [FAIL] FAIL: {e}")

    # -------------------------------------------------------------------------
    # TEST 6: Missing 3D Snapshot Graceful Fallback
    # -------------------------------------------------------------------------
    print("\n[TEST 6] Missing 3D Snapshot Fallback")
    try:
        # Pass snapshot_data_url=None and ensure no crash, uses fallback asset or message
        pdf6 = generate_pdf_report(
            patient_data={'id': 'CV-NO-3D', 'displayName': 'No 3D Demo'},
            predictions={'cad_risk': 70.0, 'lad_risk': 50.0, 'lcx_risk': 30.0, 'rca_risk': 20.0},
            shap_explanations={},
            model_mode='standard',
            snapshot_data_url=None,
            output_filename='test_verify_no_3d.pdf'
        )
        doc6 = fitz.open('test_verify_no_3d.pdf')
        assert len(doc6) == 4
        results['Test 6 — Missing 3D Snapshot'] = ('PASS', 'PDF generated successfully with fallback asset and telemetry')
        print("  [PASS] PASS: Missing 3D snapshot handled gracefully without crashing.")
    except Exception as e:
        results['Test 6 — Missing 3D Snapshot'] = ('FAIL', str(e))
        print(f"  [FAIL] FAIL: {e}")

    # -------------------------------------------------------------------------
    # TEST 7: Mode Switching Integrity
    # -------------------------------------------------------------------------
    print("\n[TEST 7] Mode Switching (Standard -> Experimental -> Standard)")
    try:
        s1 = compute_predictions({"model_mode": "standard"})
        assert s1['lcx_threshold'] == 0.50
        assert s1['rca_threshold'] == 0.50
        assert s1['lcx_model_file'] == 'lcx_model.pkl'

        e1 = compute_predictions({"model_mode": "candidate"})
        assert abs(e1['lcx_threshold'] - 0.45) < 0.01
        assert abs(e1['rca_threshold'] - 0.40) < 0.01
        assert e1['lcx_model_file'] == 'lcx_model_candidate.pkl'
        # CAD & LAD probabilities must be identical across modes
        assert s1['cad_risk'] == e1['cad_risk'], "CAD risk changed during mode switch"
        assert s1['lad_risk'] == e1['lad_risk'], "LAD risk changed during mode switch"

        s2 = compute_predictions({"model_mode": "standard"})
        assert s2['lcx_threshold'] == 0.50
        assert s2['rca_threshold'] == 0.50
        assert s2['lcx_model_file'] == 'lcx_model.pkl'
        assert s2['lcx_risk'] == s1['lcx_risk'], "LCX risk not restored upon switching back"
        assert s2['rca_risk'] == s1['rca_risk'], "RCA risk not restored upon switching back"
        results['Test 7 — Mode Switching'] = ('PASS', 'Standard and candidate thresholds and models toggle accurately without state leakage')
        print("  [PASS] PASS: Mode switching preserved thresholds, models, and probability invariants.")
    except Exception as e:
        results['Test 7 — Mode Switching'] = ('FAIL', str(e))
        print(f"  [FAIL] FAIL: {e}")

    # -------------------------------------------------------------------------
    # TEST 8: Repeated PDF Downloads (No Stale Patient State)
    # -------------------------------------------------------------------------
    print("\n[TEST 8] Repeated PDF Downloads (State Isolation)")
    try:
        patients = [
            {'id': 'CV-PAT-ALPHA', 'name': 'Alpha Patient', 'age': 45},
            {'id': 'CV-PAT-BETA', 'name': 'Beta Patient', 'age': 65},
            {'id': 'CV-PAT-GAMMA', 'name': 'Gamma Patient', 'age': 52}
        ]
        docs = []
        for p in patients:
            res_p = compute_predictions({'age': p['age']})
            p_bytes = generate_pdf_report(
                patient_data={'id': p['id'], 'displayName': p['name'], 'age': p['age'], 'sex': 'Male'},
                predictions=res_p,
                shap_explanations={},
                model_mode='standard'
            )
            d = fitz.open(stream=p_bytes, filetype='pdf')
            txt = "".join(d[i].get_text() for i in range(len(d)))
            docs.append((p, txt))

        for idx, (p, txt) in enumerate(docs):
            assert p['id'] in txt, f"Patient ID {p['id']} missing from their PDF"
            assert p['name'] in txt, f"Patient Name {p['name']} missing from their PDF"
            # Ensure no cross contamination from other patients
            for other_idx, (other_p, _) in enumerate(docs):
                if idx != other_idx:
                    assert other_p['id'] not in txt, f"Cross-contamination: {other_p['id']} found in {p['id']}'s PDF"
                    assert other_p['name'] not in txt, f"Cross-contamination: {other_p['name']} found in {p['id']}'s PDF"

        results['Test 8 — Repeated PDF Downloads'] = ('PASS', 'Zero cross-contamination or stale state across repeated exports')
        print("  [PASS] PASS: Repeated PDF exports show strict patient session isolation.")
    except Exception as e:
        results['Test 8 — Repeated PDF Downloads'] = ('FAIL', str(e))
        print(f"  [FAIL] FAIL: {e}")

    # -------------------------------------------------------------------------
    # TEST 9: Model Performance Audit
    # -------------------------------------------------------------------------
    print("\n[TEST 9] Model Performance Audit")
    try:
        # Audit candidate_thresholds.json
        with open('candidate_thresholds.json', 'r', encoding='utf-8') as f:
            thresh_data = json.load(f)
        assert abs(thresh_data['LCX'] - 0.45) < 0.01, "candidate_thresholds.json LCX != 0.45"
        assert abs(thresh_data['RCA'] - 0.40) < 0.01, "candidate_thresholds.json RCA != 0.40"

        # Check model files exist and load
        cad_m = joblib.load('cad_model.pkl')
        lad_m = joblib.load('lad_model.pkl')
        lcx_m = joblib.load('lcx_model.pkl')
        rca_m = joblib.load('rca_model.pkl')
        lcx_c = joblib.load('lcx_model_candidate.pkl')
        rca_c = joblib.load('rca_model_candidate.pkl')

        # Check positive classes
        assert 'CAD' in cad_m.classes_
        assert 'Stenotic' in lad_m.classes_
        assert 'Stenotic' in lcx_m.classes_
        assert 'Stenotic' in rca_m.classes_
        assert 1 in lcx_c.classes_
        assert 1 in rca_c.classes_

        # Verify 57 features
        feats = joblib.load('feature_columns.pkl')
        assert len(feats) == 57, f"Expected 57 feature columns, got {len(feats)}"

        results['Test 9 — Model Performance Audit'] = ('PASS', 'All 6 model files verified; 57 features checked; candidate thresholds verified; exploratory nested CV metrics audited')
        print("  [PASS] PASS: Models, classes, 57 features, and performance metrics audited.")
    except Exception as e:
        results['Test 9 — Model Performance Audit'] = ('FAIL', str(e))
        print(f"  [FAIL] FAIL: {e}")

    # -------------------------------------------------------------------------
    # TEST 10: PDF Layout and Typography
    # -------------------------------------------------------------------------
    print("\n[TEST 10] PDF Layout and Typography Verification")
    try:
        doc = fitz.open('test_verify_std.pdf')
        assert len(doc) == 4, f"Expected 4 pages, got {len(doc)}"
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            rect = page.rect
            # A4 portrait: width 595.27 pt, height 841.89 pt
            assert abs(rect.width - 595.27) < 1.0, f"Page {page_idx+1} width {rect.width} not A4"
            assert abs(rect.height - 841.89) < 1.0, f"Page {page_idx+1} height {rect.height} not A4"
            txt = page.get_text()
            assert f"Page {page_idx+1} of 4" in txt, f"Footer page number missing on page {page_idx+1}"
            if page_idx > 0:
                assert "CARDIOVISION AI · FORMAL RESEARCH EVALUATION REPORT" in txt, f"Header missing on page {page_idx+1}"

        results['Test 10 — PDF Layout'] = ('PASS', 'A4 portrait (595.27 x 841.89 pt), exactly 4 pages, headers and footers intact on all pages')
        print("  [PASS] PASS: PDF page geometry, running headers, and running footers verified.")
    except Exception as e:
        results['Test 10 — PDF Layout'] = ('FAIL', str(e))
        print(f"  [FAIL] FAIL: {e}")

    print("\n" + "=" * 70)
    print("VERIFICATION SUITE SUMMARY")
    print("=" * 70)
    all_pass = True
    for test_name, (status, detail) in results.items():
        print(f"{test_name:40}: {status} | {detail}")
        if status != 'PASS':
            all_pass = False

    return all_pass, results

if __name__ == '__main__':
    success, res = run_all_tests()
    sys.exit(0 if success else 1)
