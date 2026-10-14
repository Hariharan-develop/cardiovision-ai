# CardioVision AI — Dataset Documentation & Attribution

## 1. Z-Alizadeh Sani Cardiovascular Dataset

The models within CardioVision AI were trained on the **Z-Alizadeh Sani Dataset**, a canonical benchmark dataset for coronary artery disease (CAD) diagnosis.

- **Primary Citation**: 
  > Alizadehsani, R., Hosseini, M. J., Sani, Z. A., Ghandeharioun, A., & Boghrati, R. (2013). *Computer-aided diagnosis of coronary artery disease using machine learning techniques*. Scientific Reports, 3(1), 1-9.
- **Repository**: [UCI Machine Learning Repository: Z-Alizadeh Sani Dataset](https://archive.ics.uci.edu/dataset/412/z+alizadeh+sani)
- **License / Terms of Use**: Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Patient Cohort**: 303 consecutive patients presenting at Tehran Heart Center undergoing coronary angiography.
- **Features**: 54 clinical, demographic, symptom, physical examination, electrocardiographic (ECG), echocardiographic, and laboratory variables, mapped into the 57 canonical one-hot encoded input columns (`feature_columns.pkl`).
- **Target Vessels**:
  - `CAD`: Overall coronary artery disease (stenosis ≥ 50% in at least one major coronary artery).
  - `LAD`: Left anterior descending artery stenosis.
  - `LCX`: Left circumflex artery stenosis.
  - `RCA`: Right coronary artery stenosis.

---

## 2. Local Database & Patient Privacy

The local SQLite database (`data/prediction_history.db` and journal files `*.db-journal`, `*.db-wal`) is used exclusively for local session history during development and testing.

- **Exclusion from Version Control**: `data/*.db` and `*.db-journal` are excluded via `.gitignore` to guarantee that no local evaluation snapshots or clinical test history are committed to public source control.
- **Data Protection**: Only fictional synthetic patient profiles (e.g., Alex Morgan, Eleanor Vance, Aarav Kumar) are used in synthetic fixtures (`tests/fixtures/`).
- **Database Initialization**: The application automatically creates and initializes `data/prediction_history.db` on first run if it does not already exist.
