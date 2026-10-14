import urllib.request
import json

req_data = {
    'Age': 62,
    'Weight': 80,
    'Length': 175,
    'Sex': 'Male',
    'Current Smoker': 'Yes',
    'model_mode': 'standard'
}

req = urllib.request.Request(
    'http://127.0.0.1:8502/api/predict',
    data=json.dumps(req_data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode('utf-8'))
    print("=== STANDARD MODE ===")
    print("CAD:", res.get('cad_risk'), res.get('cad_label'))
    print("LAD:", res.get('lad_risk'), res.get('lad_label'))
    print("LCX:", res.get('lcx_risk'), res.get('lcx_label'))
    print("RCA:", res.get('rca_risk'), res.get('rca_label'))
    print("SHAP keys:", list(res.get('shap_explanations', {}).keys()))
    for k, v in res.get('shap_explanations', {}).items():
        print(f"  {k.upper()}: model={v.get('model_file')}, scale={v.get('scale')}, explainer={v.get('explainer_type')}")
        if v.get('top_features'):
            top1 = v['top_features'][0]
            print(f"    Top 1: {top1['display_name']} ({top1['patient_value']}) -> {top1['display_shap']} [{top1['direction']}]")

req_data['model_mode'] = 'candidate'
req2 = urllib.request.Request(
    'http://127.0.0.1:8502/api/predict',
    data=json.dumps(req_data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req2) as resp2:
    res2 = json.loads(resp2.read().decode('utf-8'))
    print("\n=== EXPERIMENTAL / CANDIDATE MODE ===")
    print("CAD:", res2.get('cad_risk'), res2.get('cad_label'))
    print("LAD:", res2.get('lad_risk'), res2.get('lad_label'))
    print("LCX:", res2.get('lcx_risk'), res2.get('lcx_label'))
    print("RCA:", res2.get('rca_risk'), res2.get('rca_label'))
    for k, v in res2.get('shap_explanations', {}).items():
        print(f"  {k.upper()}: model={v.get('model_file')}, scale={v.get('scale')}, explainer={v.get('explainer_type')}")
        if v.get('top_features'):
            top1 = v['top_features'][0]
            print(f"    Top 1: {top1['display_name']} ({top1['patient_value']}) -> {top1['display_shap']} [{top1['direction']}]")
