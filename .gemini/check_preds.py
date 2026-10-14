import joblib
import pandas as pd
import numpy as np
import os

from api_server import compute_predictions

# Check compute_predictions with empty dict
p_empty = compute_predictions({})
print("Empty dict predictions:")
print(f"CAD: {p_empty['cad_risk']}%, LAD: {p_empty['lad_risk']}%, LCX: {p_empty['lcx_risk']}%, RCA: {p_empty['rca_risk']}%")

# Let's inspect app.py prediction calculation
# Let's see what app.py does!
