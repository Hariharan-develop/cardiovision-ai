# CardioVision AI — 3 to 5 Minute Demo Video Script

**Target Duration:** 4 minutes 30 seconds (Range: 3:30 – 5:00)  
**Presenter:** Project Lead / ML Clinician Engineer  
**Key Goal:** Demonstrate end-to-end multi-vessel cardiovascular risk prediction, mathematical SHAP explainability, 106-mesh 3D cardiac anatomical mapping, and synchronized clinical PDF generation.

---

## Video Outline & Timecodes

| Timecode | Segment Title | Visual On-Screen | Speaker Narrative & Technical Focus |
|:---:|---|---|---|
| **0:00 – 0:45** | **1. The Problem & Clinical Motivation** | Title card; statistics on CAD mortality; split screen of coronary angiogram vs non-invasive inputs | Non-invasive risk stratification of multi-vessel CAD; limitations of single-score predictors; need for vessel-specific explainability. |
| **0:45 – 1:30** | **2. Standardized 57-Feature Clinical Vector** | Active dashboard (`view-predict`); entering Alex Morgan profile (58y, 170cm, 72kg, BMI 24.9); biomarker inputs | Tracing 34 physiological biomarkers and 23 binary clinical indicators into an immutable `PatientFeatureSnapshot` with SHA-256 integrity. |
| **1:30 – 2:30** | **3. Multi-Model Inference & Mathematical SHAP** | Predictive risk cards updating; expanding SHAP explainability panels with waterfall charts | Four distinct models (CAD, LAD, LCX, RCA); strict separation of Tree probability ($\Delta\text{prob}$) vs Linear log-odds ($\Delta\text{log-odds}$) scales; additivity check. |
| **2:30 – 3:30** | **4. Interactive Three.js 106-Mesh 3D Cardiac Mapping** | 3D heart view; camera rotation; zooming into LAD trunk and LCX circumflex; live telemetry badge | Anatomical BodyParts3D 106-mesh geometry; mapping AI predictive probabilities directly onto arterial meshes with color-coded risk highlights. |
| **3:30 – 4:15** | **5. Publication-Grade PDF Report Export** | Clicking "Export Clinical PDF"; opening generated 3-page PDF; zooming into Page 3 3D visualization | Instant generation of 3-page A4 report; enlarged 3D heart viewport; high-contrast coronary telemetry; zero silent data mutation. |
| **4:15 – 4:45** | **6. Standard vs. Experimental Mode & Validation** | Toggling to Experimental Mode; highlighting LCX 0.45 and RCA 0.40 candidate thresholds; terminal test evidence | Rigorous validation: held-out test cohort benchmarks vs exploratory nested CV metrics; automated test suites running with 100% PASS. |
| **4:45 – 5:00** | **7. Summary & Ethical Research Disclaimer** | Platform summary slide; ethical research prototype notice and clear disclaimer | Recap of achievements; clear statement that platform is an exploratory research prototype, not a cleared medical device. |

---

## Detailed Teleprompter Script

### [0:00 – 0:45] 1. The Problem & Clinical Motivation
**[Visual: Title Card -> CardioVision AI Logo -> High-level problem slide]**

> *"Coronary artery disease remains the leading cause of mortality worldwide. Yet, traditional screening tools often condense patient risk into a single monolithic score, obscuring critical anatomical details about which specific coronary arteries are at risk of stenosis.*
>
> *Clinicians are left asking: Is the Left Anterior Descending artery obstructed? Is the Left Circumflex or Right Coronary Artery compromised? And more importantly, which specific biomarkers are driving the algorithm’s conclusion?*
>
> *Welcome to **CardioVision AI**—an explainable, multi-vessel cardiovascular risk intelligence platform designed to bridge machine learning, anatomical visualization, and publication-grade clinical reporting."*

---

### [0:45 – 1:30] 2. Standardized 57-Feature Clinical Vector
**[Visual: Screen recording of the dashboard at `http://127.0.0.1:8502` / `cardiovision_exact_dashboard.html`]**

> *"Here in our clinical dashboard, we evaluate patient Alex Morgan—a 58-year-old male presenting with typical chest pain, resting BP of 130 over 70, and physiological stature of 170 centimeters and 72 kilograms.*
>
> *Notice our physiological validation engine immediately calculates a normal baseline BMI of 24.9 kg/m².*
>
> *Unlike conventional prototypes that silently clip, drop, or guess values, CardioVision AI establishes an **immutable 57-dimensional Patient Feature Snapshot**. This vector encompasses 34 physiological laboratory biomarkers—including fasting blood sugar, creatinine, lipid fractions, cardiac enzymes, and electrolytes—along with 23 binary clinical indicators.*
>
> *A cryptographic SHA-256 fingerprint guarantees that the exact same verified clinical state is shared across our predictive models, SHAP explainers, 3D telemetry, and PDF generator."*

