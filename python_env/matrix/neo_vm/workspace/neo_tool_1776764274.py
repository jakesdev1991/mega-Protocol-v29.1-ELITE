# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re

# Paste the exact Meta‑Scrutiny text below (truncated for brevity)
meta_scrutiny = """
META-PASS
...
METHODS
INSIGHTS
EVOLUTION
1. Detect hidden boilerplate...
2. Derive covariant modes...
3. Cross‑validate...
"""

# Count violations
uppercase_headers = [ln for ln in meta_scrutiny.splitlines() if ln.isupper() and ln.strip()]
numeric_lists     = [ln for ln in meta_scrutiny.splitlines() if re.match(r'^\s*\d+\.\s', ln)]
single_word_hdrs  = [ln for ln in meta_scrutiny.splitlines() if ln.strip() in {'META-PASS','METHODS','INSIGHTS','EVOLUTION'}]

print(f"Uppercase headers: {len(uppercase_headers)}")
print(f"Numeric list items: {len(numeric_lists)}")
print(f"Single‑word headings: {len(single_word_hdrs)}")