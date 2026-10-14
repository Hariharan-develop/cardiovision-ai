import os, io, sys
sys.path.insert(0, os.path.abspath("."))
import pymupdf
import docx

def parse_docx_tables(doc):
    table_lines = []
    for table in doc.tables:
        if not table.rows:
            continue
        hdr_cells = [c.text.strip().lower() for c in table.rows[0].cells]
        analyte_idx = 0
        result_idx = 1 if len(hdr_cells) > 1 else None
        unit_idx = None
        for i, h in enumerate(hdr_cells):
            if any(w in h for w in ["analyte", "test", "parameter", "investigation", "biomarker"]):
                analyte_idx = i
            elif any(w in h for w in ["result", "value", "measured", "finding"]):
                result_idx = i
            elif any(w in h for w in ["unit", "units"]):
                unit_idx = i

        start_row = 1 if result_idx is not None else 0
        for row in table.rows[start_row:]:
            cells = [c.text.strip() for c in row.cells]
            if len(cells) > analyte_idx and cells[analyte_idx]:
                analyte = cells[analyte_idx]
                res_val = cells[result_idx] if (result_idx is not None and len(cells) > result_idx) else ""
                unit_val = cells[unit_idx] if (unit_idx is not None and len(cells) > unit_idx) else ""
                if res_val:
                    table_lines.append(f"{analyte}: {res_val} {unit_val}".strip())
            # also include the standard row
            row_txt = " | ".join(c for c in cells if c)
            if row_txt:
                table_lines.append(row_txt)
    return table_lines

with open("test_output/extraction_tests/test4_medical_report.docx", "rb") as f:
    d = docx.Document(io.BytesIO(f.read()))
lines = parse_docx_tables(d)
print("DOCX parsed table lines:")
for l in lines:
    print("  ", l)
