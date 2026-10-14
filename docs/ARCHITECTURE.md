# CardioVision AI — System Architecture & Engineering Design

**IIT Mandi Multimodal AI Hackathon 2026 — Track A: Cardiovascular Risk Visualization & Prediction**

---

## 1. High-Level Architectural Overview

CardioVision AI is an explainable multimodal AI research prototype designed to streamline cardiovascular risk assessment. It ingests unstructured clinical reports (PDF, DOCX, raster scans with OCR), maps patient measurements into a validated canonical 57-feature space, performs multi-vessel risk inference (CAD, LAD, LCX, RCA), generates mathematical SHAP explanations, renders an interactive Three.js 106-mesh anatomical heart visualization with telemetry risk overlays, and exports multi-page audit-ready research PDF dossiers.

```
                      ┌──────────────────────────────────────┐
                      │    Unstructured Clinical Reports     │
                      │  (Digital PDF, Scanned PDF, DOCX)    │
                      └──────────────────┬───────────────────┘
                                         │
                                         ▼
                      ┌──────────────────────────────────────┐
                      │      Clinical Extraction Engine      │
                      │   (Unit normalization, page tracking,│
                      │    reference range exclusion)        │
                      └──────────────────┬───────────────────┘
                                         │
                                         ▼
                      ┌──────────────────────────────────────┐
                      │    Human-Reviewed Review Table       │
                      │  (Extracted, Needs Review, Not Found)│
                      └──────────────────┬───────────────────┘
                                         │ Form Autofill / Invalidation
                                         ▼
                      ┌──────────────────────────────────────┐
                      │ Immutable 57-Feature Patient Snapshot│
                      │  (SHA-256 State Guard & Bounds Check)│
                      └──────────────────┬───────────────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         │                               │                               │
         ▼                               ▼                               ▼
┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐
│ Four-Model ML    │           │ SHAP Attribution │           │ Three.js 106-Mesh│
│ Inference Engine │           │ Service          │           │ Anatomical Heart │
│ (CAD, LAD, LCX,  │           │ (Linear & Tree   │           │ (Coronary risk   │
│  RCA)            │           │  Explainers)     │           │  telemetry HUD)  │
└────────┬─────────┘           └────────┬─────────┘           └────────┬─────────┘
         │                               │                             │
         └───────────────────────────────┼─────────────────────────────┘
                                         │
                                         ▼
                      ┌──────────────────────────────────────┐
                      │ Output & Synchronization Layer       │
                      │ - Live Dashboard Telemetry           │
                      │ - SQLite Session History             │
                      │ - Multi-Page Research PDF Export     │
                      └──────────────────────────────────────┘
```

---

## 2. Multimodal Clinical Extraction Engine (`backend/clinical_extractor.py`)

1. **Digital Document Parsing**: Uses PyMuPDF (`pymupdf`) for high-fidelity token and layout extraction, and `python-docx` for structured Word document analysis.
2. **Context-Aware Disambiguation**: 
   - Excludes reference intervals (e.g., `(Ref: 70-99 mg/dL)`) and test codes before extracting measured patient biomarker values.
   - Disregards document pagination and dates to eliminate false age conflicts.
3. **Unit Normalization**: Automatically converts diverse units into canonical representations:
   - Stature: ft/in, in, m → cm
   - Weight: lbs → kg
   - Glucose: mmol/L → mg/dL ($\times 18.0182$)
   - Creatinine: $\mu\text{mol/L} \rightarrow \text{mg/dL}$ ($\div 88.4$)
   - Cholesterol: mmol/L → mg/dL ($\times 38.67$)
   - Triglycerides: mmol/L → mg/dL ($\times 88.57$)
4. **Scanned PDF Fallback**: Detects raster image pages and invokes Tesseract OCR (`pytesseract`) if installed. If Tesseract is unavailable, raises a descriptive advisory without crashing.

---

## 3. Canonical 57-Feature Snapshot (`backend/patient_feature_snapshot.py`)

