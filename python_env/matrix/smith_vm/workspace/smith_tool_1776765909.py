# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Whitepaper Validator
Enforces the stylistic and Φ‑density invariants extracted from the audit.
"""

import re
import sys
from typing import List, Tuple

# -------------------------------------------------
# CONFIGURABLE PARAMETERS (reflect Ω‑Protocol invariants)
# -------------------------------------------------
TARGET_VERBAL_RATIO = 0.70   # 70% verbal explanation
TARGET_FORMAL_RATIO = 0.30   # 30% formal mathematics
RATIO_TOLERANCE = 0.05       # allow ±5% deviation

# Φ‑density thresholds (from audit)
MAX_SHORT_TERM_COST = 0.15   # 15% upper bound on rewrite cost
MIN_LONG_TERM_GAIN  = 0.30   # 30% lower bound on adoption gain
MIN_NET_GAIN        = 0.20   # 20% net gain required for J* ≥ 0

# Trigger words that indicate an equation is being *conceptually introduced*
CONCEPTUAL_TRIGGERS = {
    r"formalized as",
    r"captured by",
    r"expressed as",
    r"described by",
    r"given by",
    r"represented by",
    r"modeled by",
    r"written as",
    r"equals",
    r"is",
}

# Forbidden patterns (regex)
FORBIDDEN = [
    r"\\appendix",                     # isolated appendix
    r"\\[^\\n]*?\\\\begin\\{equation\\}",  # equation without preceding conceptual sentence (checked separately)
    r"\b(?:it is|was|were)\b.*?\\b(?:demonstrated|shown|proved)\b",  # passive voice obscuring agency
    r"\b(?:quantum|topological|non‑abelian)\b(?!\s+(?:analogy|metaphor|similar))",  # jargon without grounding (simple)
]

def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def split_into_sections(text: str) -> List[str]:
    """Very coarse split: treat blank lines as section boundaries."""
    return [s.strip() for s in re.split(r"\n\s*\n", text) if s.strip()]

def count_verbal_vs_formal(sections: List[str]) -> Tuple[int, int]:
    """Count sentences (verbal) vs. LaTeX equation blocks (formal)."""
    verbal = 0
    formal = 0
    eq_pattern = re.compile(r"\\begin\{equation\}|\\begin\{align\}|\\$\\$.*?\\$\\$|\\$.*?\\$", re.DOTALL)
    for sec in sections:
        # sentences: split on . ! ? followed by space or newline
        sentences = re.split(r"[.!?]\s+", sec)
        verbal += len([s for s in sentences if s.strip()])
        # equation blocks
        formal += len(eq_pattern.findall(sec))
    return verbal, formal

def check_ratio(verbal: int, formal: int) -> bool:
    total = verbal + formal
    if total == 0:
        return False
    verbal_ratio = verbal / total
    formal_ratio = formal / total
    ok = (abs(verbal_ratio - TARGET_VERBAL_RATIO) <= RATIO_TOLERANCE and
          abs(formal_ratio - TARGET_FORMAL_RATIO) <= RATIO_TOLERANCE)
    return ok, verbal_ratio, formal_ratio

def check_embedding(sections: List[str]) -> List[str]:
    """Return list of sections where an equation appears without a conceptual trigger before it."""
    violations = []
    eq_pattern = re.compile(r"\\begin\{equation\}|\\begin\{align\}|\\$\\$.*?\\$\\$|\\$.*?\\$", re.DOTALL)
    for idx, sec in enumerate(sections):
        # Find position of first equation
        match = eq_pattern.search(sec)
        if not match:
            continue
        # Look at the text before the equation
        before_eq = sec[:match.start()]
        # Check for any conceptual trigger (case‑insensitive)
        if not any(re.search(trigger, before_eq, re.I) for trigger in CONCEPTUAL_TRIGGERS):
            violations.append(f"Section {idx+1}: equation lacks preceding conceptual explanation.")
    return violations

def check_forbidden(text: str) -> List[str]:
    violations = []
    for pat in FORBIDDEN:
        if re.search(pat, text, re.I | re.S):
            violations.append(f"Forbidden pattern matched: {pat}")
    return violations

def check_phi_density(cost: float, gain: float) -> Tuple[bool, float]:
    """Return (compliant, net_gain)."""
    net = gain - cost
    compliant = (cost <= MAX_SHORT_TERM_COST and
                 gain >= MIN_LONG_TERM_GAIN and
                 net >= MIN_NET_GAIN)
    return compliant, net

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_omega_whitepaper.py <path_to_text> [cost gain]")
        sys.exit(1)

    path = sys.argv[1]
    text = load_text(path)

    # 1. Ratio & embedding
    sections = split_into_sections(text)
    verbal, formal = count_verbal_vs_formal(sections)
    ratio_ok, v_ratio, f_ratio = check_ratio(verbal, formal)
    embed_violations = check_embedding(sections)

    # 2. Forbidden patterns
    forb_violations = check_forbidden(text)

    # 3. Φ‑density (optional args)
    cost = float(sys.argv[2]) if len(sys.argv) > 2 else 0.08   # default 8%
    gain = float(sys.argv[3]) if len(sys.argv) > 3 else 0.45   # default 45%
    phi_ok, net_gain = check_phi_density(cost, gain)

    # ----- Reporting -----
    print("=== Ω‑Protocol Whitepaper Validation ===")
    print(f"Verbal sentences : {verbal}")
    print(f"Formal blocks    : {formal}")
    print(f"Verbal ratio     : {v_ratio:.2%} (target {TARGET_VERBAL_RATIO:.0%} ±{RATIO_TOLERANCE:.0%})")
    print(f"Formal ratio     : {f_ratio:.2%} (target {TARGET_FORMAL_RATIO:.0%} ±{RATIO_TOLERANCE:.0%})")
    print(f"Ratio OK?        : {'✅' if ratio_ok else '❌'}")
    print()
    if embed_violations:
        print("Embedding violations:")
        for v in embed_violations:
            print(" -", v)
    else:
        print("Embedding check: ✅ All equations preceded by conceptual trigger.")
    print()
    if forb_violations:
        print("Forbidden pattern violations:")
        for v in forb_violations:
            print(" -", v)
    else:
        print("Forbidden patterns: ✅ None detected.")
    print()
    print(f"Φ‑density: short‑term cost = {cost:.1%}, long‑term gain = {gain:.1%}")
    print(f"Net Φ gain = {net_gain:.1%} (required ≥ {MIN_NET_GAIN:.0%})")
    print(f"Φ‑density OK? : {'✅' if phi_ok else '❌'}")
    print()
    overall_ok = ratio_ok and not embed_violations and not forb_violations and phi_ok
    print("=== OVERALL VALIDATION :", "PASS ✅" if overall_ok else "FAIL ❌", "===")
    sys.exit(0 if overall_ok else 1)

if __name__ == "__main__":
    main()