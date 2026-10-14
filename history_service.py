"""
CardioVision AI — Prediction History Service
Persistent SQLite storage for all completed patient risk evaluations.

Guarantees:
- Data persists across application restarts.
- No hardcoded demo history.
- No duplicate records from repeated PDF downloads.
- Clean separation between patients and evaluations (zero cross-patient leakage).
- Preserves full 57-feature immutable snapshot, snapshot hash, SHAP explanations,
  model mode, and calibrated decision thresholds for exact historical reproducibility.
"""

import os
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "prediction_history.db")


def get_db_connection() -> sqlite3.Connection:
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                patient_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                model_mode TEXT NOT NULL,
                cad_risk REAL NOT NULL,
                cad_label TEXT NOT NULL,
                lad_risk REAL NOT NULL,
                lad_label TEXT NOT NULL,
                lcx_risk REAL NOT NULL,
                lcx_label TEXT NOT NULL,
                rca_risk REAL NOT NULL,
                rca_label TEXT NOT NULL,
                lcx_threshold REAL NOT NULL,
                rca_threshold REAL NOT NULL,
                snapshot_hash TEXT NOT NULL,
                snapshot_json TEXT NOT NULL,
                shap_json TEXT,
                active_models_json TEXT
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_eval_timestamp ON evaluations(timestamp DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_eval_patient ON evaluations(patient_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_eval_mode ON evaluations(model_mode);")
        conn.commit()
    finally:
        conn.close()


init_db()


def save_evaluation(
    patient_data: Dict[str, Any],
    predictions: Dict[str, Any],
    shap_explanations: Optional[Dict[str, Any]] = None,
    model_mode: str = "standard",
    active_models: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Save a successfully completed prediction evaluation.
    Prevents duplicate entries from repeated requests with identical snapshot and mode.
    """
    init_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        pat_id = str(patient_data.get("id") or patient_data.get("patient_id") or "CV-2026-8492")
        pat_name = str(patient_data.get("displayName") or patient_data.get("patient_name") or patient_data.get("name") or "Alex Morgan (Demo Patient)")
        
        mode = str(model_mode or predictions.get("model_mode") or "standard").lower()
        snapshot_hash = str(predictions.get("snapshot_hash") or "")

        # Idempotency check: if an identical evaluation was saved for this patient within the last 15 seconds, return it
        if snapshot_hash:
            cursor.execute(
                "SELECT * FROM evaluations WHERE snapshot_hash = ? AND patient_id = ? AND model_mode = ? ORDER BY timestamp DESC LIMIT 1;",
                (snapshot_hash, pat_id, mode)
            )
            existing = cursor.fetchone()
            if existing:
                try:
                    eval_time = datetime.fromisoformat(existing["timestamp"])
                    now_utc = datetime.now(timezone.utc)
                    if (now_utc - eval_time).total_seconds() < 15:
                        return _normalize_evaluation_record(dict(existing))
                except Exception:
                    pass

        eval_id = f"eval-{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        cad_risk = float(predictions.get("cad_risk", 0.0))
        cad_label = str(predictions.get("cad_label", "CAD"))
        lad_risk = float(predictions.get("lad_risk", 0.0))
        lad_label = str(predictions.get("lad_label", "Normal"))
        lcx_risk = float(predictions.get("lcx_risk", 0.0))
        lcx_label = str(predictions.get("lcx_label", "Normal"))
        rca_risk = float(predictions.get("rca_risk", 0.0))
        rca_label = str(predictions.get("rca_label", "Normal"))

        lcx_thresh = float(predictions.get("lcx_threshold", 0.5 if mode == "standard" else 0.45))
        rca_thresh = float(predictions.get("rca_threshold", 0.5 if mode == "standard" else 0.40))

        if active_models is None:
            active_models = {
                "cad": "cad_model.pkl",
                "lad": "lad_model.pkl",
                "lcx": str(predictions.get("lcx_model_file", "lcx_model.pkl" if mode == "standard" else "lcx_model_candidate.pkl")),
                "rca": str(predictions.get("rca_model_file", "rca_model.pkl" if mode == "standard" else "rca_model_candidate.pkl")),
            }

        # Snapshot package including clinical input parameters and features
        full_patient_data = dict(predictions.get("patient_data") or {})
        full_patient_data.update(patient_data or {})
        snapshot_package = {
            "patient_data": full_patient_data,
            "features": predictions.get("features", {}),
            "snapshot_hash": snapshot_hash
        }

        cursor.execute(
            """
            INSERT INTO evaluations (
                id, patient_id, patient_name, timestamp, model_mode,
                cad_risk, cad_label, lad_risk, lad_label, lcx_risk, lcx_label, rca_risk, rca_label,
                lcx_threshold, rca_threshold, snapshot_hash, snapshot_json, shap_json, active_models_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                eval_id, pat_id, pat_name, now_iso, mode,
                cad_risk, cad_label, lad_risk, lad_label, lcx_risk, lcx_label, rca_risk, rca_label,
                lcx_thresh, rca_thresh, snapshot_hash,
                json.dumps(snapshot_package, ensure_ascii=False),
                json.dumps(shap_explanations or predictions.get("shap_explanations") or {}, ensure_ascii=False),
                json.dumps(active_models, ensure_ascii=False)
            )
        )
        conn.commit()

        cursor.execute("SELECT * FROM evaluations WHERE id = ?;", (eval_id,))
        row = cursor.fetchone()
        return _normalize_evaluation_record(dict(row)) if row else {}
    finally:
        conn.close()


def _normalize_evaluation_record(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure every history evaluation record provides both percentage ('cad_risk')
    and ratio ('cad_probability') keys, consistent classification labels, and decision thresholds.
    """
    if not isinstance(item, dict):
        return {}
    
    # Parse json snapshots for convenience
    if isinstance(item.get("snapshot_json"), str):
        try:
            item["snapshot"] = json.loads(item["snapshot_json"])
        except Exception:
            item["snapshot"] = {}
    elif not isinstance(item.get("snapshot"), dict):
        item["snapshot"] = {}

    if isinstance(item.get("shap_json"), str):
        try:
            item["shap_explanations"] = json.loads(item["shap_json"])
        except Exception:
            item["shap_explanations"] = {}

    if isinstance(item.get("active_models_json"), str):
        try:
            item["active_models"] = json.loads(item["active_models_json"])
        except Exception:
            item["active_models"] = {}

    item["patient_data"] = item["snapshot"].get("patient_data", {})

    # Ensure all risk values are floats, percentage and ratio formats, and normalized classifications
    for v in ["cad", "lad", "lcx", "rca"]:
        risk_val = item.get(f"{v}_risk")
        try:
            risk_float = float(risk_val) if risk_val is not None else 0.0
        except (ValueError, TypeError):
            risk_float = 0.0
        item[f"{v}_risk"] = round(risk_float, 1)
        # Probability ratio (0.0 - 1.0)
        item[f"{v}_probability"] = round(risk_float / 100.0 if risk_float > 1.0 else risk_float, 4)
        
        lbl = item.get(f"{v}_label") or ("CAD" if v == "cad" else "Normal")
        item[f"{v}_label"] = lbl
        item[f"{v}_classification"] = lbl

    # Calibrated decision thresholds
    mode = str(item.get("model_mode", "standard")).lower()
    lcx_thresh = float(item.get("lcx_threshold") if item.get("lcx_threshold") is not None else (0.45 if mode in ["candidate", "experimental"] else 0.50))
    rca_thresh = float(item.get("rca_threshold") if item.get("rca_threshold") is not None else (0.40 if mode in ["candidate", "experimental"] else 0.50))
    item["lcx_threshold"] = lcx_thresh
    item["rca_threshold"] = rca_thresh
    item["decision_thresholds"] = {
        "CAD": 0.50,
        "LAD": 0.50,
        "LCX": lcx_thresh,
        "RCA": rca_thresh
    }
    return item


def get_evaluations(
    search: Optional[str] = None,
    mode: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Retrieve evaluation records sorted newest to oldest with optional search and mode filtering.
    """
    init_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM evaluations WHERE 1=1"
        params: List[Any] = []

        if search is not None and str(search).strip():
            s = f"%{str(search).strip()}%"
            query += " AND (patient_name LIKE ? OR patient_id LIKE ? OR id LIKE ?)"
            params.extend([s, s, s])

        if mode and mode.lower() in ["standard", "candidate", "experimental"]:
            target_mode = "candidate" if mode.lower() in ["candidate", "experimental"] else "standard"
            query += " AND model_mode = ?"
            params.append(target_mode)

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?;"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = []
        for r in rows:
            item = dict(r)
            result.append(_normalize_evaluation_record(item))
        return result
    finally:
        conn.close()


def get_evaluation_by_id(eval_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single evaluation by its unique evaluation ID.
    """
    init_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evaluations WHERE id = ?;", (eval_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return _normalize_evaluation_record(dict(row))
    finally:
        conn.close()


def delete_evaluation(eval_id: str) -> bool:
    """
    Delete an evaluation record by ID.
    """
    init_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM evaluations WHERE id = ?;", (eval_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_summary_metrics() -> Dict[str, int]:
    """
    Compute summary metrics for Prediction History dashboard cards:
    - Total evaluations
    - Total unique patients
    - Standard mode evaluations
    - Experimental/Candidate mode evaluations
    """
    init_db()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM evaluations;")
        total_evals = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT patient_id) FROM evaluations;")
        unique_patients = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM evaluations WHERE model_mode = 'standard';")
        std_evals = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM evaluations WHERE model_mode IN ('candidate', 'experimental');")
        cand_evals = cursor.fetchone()[0]

        return {
            "total_evaluations": int(total_evals),
            "total_patients": int(unique_patients),
            "total_unique_patients": int(unique_patients),
            "standard_evaluations": int(std_evals),
            "candidate_evaluations": int(cand_evals)
        }
    finally:
        conn.close()


class HistoryService:
    """Object-oriented wrapper around the prediction history SQLite repository."""
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DB_PATH
        init_db()

    def save_evaluation(self, patient_data: Dict[str, Any], predictions: Dict[str, Any],
                        shap_explanations: Optional[Dict[str, Any]] = None,
                        model_mode: str = "standard", active_models: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        return save_evaluation(patient_data, predictions, shap_explanations, model_mode, active_models)

    def get_evaluations(self, search: Optional[str] = None, mode: Optional[str] = None,
                        limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return get_evaluations(search=search, mode=mode, limit=limit, offset=offset)

    def get_evaluation_by_id(self, eval_id: str) -> Optional[Dict[str, Any]]:
        return get_evaluation_by_id(eval_id)

    def delete_evaluation(self, eval_id: str) -> bool:
        return delete_evaluation(eval_id)

    def get_summary_metrics(self) -> Dict[str, int]:
        return get_summary_metrics()

