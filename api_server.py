import os
import sys
import json
import socket
import urllib.parse
from pathlib import Path
import joblib
import pandas as pd
from http.server import HTTPServer, BaseHTTPRequestHandler

# -----------------------------------------------------------------------------
# Base Directory & Module Path Configuration
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
MODELS_DIR = os.path.join(BASE_DIR, "models")

for p in [BACKEND_DIR, BASE_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

def get_model_path(filename: str) -> str:
    for candidate_dir in [MODELS_DIR, BACKEND_DIR, BASE_DIR]:
        full_path = os.path.join(candidate_dir, filename)
        if os.path.exists(full_path):
            return full_path
    return os.path.join(MODELS_DIR, filename)

# -----------------------------------------------------------------------------
# Load Trained Machine Learning Models & Feature Metadata
# -----------------------------------------------------------------------------
cad_model = joblib.load(get_model_path("cad_model.pkl"))
lad_model = joblib.load(get_model_path("lad_model.pkl"))
lcx_model = joblib.load(get_model_path("lcx_model.pkl"))
rca_model = joblib.load(get_model_path("rca_model.pkl"))

# Candidate models (experimental mode) and calibrated thresholds
lcx_model_candidate = joblib.load(get_model_path("lcx_model_candidate.pkl"))
rca_model_candidate = joblib.load(get_model_path("rca_model_candidate.pkl"))

cand_thresh_file = get_model_path("candidate_thresholds.json")
candidate_thresholds = {"LCX": 0.45, "RCA": 0.40}
if os.path.exists(cand_thresh_file):
    try:
        with open(cand_thresh_file, "r", encoding="utf-8") as f:
            candidate_thresholds = json.load(f)
    except Exception:
        pass

CANDIDATE_LCX_THRESH = float(candidate_thresholds.get("LCX", 0.45))
CANDIDATE_RCA_THRESH = float(candidate_thresholds.get("RCA", 0.40))
CANDIDATE_LCX_THRESH_PCT = f"{CANDIDATE_LCX_THRESH * 100.0:.1f}"
CANDIDATE_RCA_THRESH_PCT = f"{CANDIDATE_RCA_THRESH * 100.0:.1f}"

feature_columns = joblib.load(get_model_path("feature_columns.pkl"))
numeric_defaults = joblib.load(get_model_path("numeric_defaults.pkl"))

try:
    from backend.shap_service import get_all_shap_explanations
except ImportError:
    try:
        from shap_service import get_all_shap_explanations
    except ImportError:
        get_all_shap_explanations = None

try:
    from backend.patient_feature_snapshot import (
        create_patient_feature_snapshot,
        verify_snapshot_consistency,
        InconsistentPayloadError,
        PHYSIOLOGICAL_BOUNDS,
    )
    from backend.clinical_extractor import process_uploaded_document
    from backend import history_service
except ImportError:
    from patient_feature_snapshot import (
        create_patient_feature_snapshot,
        verify_snapshot_consistency,
        InconsistentPayloadError,
        PHYSIOLOGICAL_BOUNDS,
    )
    from clinical_extractor import process_uploaded_document
    import history_service

def compute_predictions(params, strict=False):
    mode = str(params.get("model_mode", "standard")).lower()
    is_candidate = mode in ["candidate", "experimental"] or str(params.get("experimental", "0")).lower() in ["1", "true", "yes"]

    # Build validated immutable 57-feature snapshot
    snapshot = create_patient_feature_snapshot(params, model_mode="candidate" if is_candidate else "standard", strict=strict)
    X = snapshot.X

    def class_prob(model, target_label):
        classes = list(model.classes_)
        idx = classes.index(target_label) if target_label in classes else 1
        return float(model.predict_proba(X)[0][idx] * 100.0)

    def get_tier(prob):
        if prob < 50.0: return "tierLow", "Low Est. Prob (<50%)"
        elif prob < 70.0: return "tierModerate", "Moderate Est. Prob (50–69%)"
        else: return "tierHigh", "High Est. Prob (≥70%)"

    cad_r = class_prob(cad_model, "CAD")
    cad_lbl = str(cad_model.predict(X)[0])
    lad_r = class_prob(lad_model, "Stenotic")
    lad_lbl = str(lad_model.predict(X)[0])

    if is_candidate:
        classes_lcx = list(lcx_model_candidate.classes_)
        idx_lcx = classes_lcx.index(1) if 1 in classes_lcx else 1
        lcx_prob_ratio = float(lcx_model_candidate.predict_proba(X)[0][idx_lcx])
        lcx_r = float(lcx_prob_ratio * 100.0)

        classes_rca = list(rca_model_candidate.classes_)
        idx_rca = classes_rca.index(1) if 1 in classes_rca else 1
        rca_prob_ratio = float(rca_model_candidate.predict_proba(X)[0][idx_rca])
        rca_r = float(rca_prob_ratio * 100.0)

        lcx_thresh = float(candidate_thresholds.get("LCX", 0.45))
        rca_thresh = float(candidate_thresholds.get("RCA", 0.40))

        lcx_lbl = "Stenotic" if lcx_prob_ratio >= lcx_thresh else "Normal"
        rca_lbl = "Stenotic" if rca_prob_ratio >= rca_thresh else "Normal"

        lcx_model_file = "lcx_model_candidate.pkl"
        rca_model_file = "rca_model_candidate.pkl"
    else:
        lcx_r = class_prob(lcx_model, "Stenotic")
        lcx_lbl = str(lcx_model.predict(X)[0])
        rca_r = class_prob(rca_model, "Stenotic")
        rca_lbl = str(rca_model.predict(X)[0])
        lcx_thresh = 0.5
        rca_thresh = 0.5
        lcx_model_file = "lcx_model.pkl"
        rca_model_file = "rca_model.pkl"

    cad_tc, cad_tl = get_tier(cad_r)
    lad_tc, lad_tl = get_tier(lad_r)
    lcx_tc, lcx_tl = get_tier(lcx_r)
    rca_tc, rca_tl = get_tier(rca_r)

    # Compute patient-specific SHAP explanations directly on this snapshot
    active_lcx_model = lcx_model_candidate if is_candidate else lcx_model
    active_rca_model = rca_model_candidate if is_candidate else rca_model
    shap_explanations = {}
    if get_all_shap_explanations is not None:
        try:
            shap_explanations = get_all_shap_explanations(
                cad_model, lad_model, active_lcx_model, active_rca_model, X, is_candidate=is_candidate
            )
            shap_explanations["snapshot_hash"] = snapshot.snapshot_hash
            shap_explanations["model_mode"] = snapshot.model_mode
            for v in ["cad", "lad", "lcx", "rca"]:
                if v in shap_explanations and isinstance(shap_explanations[v], dict):
                    shap_explanations[v]["snapshot_hash"] = snapshot.snapshot_hash
                    shap_explanations[v]["model_mode"] = snapshot.model_mode
        except Exception as e:
            shap_explanations = {"available": False, "error": str(e)}

    return {
        "success": True,
        "model_mode": snapshot.model_mode,
        "is_candidate_mode": is_candidate,
        "snapshot_hash": snapshot.snapshot_hash,
        "lcx_threshold": lcx_thresh,
        "rca_threshold": rca_thresh,
        "lcx_thresh_pct": f"{lcx_thresh * 100.0:.1f}",
        "rca_thresh_pct": f"{rca_thresh * 100.0:.1f}",
        "candidate_lcx_threshold": CANDIDATE_LCX_THRESH,
        "candidate_rca_threshold": CANDIDATE_RCA_THRESH,
        "candidate_lcx_thresh_pct": CANDIDATE_LCX_THRESH_PCT,
        "candidate_rca_thresh_pct": CANDIDATE_RCA_THRESH_PCT,
        "lcx_model_file": lcx_model_file,
        "rca_model_file": rca_model_file,
        "cad_risk": round(cad_r, 1), "cad_pct": int(round(cad_r)), "cad_label": cad_lbl,
        "cad_tier_class": cad_tc, "cad_tier_label": cad_tl,
        "lad_risk": round(lad_r, 1), "lad_pct": int(round(lad_r)), "lad_label": lad_lbl,
        "lad_tier_class": lad_tc, "lad_tier_label": lad_tl,
        "lcx_risk": round(lcx_r, 1), "lcx_pct": int(round(lcx_r)), "lcx_label": lcx_lbl,
        "lcx_tier_class": lcx_tc, "lcx_tier_label": lcx_tl,
        "rca_risk": round(rca_r, 1), "rca_pct": int(round(rca_r)), "rca_label": rca_lbl,
        "rca_tier_class": rca_tc, "rca_tier_label": rca_tl,
        "bmi": snapshot.patient_data["bmi"],
        "age": snapshot.patient_data["age"],
        "length": snapshot.patient_data["length"],
        "weight": snapshot.patient_data["weight"],
        "sex": snapshot.patient_data["sex"],
        "bp": snapshot.patient_data["bp"],
        "pr": snapshot.patient_data["pr"],
        "features": snapshot.features_dict,
        "patient_data": snapshot.patient_data,
        "shap_explanations": shap_explanations
    }

import base64

class PredictionAPIHandler(BaseHTTPRequestHandler):
    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors()
        self.end_headers()

    def _serve_file(self, file_path, content_type="text/plain; charset=utf-8"):
        if os.path.exists(file_path) and os.path.isfile(file_path):
            try:
                with open(file_path, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(data)))
                self._set_cors()
                self.end_headers()
                self.wfile.write(data)
                return True
            except Exception:
                pass
        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self._set_cors()
        self.end_headers()
        self.wfile.write(b"File not found")
        return False

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        clean_path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if clean_path.startswith("/models/"):
            rel_name = urllib.parse.unquote(clean_path[len("/models/"):])
            candidate_dirs = [
                os.path.join(BASE_DIR, "assets", "heart_3d"),
                os.path.join(BASE_DIR, "assets", "bodyparts3d"),
                os.path.join(BASE_DIR, "3d-test", "models"),
            ]
            for cdir in candidate_dirs:
                file_path = os.path.normpath(os.path.join(cdir, rel_name))
                if os.path.exists(file_path):
                    self._serve_file(file_path, "text/plain; charset=utf-8")
                    return
            self.send_response(404)
            self.end_headers()
            return
        elif clean_path in ["/dashboard", "/cardiovision_exact_dashboard.html"]:
            dash_path = os.path.join(BASE_DIR, "frontend", "cardiovision_exact_dashboard.html")
            if not os.path.exists(dash_path):
                dash_path = os.path.join(BASE_DIR, "cardiovision_exact_dashboard.html")
            self._serve_file(dash_path, "text/html; charset=utf-8")
            return
        elif any(clean_path.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.svg', '.gif', '.ico']):
            img_name = os.path.basename(clean_path)
            candidates = [
                os.path.join(BASE_DIR, "frontend", "assets", img_name),
                os.path.join(BASE_DIR, "assets", img_name),
                os.path.join(BASE_DIR, img_name),
                os.path.join(BASE_DIR, clean_path.lstrip("/")),
            ]
            for cand in candidates:
                if os.path.exists(cand) and os.path.isfile(cand):
                    ext = os.path.splitext(cand)[1].lower()
                    mime = "image/svg+xml" if ext == ".svg" else ("image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png")
                    self._serve_file(cand, mime)
                    return
        elif clean_path == "/viewer.html" or clean_path == "/3d-viewer":
            v_candidates = [
                os.path.join(BASE_DIR, "frontend", "components", "heart_viewer.html"),
                os.path.join(BASE_DIR, "components", "heart_viewer.html"),
                os.path.join(BASE_DIR, "3d-test", "viewer.html"),
            ]
            for v_path in v_candidates:
                if os.path.exists(v_path):
                    self._serve_file(v_path, "text/html; charset=utf-8")
                    return
            self.send_response(404)
            self.end_headers()
            return
        elif clean_path == "/mesh_manifest.csv":
            m_path = os.path.join(BASE_DIR, "3d-test", "mesh_manifest.csv")
            self._serve_file(m_path, "text/csv; charset=utf-8")
            return
        elif clean_path.startswith("/api/health"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._set_cors()
            self.end_headers()
            res = json.dumps({"status": "ok", "service": "CardioVision Prediction API"})
            self.wfile.write(res.encode("utf-8"))
            return
        elif clean_path.startswith("/api/defaults"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._set_cors()
            self.end_headers()
            res = json.dumps(compute_predictions({}), ensure_ascii=False)
            self.wfile.write(res.encode("utf-8"))
            return
        elif clean_path == "/api/predict":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._set_cors()
            self.end_headers()
            res = json.dumps(compute_predictions({}), ensure_ascii=False)
            self.wfile.write(res.encode("utf-8"))
            return
        elif clean_path == "/api/history":
            search = query_params.get("search", [None])[0]
            mode = query_params.get("mode", [None])[0]
            evals = history_service.get_evaluations(search=search, mode=mode)
            metrics = history_service.get_summary_metrics()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._set_cors()
            self.end_headers()
            res = json.dumps({"success": True, "metrics": metrics, "evaluations": evals}, ensure_ascii=False)
            self.wfile.write(res.encode("utf-8"))
            return
        elif clean_path.startswith("/api/history/") and clean_path.endswith("/export-pdf"):
            eval_id = clean_path[len("/api/history/"):-len("/export-pdf")].strip("/")
            self._handle_history_pdf_export(eval_id)
            return
        elif clean_path.startswith("/api/history/"):
            eval_id = clean_path[len("/api/history/"):].strip("/")
            record = history_service.get_evaluation_by_id(eval_id)
            if record:
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self._set_cors()
                self.end_headers()
                res = json.dumps({"success": True, "evaluation": record}, ensure_ascii=False)
                self.wfile.write(res.encode("utf-8"))
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self._set_cors()
                self.end_headers()
                res = json.dumps({"success": False, "error": f"Evaluation '{eval_id}' not found."})
                self.wfile.write(res.encode("utf-8"))
            return
        elif clean_path in ["/api/generate-pdf", "/api/export-pdf"]:
            try:
                from pdf_generator import generate_pdf_report
                preds = compute_predictions({})
                pdf_bytes = generate_pdf_report(
                    patient_data={"id": "CV-2026-8492", "displayName": "Alex Morgan (Demo Patient)", "age": 58, "sex": "Male"},
                    predictions=preds,
                    shap_explanations=preds.get("shap_explanations", {}),
                    model_mode=preds.get("model_mode", "standard"),
                )
                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Disposition", 'attachment; filename="CardioVision_Research_Report.pdf"')
                self.send_header("Content-Length", str(len(pdf_bytes)))
                self._set_cors()
                self.end_headers()
                self.wfile.write(pdf_bytes)
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self._set_cors()
                self.end_headers()
                res = json.dumps({"success": False, "error": str(e)})
                self.wfile.write(res.encode("utf-8"))
                return
        else:
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._set_cors()
            self.end_headers()
            res = json.dumps({"status": "ready"})
            self.wfile.write(res.encode("utf-8"))

    def do_DELETE(self):
        clean_path = self.path.split("?")[0]
        if clean_path.startswith("/api/history/"):
            eval_id = clean_path[len("/api/history/"):].strip("/")
            deleted = history_service.delete_evaluation(eval_id)
            if deleted:
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self._set_cors()
                self.end_headers()
                res = json.dumps({"success": True, "message": f"Evaluation '{eval_id}' removed."})
                self.wfile.write(res.encode("utf-8"))
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self._set_cors()
                self.end_headers()
                res = json.dumps({"success": False, "error": f"Evaluation '{eval_id}' not found."})
                self.wfile.write(res.encode("utf-8"))
            return
        else:
            self.send_response(405)
            self._set_cors()
            self.end_headers()

    def _handle_history_pdf_export(self, eval_id: str):
        record = history_service.get_evaluation_by_id(eval_id)
        if not record:
            self.send_response(404)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._set_cors()
            self.end_headers()
            res = json.dumps({"success": False, "error": f"Evaluation '{eval_id}' not found."})
            self.wfile.write(res.encode("utf-8"))
            return

        try:
            from pdf_generator import generate_pdf_report
            snapshot = record.get("snapshot", {})
            patient_data = dict(snapshot.get("patient_data", {}))
            for k, v in snapshot.get("features", {}).items():
                if k not in patient_data:
                    patient_data[k] = v
            patient_data["id"] = record.get("patient_id")
            patient_data["displayName"] = record.get("patient_name")
            patient_data["model_mode"] = record.get("model_mode", "standard")

            # Construct predictions payload identical to historical record
            predictions = {
                "model_mode": record.get("model_mode", "standard"),
                "snapshot_hash": record.get("snapshot_hash", ""),
                "cad_risk": record.get("cad_risk", 0.0),
                "cad_label": record.get("cad_label", "CAD"),
                "lad_risk": record.get("lad_risk", 0.0),
                "lad_label": record.get("lad_label", "Normal"),
                "lcx_risk": record.get("lcx_risk", 0.0),
                "lcx_label": record.get("lcx_label", "Normal"),
                "rca_risk": record.get("rca_risk", 0.0),
                "rca_label": record.get("rca_label", "Normal"),
                "lcx_threshold": record.get("lcx_threshold", 0.5),
                "rca_threshold": record.get("rca_threshold", 0.5),
                "features": snapshot.get("features", {}),
            }

            shap_data = record.get("shap_explanations", {})

            pdf_bytes = generate_pdf_report(
                patient_data=patient_data,
                predictions=predictions,
                shap_explanations=shap_data,
                model_mode=record.get("model_mode", "standard"),
                snapshot_data_url=record.get("snapshot_data_url") or record.get("snapshot_url")
            )

            pat_id = record.get("patient_id", "CV-HIST")
            import re
            safe_id = re.sub(r'[^a-zA-Z0-9_\-]', '_', str(pat_id))
            filename = f"CardioVision_Research_Report_{safe_id}_{eval_id}.pdf"

            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.send_header("Content-Length", str(len(pdf_bytes)))
            self._set_cors()
            self.end_headers()
            self.wfile.write(pdf_bytes)
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._set_cors()
            self.end_headers()
            res = json.dumps({"success": False, "error": f"Historical PDF export error: {str(e)}"})
            self.wfile.write(res.encode("utf-8"))

    def do_POST(self):
        clean_path = self.path.split("?")[0]
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        try:
            params = json.loads(body)
        except Exception:
            params = {}

        # 1. Document Upload Endpoint
        if clean_path == "/api/upload-report":
            try:
                filename = params.get("filename", "report.pdf")
                file_b64 = params.get("file_data", "")
                if not file_b64:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self._set_cors()
                    self.end_headers()
                    res = json.dumps({"success": False, "error": "No file_data payload received."})
                    self.wfile.write(res.encode("utf-8"))
                    return

                # Decode base64 data (handles data URL prefixes if present)
                if "," in file_b64:
                    file_b64 = file_b64.split(",", 1)[1]
                file_bytes = base64.b64decode(file_b64)

                result = process_uploaded_document(file_bytes, filename)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self._set_cors()
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
                return
            except ValueError as ve:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self._set_cors()
                self.end_headers()
                res = json.dumps({"success": False, "error": str(ve)})
                self.wfile.write(res.encode("utf-8"))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self._set_cors()
                self.end_headers()
                res = json.dumps({"success": False, "error": f"Document extraction error: {str(e)}"})
                self.wfile.write(res.encode("utf-8"))
                return

        # 2. History PDF Export via POST
        if clean_path.startswith("/api/history/") and clean_path.endswith("/export-pdf"):
            eval_id = clean_path[len("/api/history/"):-len("/export-pdf")].strip("/")
            self._handle_history_pdf_export(eval_id)
            return

        # 3. History Delete via POST (Fallback)
        if clean_path.startswith("/api/history/") and clean_path.endswith("/delete"):
            eval_id = clean_path[len("/api/history/"):-len("/delete")].strip("/")
            deleted = history_service.delete_evaluation(eval_id)
            self.send_response(200 if deleted else 404)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._set_cors()
            self.end_headers()
            res = json.dumps({"success": deleted})
            self.wfile.write(res.encode("utf-8"))
            return

        # 4. Standard / Live PDF Export
        if clean_path in ["/api/generate-pdf", "/api/export-pdf"]:
            try:
                from pdf_generator import generate_pdf_report
                patient_data = params.get("patient_data") or params
                model_mode = params.get("model_mode") or patient_data.get("model_mode") or "standard"
                
                combined_params = dict(params)
                if isinstance(params.get("patient_data"), dict):
                    combined_params.update(params["patient_data"])
                combined_params["model_mode"] = model_mode

                predictions = params.get("predictions")
                shap_data = params.get("shap_explanations") or (predictions.get("shap_explanations") if isinstance(predictions, dict) else None)

                snapshot = create_patient_feature_snapshot(combined_params, model_mode=model_mode, strict=False)

                if predictions or shap_data:
                    is_ok, reason = verify_snapshot_consistency(snapshot, predictions=predictions, shap_explanations=shap_data)
                    if not is_ok:
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json; charset=utf-8")
                        self._set_cors()
                        self.end_headers()
                        res = json.dumps({
                            "success": False,
                            "error": f"Inconsistent PDF export rejected: {reason} Silent auto-substitution prohibited."
                        })
                        self.wfile.write(res.encode("utf-8"))
                        return

                if not predictions or not shap_data:
                    computed = compute_predictions(combined_params)
                    predictions = computed
                    shap_data = computed.get("shap_explanations", {})

                snapshot_url = params.get("snapshot_data_url") or params.get("snapshot_url")
                
                pdf_bytes = generate_pdf_report(
                    patient_data=snapshot.patient_data,
                    predictions=predictions,
                    shap_explanations=shap_data,
                    model_mode=snapshot.model_mode,
                    snapshot_data_url=snapshot_url
                )

                pat_id = patient_data.get("id") or patient_data.get("patient_id") or "CV-2026-8492"
                import re
                safe_id = re.sub(r'[^a-zA-Z0-9_\-]', '_', str(pat_id))
                filename = f"CardioVision_Research_Report_{safe_id}.pdf"

                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
                self.send_header("Content-Length", str(len(pdf_bytes)))
                self._set_cors()
                self.end_headers()
                self.wfile.write(pdf_bytes)
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self._set_cors()
                self.end_headers()
                res = json.dumps({"success": False, "error": str(e)})
                self.wfile.write(res.encode("utf-8"))
                return

        # 5. Prediction Execution + History Persistence
        result = compute_predictions(params)
        
        # Save to history if explicitly requested or on standard prediction call
        save_to_hist = params.get("save_history", True)
        if save_to_hist and result.get("success"):
            try:
                p_data = params.get("patient_data") if isinstance(params.get("patient_data"), dict) else {}
                p_id = params.get("patient_id") or p_data.get("id") or "CV-2026-8492"
                p_name = params.get("patient_name") or p_data.get("name") or "Alex Morgan (Demo Patient)"
                patient_info = {
                    "id": p_id,
                    "name": p_name,
                    "age": result.get("age", 58),
                    "sex": result.get("sex", "Male"),
                    "length": result.get("length", 170),
                    "weight": result.get("weight", 72)
                }
                hist_rec = history_service.save_evaluation(
                    patient_data=patient_info,
                    predictions=result,
                    shap_explanations=result.get("shap_explanations"),
                    model_mode=result.get("model_mode", "standard")
                )
                result["evaluation_id"] = hist_rec.get("id")
            except Exception as he:
                result["history_error"] = str(he)

        res = json.dumps(result, ensure_ascii=False)
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._set_cors()
        self.end_headers()
        self.wfile.write(res.encode("utf-8"))

    def log_message(self, format, *args):
        # Silent logging
        pass

def run_server():
    port = int(os.environ.get("PORT", 8502))
    server = HTTPServer(("0.0.0.0", port), PredictionAPIHandler)
    print(f"CardioVision API running on port {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    run_server()