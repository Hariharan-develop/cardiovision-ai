import pymupdf
import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".gemini"))

with open(r"c:\Users\hario\Downloads\CardioVision-AI\pdf_generator.py", "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect where render_model_shap_section returns
old_return = """        return [
            banner_table,
            Spacer(1, 2),
            feat_table,
            Spacer(1, 2),
            charts_table,
            Spacer(1, 6)
        ]"""

new_return = """        return [
            KeepTogether([
                banner_table,
                Spacer(1, 2),
                feat_table,
                Spacer(1, 2),
                charts_table
            ]),
            Spacer(1, 4)
        ]"""

text = text.replace(old_return, new_return)

# Also wrap Section 4
old_sec4 = """    # Section 4: 3D Coronary Heart Visualization
    story.append(Paragraph("4. 3D Coronary Heart Visualization", styles['SectionHeader']))
    story.append(Paragraph(
        "High-resolution anatomical perspective from the interactive Three.js 106-mesh BodyParts3D cardiac model.",
        styles['Subtitle']
    ))
    story.append(Spacer(1, 3))"""

# and story.append(vis_table)
# Remove PageBreaks
text = text.replace("story.append(PageBreak())", "# PageBreak removed for dynamic pagination")

# Write to test_dyn_gen2.py
with open(r"c:\Users\hario\Downloads\CardioVision-AI\.gemini\test_dyn_gen2.py", "w", encoding="utf-8") as f:
    f.write(text)

print("test_dyn_gen2.py created successfully.")