To eliminate silent bugs, data leakage, and stale caching:
1. **Single Immutable Snapshot**: All models, SHAP explanations, 3D telemetry overlays, and PDF generators consume an identical feature matrix $X \in \mathbb{R}^{1 \times 57}$ whose schema exactly mirrors `feature_columns.pkl`.
2. **Deterministic Cryptographic Hashing**: Each unique feature vector computes a deterministic SHA-256 fingerprint:
   $$\text{Hash} = \text{SHA-256}\left(\prod_{i=1}^{57} \text{col}_i \parallel \text{val}_i \parallel \text{mode}\right)_{:16}$$
3. **Strict Validation & No Silent Substitution**: Implausible values (e.g., height > 250 cm or < 50 cm) are preserved verbatim and tagged with clinical alerts rather than being silently mutated or clipped.

---

## 4. Multi-Vessel Cardiovascular Prediction Models (`models/`)

Four independent scikit-learn models predict patient risk:
- **CAD Model** (`cad_model.pkl`): Logistic Regression baseline evaluating overall coronary artery disease risk.
- **LAD Model** (`lad_model.pkl`): Random Forest classifier targeting the Left Anterior Descending artery.
- **LCX Model** (`lcx_model.pkl` / `lcx_model_candidate.pkl`):
  - Standard Mode: Baseline Random Forest model ($0.50$ threshold).
  - Experimental Mode: Candidate Random Forest model ($0.45$ threshold).
- **RCA Model** (`rca_model.pkl` / `rca_model_candidate.pkl`):
  - Standard Mode: Baseline Logistic Regression model ($0.50$ threshold).
  - Experimental Mode: Candidate Logistic Regression model ($0.40$ threshold).

---

## 5. Explainable AI Pipeline (`backend/shap_service.py`)

Explainability is tailored to model mathematics:
- **Linear Models (CAD & RCA)**: Analyzed with `shap.LinearExplainer`. Explanations operate on the log-odds margin scale ($f(x) \in \mathbb{R}$). Model probability is mathematically equivalent to:
  $$P(\text{Risk}) = \sigma(f(x)) = \frac{1}{1 + e^{-f(x)}}$$
- **Tree Ensemble Models (LAD & LCX)**: Analyzed with `shap.TreeExplainer`. Explanations operate directly on the probability scale ($f(x) \in [0, 1]$).
- **Waterfall Decomposition**: Evaluates top contributing risk features alongside a mathematically sound `Remaining Features` balance term that guarantees strict additivity.

---

## 6. Interactive Three.js 106-Mesh Anatomical Visualization (`frontend/components/heart_viewer.html`)

1. **Anatomical Accuracy**: Renders 106 curated OBJ meshes derived from BodyParts3D (FMA anatomical ontology).
2. **Dynamic Vessel Telemetry**: Parent window dispatches `UPDATE_CARDIO_DATA` messages updating the 3D HUD chips and coloring coronary branches (LAD, LCX, RCA, Left Coronary Stem) by risk tier (Low: Green, Borderline: Yellow, High: Red).
3. **Optimized Render Loop**: Operates on a demand-driven rendering strategy (`requestRender()`), capping device pixel ratio at 1.5 and halting animations when tab or viewer is hidden.
4. **Snapshot Capture**: Enables high-resolution WebGL canvas capture (`canvas.toDataURL("image/png")`) for seamless embedding in exported PDF dossiers.

---

## 7. Audit-Ready Research PDF Generation (`backend/pdf_generator.py`)

Multi-page ReportLab-generated research dossiers featuring:
- Header banner and document metadata.
- Patient profile and complete 54-field measurement table.
- Multi-vessel risk summary table with classification thresholds.
- Four patient-specific SHAP waterfall charts with baseline log-odds / probability explanations.
- High-resolution embedded 3D anatomical heart capture with coronary vessel telemetry.
- Dynamic pagination with running headers, footers (`Page X of Y`), and comprehensive medical research disclaimers.
