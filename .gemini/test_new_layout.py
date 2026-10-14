import os, sys, io
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE_DIR)

from api_server import compute_predictions
from shap_service import get_all_shap_explanations
import fitz

# Let's inspect the current code and test
res = compute_predictions({})
print("Predictions computed:", res['success'])
