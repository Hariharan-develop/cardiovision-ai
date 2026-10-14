# CardioVision AI — Model Evaluation & Performance Analysis

**IIT Mandi Multimodal AI Hackathon 2026 — Track A: Cardiovascular Risk Visualization & Prediction**

---

## 1. Dataset & Validation Methodology

All machine learning models were developed and retrospectively evaluated on the **Z-Alizadeh Sani Cardiovascular Dataset** (303 consecutive patients undergoing catheter-based coronary angiography at Tehran Heart Center).

- **Patient Count**: 303 cases.
- **Validation Scheme**: Retrospective stratified cross-validation.
- **Canonical Feature Space**: 57 one-hot encoded variables (`feature_columns.pkl`) encompassing demographic, clinical history, symptom presentation, physical exam, resting ECG, echocardiography, and laboratory biomarker panels.

---

## 2. Retrospective Baseline Model Discrimination

The baseline models provide multi-vessel risk estimation across the overall coronary vasculature and the three primary epicardial coronary arteries:

| Target Model | Algorithm | Primary Target Endpoint | Retrospective Baseline ROC-AUC | Decision Threshold |
| :--- | :--- | :--- | :---: | :---: |
| **CAD Model** | Logistic Regression | Overall CAD (≥ 50% stenosis in ≥ 1 vessel) | **0.917** | 0.50 |
| **LAD Model** | Random Forest | Left Anterior Descending Artery Stenosis | **0.756** | 0.50 |
| **LCX Model** | Random Forest | Left Circumflex Artery Stenosis | **0.584** | 0.50 |
| **RCA Model** | Logistic Regression | Right Coronary Artery Stenosis | **0.652** | 0.50 |

---

## 3. Critical Analytical Observations on Model Performance

1. **Strong Overall CAD Discrimination**:
   - The CAD model demonstrates excellent discriminatory power ($\text{ROC-AUC} = 0.917$), accurately stratifying patients with angiographically confirmed CAD from normal controls.
2. **Moderate LAD Discrimination**:
   - The LAD model achieves respectable discrimination ($\text{ROC-AUC} = 0.756$), reflecting the strong correlation of anterior ECG changes, regional wall motion abnormalities (RWMA), and typical exertional angina with anterior wall ischemia.
3. **Limited Discrimination for LCX and RCA**:
   - **LCX Baseline ($\text{ROC-AUC} = 0.584$)**: Lateral ischemia often presents with non-specific symptoms and subtle ECG abnormalities that are poorly captured on standard 12-lead surface ECGs, resulting in limited discriminatory performance for the baseline Random Forest model.
   - **RCA Baseline ($\text{ROC-AUC} = 0.652$)**: Inferior wall involvement and variable right coronary anatomy introduce significant variance in non-invasive biomarker correlation.

> [!WARNING]
> **Research Reality & Technical Transparency**:
> The limited discriminatory capacity of the LCX and RCA baseline models is transparently acknowledged. In academic and clinical AI research, stating actual empirical performance without inflation or synthetic overfitting is essential for scientific integrity.

---

## 4. Standard Mode vs. Experimental Candidate Mode

To investigate sensitivity-oriented decision support for subtle branch lesions, CardioVision AI provides two user-selectable operational modes:

### Standard Mode
- **Configuration**: Baseline models across all four vessels (`cad_model.pkl`, `lad_model.pkl`, `lcx_model.pkl`, `rca_model.pkl`).
- **Decision Thresholds**:
  - CAD: $0.50$ (50.0%)
  - LAD: $0.50$ (50.0%)
  - LCX: $0.50$ (50.0%)
  - RCA: $0.50$ (50.0%)

### Experimental Mode (Candidate Models)
- **Configuration**: Evaluates candidate models (`lcx_model_candidate.pkl`, `rca_model_candidate.pkl`) alongside baseline CAD and LAD models.
- **Operating Thresholds**:
  - CAD: $0.50$ (50.0%)
  - LAD: $0.50$ (50.0%)
  - **LCX Candidate**: $0.45$ (45.0%)
  - **RCA Candidate**: $0.40$ (40.0%)

> [!IMPORTANT]
> **Statistical Distinction Between Threshold Adjustment and Probability Calibration**:
> Lowering classification decision thresholds (e.g., from $0.50$ to $0.45$ or $0.40$) increases detection sensitivity for potential lesions at the cost of specificity. Adjusting decision thresholds does **not** constitute probability calibration (such as Platt scaling or isotonic regression). Predicted probabilities remain continuous outputs of the underlying models; the threshold governs solely the binary alert assignment.

---

## 5. Explainability Architecture & Scaling Alignment

Because model architectures vary, SHAP feature attributions are computed on mathematically appropriate scales:

1. **CAD Model (Logistic Regression)**:
   - Uses `shap.LinearExplainer`.
   - Explanations operate on the **log-odds** margin:
     $$f(x) = \beta_0 + \sum_{i=1}^{57} \beta_i x_i$$
   - The predicted probability is obtained via the logistic sigmoid transform:
     $$P(\text{CAD}) = \sigma(f(x)) = \frac{1}{1 + e^{-f(x)}}$$
   - SHAP waterfall plots display feature contributions in log-odds units alongside the baseline expected value $\mathbb{E}[f(x)]$.
2. **LAD Model (Random Forest)**:
   - Uses `shap.TreeExplainer`.
   - Explanations operate directly on the **probability scale** ($[0, 1]$), decomposing the ensemble tree margin directly into probability increments.
3. **LCX Models (Standard & Candidate Random Forests)**:
   - Evaluated on the **probability scale** via `shap.TreeExplainer`.
4. **RCA Models (Standard & Candidate Logistic Regressions)**:
   - Evaluated on the **log-odds scale** via `shap.LinearExplainer`, mapped to probability via sigmoid.

---

## 6. Clinical & Regulatory Disclaimer

- **No Medical Device Certification**: CardioVision AI is a research software prototype developed for the IIT Mandi Multimodal AI Hackathon 2026. It has not received clearance or approval from the U.S. FDA, European CE, CDSCO, or any medical regulatory agency.
- **No External Clinical Validation**: The system has been validated solely on retrospective public research data and synthetic benchmark fixtures. It has not undergone prospective clinical trials.
- **Intended Use**: This tool is strictly intended for scientific exploration, multimodal AI benchmarking, and educational evaluation. It must never be used as a standalone diagnostic system or to direct clinical patient management.
