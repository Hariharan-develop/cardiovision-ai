import os, io, sys
sys.path.insert(0, os.path.abspath("."))
import pymupdf

def parse_pymupdf_tables(page):
    table_lines = []
    if hasattr(page, "find_tables"):
        try:
            tabs = page.find_tables()
            for t in tabs.tables:
                df = t.extract()
                if not df or len(df) < 2:
                    continue
                hdr_cells = [str(c or "").strip().lower() for c in df[0]]
                analyte_idx = 0
                result_idx = 1 if len(hdr_cells) > 1 else None
                unit_idx = None
                for i, h in enumerate(hdr_cells):
                    if any(w in h for w in ["analyte", "test", "parameter", "investigation", "biomarker", "name"]):
                        analyte_idx = i
                    elif any(w in h for w in ["result", "value", "measured", "finding"]):
                        result_idx = i
                    elif any(w in h for w in ["unit", "units"]):
                        unit_idx = i

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
        except Exception as e:
            print("Table err:", e)
    return table_lines

doc = pymupdf.open("test_output/extraction_tests/test5_lab_tables.pdf")
for p in doc:
    lines = parse_pymupdf_tables(p)
    print(f"PyMuPDF parsed table lines ({len(lines)}):")
    for l in lines[:10]:
        print("  ", l)
