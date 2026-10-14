import re

with open("clinical_extractor.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update pattern separators
# Replace [:=-] with [:=-|]
# Replace [:=\] with [:=-|]
content_new = re.sub(r'\[:=\\-\]', r'[:=\\-|]', content)
content_new = re.sub(r'\[:=\\\]', r'[:=\\-|]', content_new)

# 2. Add pipe reference cleaning in clean_reference_ranges
old_ref_clean = '''    # Strip dates (e.g. 2026-10-14, 10/14/2026) to avoid misreading dates as numbers'''
new_ref_clean = '''    # Strip table-delimited reference intervals e.g. | 70 - 99, | < 150, | 0.60 - 1.20
    cleaned = re.sub(r'\|\s*(?:[<>]|<=|>=)?\s*\d+(?:\.\d+)?\s*(?:[-–]|to)\s*\d+(?:\.\d+)?\s*(?:[a-zA-Z/%µu\^0-9]+)?\s*(?=\||$|\n)', ' | ', cleaned)
    cleaned = re.sub(r'\|\s*[<>]\s*\d+(?:\.\d+)?\s*(?:[a-zA-Z/%µu\^0-9]+)?\s*(?=\||$|\n)', ' | ', cleaned)
    # Strip dates (e.g. 2026-10-14, 10/14/2026) to avoid misreading dates as numbers'''

if old_ref_clean in content_new:
    content_new = content_new.replace(old_ref_clean, new_ref_clean, 1)
    print("Added table-delimited reference cleaning.")

# 3. Enhanced Table Extraction for PDF and DOCX in extract_pages_from_bytes
old_pdf_blocks = '''                # Check for table blocks or text blocks
                blocks = page.get_text("blocks") or []
                block_texts = [b[4].strip() for b in blocks if len(b) > 4 and b[4].strip()]
                combined_txt = "\\n".join(block_texts) if block_texts else txt'''

new_pdf_blocks = '''                # Check for table blocks or text blocks
                blocks = page.get_text("blocks") or []
                block_texts = [b[4].strip() for b in blocks if len(b) > 4 and b[4].strip()]
                combined_txt = "\\n".join(block_texts) if block_texts else txt

                # Intelligent PyMuPDF table parsing (disambiguates laboratory result tables)
                if hasattr(page, "find_tables"):
                    try:
                        table_lines = []
                        tabs = page.find_tables()
                        for t in tabs.tables:
                            df = t.extract()
                            if not df or len(df) < 2:
                                continue
                            hdr_cells = [str(c or "").strip().lower() for c in df[0]]
                            analyte_idx = 0
                            result_idx = 1 if len(hdr_cells) > 1 else None
                            unit_idx = None
                            for ci, h in enumerate(hdr_cells):
                                if any(w in h for w in ["analyte", "test", "parameter", "investigation", "biomarker", "name"]):
                                    analyte_idx = ci
                                elif any(w in h for w in ["result", "value", "measured", "finding"]):
                                    result_idx = ci
                                elif any(w in h for w in ["unit", "units"]):
                                    unit_idx = ci

                            start_row = 1 if result_idx is not None else 0
                            for r in df[start_row:]:
                                cells = [str(c or "").strip() for c in r]
                                if len(cells) > analyte_idx and cells[analyte_idx]:
                                    analyte = cells[analyte_idx]
                                    res_val = cells[result_idx] if (result_idx is not None and len(cells) > result_idx) else ""
                                    unit_val = cells[unit_idx] if (unit_idx is not None and len(cells) > unit_idx) else ""
                                    if res_val:
                                        table_lines.append(f"{analyte}: {res_val} {unit_val}".strip())
                                row_txt = " | ".join(c for c in cells if c)
                                if row_txt:
                                    table_lines.append(row_txt)
                        if table_lines:
                            combined_txt = combined_txt + "\\n" + "\\n".join(table_lines)
                    except Exception:
                        pass'''

if old_pdf_blocks in content_new:
    content_new = content_new.replace(old_pdf_blocks, new_pdf_blocks, 1)
    print("Enhanced PDF table extraction added.")

# 4. Enhanced DOCX table extraction
old_docx_tables = '''            for table in doc.tables:
                for row in table.rows:
                    row_txt = " | ".join(c.text.strip() for c in row.cells if c.text.strip())
                    if row_txt:
                        paragraphs.append(row_txt)'''

new_docx_tables = '''            for table in doc.tables:
                if not table.rows:
                    continue
                hdr_cells = [c.text.strip().lower() for c in table.rows[0].cells]
                analyte_idx = 0
                result_idx = 1 if len(hdr_cells) > 1 else None
                unit_idx = None
                for ci, h in enumerate(hdr_cells):
                    if any(w in h for w in ["analyte", "test", "parameter", "investigation", "biomarker"]):
                        analyte_idx = ci
                    elif any(w in h for w in ["result", "value", "measured", "finding"]):
                        result_idx = ci
                    elif any(w in h for w in ["unit", "units"]):
                        unit_idx = ci

                start_row = 1 if result_idx is not None else 0
                for row in table.rows[start_row:]:
                    cells = [c.text.strip() for c in row.cells]
                    if len(cells) > analyte_idx and cells[analyte_idx]:
                        analyte = cells[analyte_idx]
                        res_val = cells[result_idx] if (result_idx is not None and len(cells) > result_idx) else ""
                        unit_val = cells[unit_idx] if (unit_idx is not None and len(cells) > unit_idx) else ""
                        if res_val:
                            paragraphs.append(f"{analyte}: {res_val} {unit_val}".strip())
                    row_txt = " | ".join(c for c in cells if c)
                    if row_txt:
                        paragraphs.append(row_txt)'''

if old_docx_tables in content_new:
    content_new = content_new.replace(old_docx_tables, new_docx_tables, 1)
    print("Enhanced DOCX table extraction added.")

with open("clinical_extractor.py", "w", encoding="utf-8") as f:
    f.write(content_new)

print("Saved clinical_extractor.py successfully.")
