import pymupdf
import os

doc = pymupdf.open(".gemini/test_dynamic.pdf")
artifact_dir = r"C:\Users\hario\.gemini\antigravity-ide\brain\e6d8f288-875f-4cd3-a41b-56062ea4a1dc"

for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=150)
    out_path = os.path.join(artifact_dir, f"dyn_page_{i+1}.png")
    pix.save(out_path)
    print(f"Saved {out_path} ({pix.width}x{pix.height})")