---

### [1:30 – 2:30] 3. Multi-Model Inference & Mathematical SHAP
**[Visual: Clicking "Run Risk Assessment". Cards animate to show CAD 91.7%, LAD 79.0%, LCX 65.0%, RCA 51.7%. Scrolling to SHAP sections]**

> *"With a single click, CardioVision AI evaluates four distinct, vessel-specific machine learning models:*
> - *Overall CAD Risk: **91.7%***
> - *LAD Stenosis Risk: **79.0%***
> - *LCX Stenosis Risk: **65.0%***
> - *RCA Stenosis Risk: **51.7%***
>
> *Crucially, CardioVision AI adheres to strict mathematical integrity in its explainability layer.*
>
> *For our tree-based LAD and LCX models, Tree SHAP operates in the **additive probability scale**, quantifying exact percentage point shifts from the baseline expectation.*
>
> *For our CAD and RCA models, Linear SHAP operates in the **log-odds scale**, verifying exact mathematical additivity—$E[f(x)] + \sum \phi_i = f(x)$—before transforming via the logistic sigmoid into final probability.*
>
> *Every feature contribution is visually broken down into both horizontal impact rankings and cumulative waterfall charts."*

---

### [2:30 – 3:30] 4. Interactive Three.js 106-Mesh 3D Cardiac Mapping
**[Visual: Switching to the 3D Coronary Visualization tab. Orbiting the heart, inspecting highlighted arteries]**

> *"Numbers on a screen only tell part of the story. CardioVision AI maps predictive telemetry directly onto an interactive **106-mesh Three.js 3D cardiac model** derived from the BodyParts3D anatomical assembly.*
>
> *Here, clinicians can rotate, pan, and zoom into specific coronary trunks.*
> - *The **LAD arterial trunk** glows in high-risk blue at 79.0%.*
> - *The **LCX circumflex trunk** highlights in emerald green at 65.0%.*
> - *The **RCA trunk** is mapped in warning amber at 51.7%.*
> - *The **Left Main stem** and **ventricular myocardium** provide full spatial anatomical context.*
>
> *This provides an intuitive anatomical bridge between statistical risk and spatial coronary anatomy."*

---

### [3:30 – 4:15] 5. Publication-Grade PDF Report Export
**[Visual: Clicking "Export Clinical PDF". Opening the freshly generated `Final_Sync_Standard_Report.pdf`]**

> *"When it's time to document findings or consult with a multidisciplinary team, CardioVision AI generates a publication-grade, 3-page medical research evaluation report.*
>
> *On Page 1: Session demographics, validated stature and BMI, four prediction cards, and complete 12-row biomarker reference tables.*
>
> *On Page 2: Mathematical SHAP explainability tables and charts for CAD and LAD.*
>
> *On Page 3: Our newly enlarged **3D Coronary Heart Visualization card**—featuring an enlarged, high-resolution cardiac snapshot alongside high-contrast, easily readable coronary telemetry and vascular color legends.*
>
> *Our pre-flight consistency checks strictly reject mismatched or stale payloads with explicit error codes, completely prohibiting silent data substitution."*

---

### [4:15 – 4:45] 6. Standard vs. Experimental Mode & Validation
**[Visual: Dashboard toggled to "Experimental Candidate Mode". Terminal showing `python verify_all_12_tests.py` passing 12/12]**

> *"To support ongoing translational research, CardioVision AI offers a clean separation between **Standard Production Mode** and **Experimental Candidate Mode**.*
>
> *In Experimental Mode, candidate models utilize tuned decision thresholds derived from exploratory nested cross-validation: **LCX at 0.45** and **RCA at 0.40**.*
>
> *Our rigorous verification suite includes 12 automated regression tests and a full 57-feature end-to-end trace, achieving a **100% PASS rate** with zero regression."*

---

### [4:45 – 5:00] 7. Summary & Ethical Research Disclaimer
**[Visual: Closing title slide with GitHub repository link, license badge, and regulatory disclaimer]**

> *"CardioVision AI brings transparency, mathematical rigor, and 3D spatial intelligence to cardiovascular AI research.*
>
> *As a reminder, CardioVision AI is an exploratory research prototype and educational demonstration. It is not an FDA-cleared medical device and should never replace formal clinical judgment.*
>
> *Thank you for watching, and explore our full open-source codebase on GitHub!"*
