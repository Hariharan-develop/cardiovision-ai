import os, sys
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORKSPACE_DIR)

from api_server import compute_predictions
from pdf_generator import generate_pdf_report
import fitz

# Let's inspect the layout and page breaks
res = compute_predictions({})
print("Testing layout...")
