# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
import re
import sys

def rubric_check(text: str) -> bool:
    """Return True if text satisfies the Omega Physics Rubric v26.0 constraints."""
    # 1. No boilerplate: markdown headings, bold markup, list markers
    heading_pattern = re(r'^\s*#{1,6}\s', re.MULTILINE)
    bold_pattern    = re(r'\*\*')
    list_pattern    = re(r'^\s*[-*]\s|^\s*\d+\.\s', re.MULTILINE)

    if heading_pattern.search(text):
        print("FAIL: Markdown heading detected.")
        return False
    if bold_pattern.search(text):
        print("FAIL: Bold markup detected.")
        return False
    if list_pattern.search(text):
        print("FAIL: List-like pattern detected.")
        return False

    # 2. Required technical tokens (case‑insensitive)
    required = [
        r'\bphi_N\b', r'\bphi_delta\b',   # covariant modes (Φ_N, Φ_Δ)
        r'\bpsi\b', r'\bxi_N\b', r'\bxi_delta\b',  # invariants
        r'shannon\s+entropy', r'\bS\s*\(\s*t\s*\)',  # entropy observable
        r'omega\s+action', r'ricci\s+tensor', r'christoffel',  # equation‑level derivation
        r'shredding\s+event', r'informational\s+freeze',  # boundaries
        r'dimension',  # dimensional consistency statement
        r'phi_density\s+impact', r'net\s+gain'  # Φ‑density impact assessment
    ]
    missing = []
    for pat in required:
        if not re.search(pat, text, re.IGNORECASE):
            missing.append(pat)
    if missing:
        print(f"FAIL: Missing required tokens: {missing}")
        return False

    # 3. Basic sanity: ensure text is not empty after stripping whitespace
    if not text.strip():
        print("FAIL: Empty submission.")
        return False

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 rubric_check.py <candidate_text_file>")
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        candidate = f.read()
    if rubric_check(candidate):
        print("PASS: Submission complies with Omega Physics Rubric v26.0.")
        sys.exit(0)
    else:
        sys.exit(1)