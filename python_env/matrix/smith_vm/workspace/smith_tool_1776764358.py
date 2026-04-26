# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re
import sys

def contains_boilerplate(text: str) -> bool:
    """
    Return True if the text contains any of the prohibited boilerplate patterns:
    - Markdown headings (lines starting with #)
    - Unordered list markers (-, *, +) at line start
    - Ordered list markers (digit + '.' + space) at line start
    - Common explicit section labels used as headings
    """
    lines = text.splitlines()
    # Patterns for headings and lists
    heading_pat = re.compile(r'^\s*#{1,6}\s')          # ### ...
    unordered_pat = re.compile(r'^\s*[-*+]\s')        # - ...
    ordered_pat   = re.compile(r'^\s*\d+\.\s')        # 1. ...
    # Explicit section labels that often appear as headings (case‑insensitive)
    label_pat = re.compile(
        r'^\s*(internal\s+thought\s+process|final\s+output|『……』|scrutiny\s+audit|'
        r'phase\s+\d+|step\s+\d+|engine\s+output|meta‑scrutiny|reflection)\s*:?\s*$',
        re.IGNORECASE
    )

    for i, line in enumerate(lines, 1):
        if heading_pat.match(line):
            print(f"Line {i}: Markdown heading detected → {line!r}")
            return True
        if unordered_pat.match(line):
            print(f"Line {i}: Unordered list marker detected → {line!r}")
            return True
        if ordered_pat.match(line):
            print(f"Line {i}: Ordered list marker detected → {line!r}")
            return True
        if label_pat.match(line):
            print(f"Line {i}: Explicit section label detected → {line!r}")
            return True
    return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_omega.py <path-to-text-file>")
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        content = f.read()
    if contains_boilerplate(content):
        print("\nBOILERPLATE VIOLATION: The submission does NOT satisfy the NO BOILERPLATE rule.")
        sys.exit(1)
    else:
        print("\nNO BOILERPLATE DETECTED: The submission passes the formatting check.")
        # Further mathematical validation could be added here if desired.
        sys.exit(0)

if __name__ == "__main__":
    main()