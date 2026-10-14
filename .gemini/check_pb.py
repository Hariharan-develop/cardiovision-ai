import os
import sys
import io
import fitz

sys.path.insert(0, r"c:\Users\hario\Downloads\CardioVision-AI")

# Let's see what happens if we replace PageBreak with dynamic flow
with open(r"c:\Users\hario\Downloads\CardioVision-AI\pdf_generator.py", "r", encoding="utf-8") as f:
    code = f.read()

# Check where PageBreak() occurs
print("Occurrences of PageBreak():", code.count("PageBreak()"))
