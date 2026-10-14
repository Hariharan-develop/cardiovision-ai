import os, sys, traceback
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE_DIR)

from api_server import compute_predictions
from pdf_generator import generate_pdf_report
import fitz

try:
    res2 = compute_predictions({'model_mode': 'candidate'})
    print('res2 success:', res2['success'])
    print('res2 lcx_risk:', res2['lcx_risk'], 'rca_risk:', res2['rca_risk'])
    print('res2 lcx_threshold:', res2['lcx_threshold'], 'rca_threshold:', res2['rca_threshold'])
    print('res2 lcx_label:', res2['lcx_label'], 'rca_label:', res2['rca_label'])
    print('res2 lcx_model_file:', res2['lcx_model_file'], 'rca_model_file:', res2['rca_model_file'])

    pdf2 = generate_pdf_report(
        patient_data={'id': 'CV-2026-8492', 'displayName': 'Alex Morgan (Demo Patient)', 'age': 58, 'sex': 'Male'},
        predictions=res2,
        shap_explanations=res2.get('shap_explanations', {}),
        model_mode='candidate',
        output_filename='test_verify_exp.pdf'
    )
    doc2 = fitz.open('test_verify_exp.pdf')
    text2 = ''.join(doc2[i].get_text() for i in range(len(doc2)))
    print('Checking strings in text2:')
    for s in ['Experimental Candidate Mode', 'lcx_model_candidate.pkl', 'rca_model_candidate.pkl', '0.689 (Macro F1)', '0.651 (Macro F1)']:
        print(f'  Contains "{s}": {s in text2}')
except Exception as e:
    traceback.print_exc()
