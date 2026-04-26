# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
detect_rubric_violations.py
Scans a piece of text for violations of the Omega Physics Rubric v26.0:
 - NO BOILERPLATE (headings, lists, fixed phrases)
 - Entropy‑based observable present
"""

import re
import sys

def check_boilerplate(text: str) -> list[str]:
    """Return list of boiler‑plate violations found in text."""
    violations = []

    # Headings: lines that start with one or more # characters
    heading_pattern = re.compile(r'^\s*#+\s+', re.MULTILINE)
    if heading_pattern.search(text):
        violations.append("NO BOILERPLATE violation: markdown headings present")

    # Fixed meta‑scrutiny phrase (the rubric forbids any boiler‑plate repetition)
    if "META-PASS" in text:
        violations.append("NO BOILERPLATE violation: fixed phrase 'META-PASS' detected")

    # Add other boiler‑plate patterns as needed (e.g., numbered lists, bold labels)
    # For brevity we only check headings and the meta‑phrase here.

    return violations

def check_entropy_observable(text: str) -> bool:
    """Return True if a Shannon‑entropy‑based observable is mentioned."""
    # Look for keywords that indicate an entropy gauge
    entropy_keywords = ["entropy", "Shannon", "S_embed", "information entropy", "distribution entropy"]
    return any(kw in text.lower() for kw in entropy_keywords)

def main():
    # Example: the meta‑scrutiny output we want to verify
    meta_scrutiny_output = """
### Internal Thought Process for Meta-Scrutiny
...
### Final Output
META-PASS
...
### Reflection on Omega Protocol Φ Density Impact
...
"""

    # Alternatively, read from stdin if you pipe the real output
    # meta_scrutiny_output = sys.stdin.read()

    # Run checks
    bp_violations = check_boilerplate(meta_scrutiny_output)
    entropy_present = check_entropy_observable(meta_scrutiny_output)

    # Report results
    print("=== Rubric Compliance Check ===")
    if bp_violations:
        for v in bp_violations:
            print(f"FAIL: {v}")
    else:
        print("PASS: No boiler‑plate violations detected.")

    if entropy_present:
        print("PASS: Entropy‑based observable found.")
    else:
        print("FAIL: Entropy‑based observable missing.")

    # Overall verdict
    if not bp_violations and entropy_present:
        print("\nOverall: COMPLIANT")
        sys.exit(0)
    else:
        print("\nOverall: NON‑COMPLIANT")
        sys.exit(1)

if __name__ == "__main__":
    main()