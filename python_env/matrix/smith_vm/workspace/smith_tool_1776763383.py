# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol v26.0 Compliance Checker
---------------------------------------
Checks a physics‑task output for:
  * NO BOILERPLATE   – no markdown headings, no bold markup, no ordered lists.
  * DIMENSIONAL CHECK – presence of an explicit dimensional‑consistency statement.
  * ENTROPY PILLAR   – at least one entropy‑related term (entropy, Shannon,
                       topological impedance, conditional entropy, etc.).

Usage:
    python3 omega_check.py "<text to validate>"
"""

import sys
import re

def has_boilerplate(text: str) -> bool:
    """Return True if any boilerplate pattern is found."""
    # Markdown headings: lines starting with one or more '#'
    if re.search(r'^\s*#{1,6}\s', text, flags=re.M):
        return True
    # Bold markup: **text** or __text__
    if re.search(r'\*\*[^\*]+\*\*|__[^_]+__', text):
        return True
    # Ordered list: line starts with a number followed by a dot and space
    if re.search(r'^\s*\d+\.\s+', text, flags=re.M):
        return True
    return False

def has_dimensional_check(text: str) -> bool:
    """Look for an explicit dimensional‑consistency verification."""
    # Accept a variety of phrasings; case‑insensitive.
    patterns = [
        r'dimensional\s+consistency',
        r'check.*dimension',
        r'verify.*dimension',
        r'each term.*dimension',
        r'[Dd]imensions?\s+match',
    ]
    return any(re.search(p, text, flags=re.I) for p in patterns)

def has_entropy_reference(text: str) -> bool:
    """Detect entropy‑related terminology required for gauge tasks."""
    entropy_terms = [
        r'entropy',
        r'shannon',
        r'conditional\s+entropy',
        r'topological\s+impedance',
        r'information\s+entropy',
        r'relative\s+entropy',
        r'kullback[- ]leitner',
    ]
    pattern = re.compile('|'.join(entropy_terms), flags=re.I)
    return bool(pattern.search(text))

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 omega_check.py \"<text>\"")
        sys.exit(1)

    text = sys.argv[1]

    boilerplate = has_boilerplate(text)
    dim_ok      = has_dimensional_check(text)
    entropy_ok  = has_entropy_reference(text)

    report = {
        "NO_BOILERPLATE": not boilerplate,
        "DIMENSIONAL_CHECK": dim_ok,
        "ENTROPY_PILLAR": entropy_ok,
    }

    all_pass = all(report.values())

    print("Omega Protocol Compliance Report:")
    for k, v in report.items():
        status = "PASS" if v else "FAIL"
        print(f"  {k}: {status}")
    print("\nOverall:", "PASS" if all_pass else "FAIL")

    # Exit code 0 for PASS, non‑zero for FAIL (useful in automation)
    sys.exit(0 if all_pass else 1)

if __name__ == "__main__":
    main()