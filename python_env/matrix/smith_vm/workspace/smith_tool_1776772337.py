# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Boilerplate Validator
------------------------------------
Checks a given text for violations of the NO BOILERPLATE pillar:
  - Markdown headings (lines starting with one or more '#')
  - Horizontal rules (---, ***, ___)
  - Ordered/unordered list markers at line start
  - Markdown code fences (``` or ~~~)
  - Blockquote markers (>)
If any pattern is found, the audit fails.
"""

import re
import sys

def load_text(source):
    """Read text from a file path or stdin."""
    if source == '-':
        return sys.stdin.read()
    try:
        with open(source, 'r', encoding='utf-8') as f:
            return f.read()
    except OSError as e:
        sys.stderr.write(f"Error reading {source}: {e}\n")
        sys.exit(1)

def check_boilerplate(text):
    """Return list of (line_no, snippet) violations."""
    lines = text.splitlines()
    violations = []

    # Pre‑compiled regexes for speed
    heading_re   = re.compile(r'^\s*#{1,6}\s')          # # Heading
    hr_re        = re.compile(r'^\s*([-*_])\s*\1\s*\1\s*$')  # ---, ***, ___
    ol_re        = re.compile(r'^\s*\d+\.\s')          # 1. Item
    ul_re        = re.compile(r'^\s*[-*+]\s')          # - Item
    fence_re     = re.compile(r'^\s*(```|~~~)')        # code fences
    bq_re        = re.compile(r'^\s*>')                # blockquote

    for i, line in enumerate(lines, start=1):
        if heading_re.match(line):
            violations.append((i, line.rstrip()))
            continue
        if hr_re.match(line):
            violations.append((i, line.rstrip()))
            continue
        if ol_re.match(line):
            violations.append((i, line.rstrip()))
            continue
        if ul_re.match(line):
            violations.append((i, line.rstrip()))
            continue
        if fence_re.match(line):
            violations.append((i, line.rstrip()))
            continue
        if bq_re.match(line):
            violations.append((i, line.rstrip()))
            continue

    return violations

def main():
    if len(sys.argv) > 2:
        sys.stderr.write("Usage: validate_boilerplate.py [FILE|-]\n")
        sys.exit(1)

    source = sys.argv[1] if len(sys.argv) == 2 else '-'
    text = load_text(source)
    bad = check_boilerplate(text)

    if not bad:
        print("PASS: No boilerplate detected.")
        sys.exit(0)
    else:
        print("FAIL: Boilerplate violations found:")
    for lineno, snippet in bad:
        print(f"  Line {lineno}: {snippet}")
    sys.exit(1)

if __name__ == "__main__":
    main()