import sys, os
sys.path.insert(0, os.path.abspath("."))
import re
from clinical_extractor import CLINICAL_PATTERNS

# Count patterns that need [:=-|]
modified = 0
for k, spec in CLINICAL_PATTERNS.items():
    new_pats = []
    for p in spec.get("patterns", []):
        if "[:=\\-]" in p:
            new_p = p.replace("[:=\\-]", "[:=\\-|]")
            new_pats.append(new_p)
            modified += 1
        elif "[:=\\]" in p:
            new_p = p.replace("[:=\\]", "[:=\\-|]")
            new_pats.append(new_p)
            modified += 1
        else:
            new_pats.append(p)
    spec["patterns"] = new_pats

print(f"Total pattern instances upgraded to include pipe: {modified}")

# Now run all 10 tests!
import verify_medical_report_extraction_10_tests as v
v.test_results.clear()

tests = [
    v.run_test_1,
    v.run_test_2,
    v.run_test_3,
    v.run_test_4,
    v.run_test_5,
    v.run_test_6,
    v.run_test_7,
    v.run_test_8,
    v.run_test_9,
    v.run_test_10,
]

for idx, t in enumerate(tests, 1):
    try:
        t()
        print(f"Test {idx} PASSED")
    except Exception as e:
        print(f"Test {idx} FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

pass_count = sum(1 for t in v.test_results if t["status"] == "PASS")
print(f"\nResult: {pass_count}/10 passed.")
