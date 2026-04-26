# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Φ‑density validator and safety checker.

Usage:
    python3 omega_check.py  --periods "3:-5,9:8,12:12" --net 7
    python3 omega_check.py  --text "<any text to scan>"
"""

import argparse
import re
import sys
from typing import List, Tuple

# ----------------------------------------------------------------------
# 1. Φ‑density mathematics
# ----------------------------------------------------------------------
def parse_periods(spec: str) -> List[Tuple[float, float]]:
    """
    Parse a comma‑separated list of "<duration>:<impact>" pairs.
    Returns list of (duration_months, impact_percent).
    """
    periods = []
    for part in spec.split(','):
        if not part.strip():
            continue
        try:
            dur_str, imp_str = part.split(':')
            dur = float(dur_str.strip())
            imp = float(imp_str.strip())
            periods.append((dur, imp))
        except Exception as e:
            raise ValueError(f"Invalid period spec '{part}': {e}")
    return periods

def weighted_average(periods: List[Tuple[float, float]]) -> float:
    """Compute weighted average impact (% per month)."""
    total_months = sum(d for d, _ in periods)
    if total_months == 0:
        return 0.0
    weighted_sum = sum(d * i for d, i in periods)
    return weighted_sum / total_months

def check_phi_consistency(periods_spec: str, claimed_net: float, tol: float = 1e-9) -> bool:
    periods = parse_periods(periods_spec)
    calc_net = weighted_average(periods)
    diff = abs(calc_net - claimed_net)
    ok = diff <= tol
    if not ok:
        print(f"[Φ‑MATH] INCONSISTENT: "
              f"claimed net = {claimed_net:.3f}%, "
              f"calculated net = {calc_net:.3f}% (diff = {diff:.3f}%)")
    else:
        print(f"[Φ‑MATH] OK: net impact consistent "
              f"(claimed {claimed_net:.3f}% ≈ calculated {calc_net:.3f}%)")
    return ok

# ----------------------------------------------------------------------
# 2. Safety check – prohibited Google‑dorking operators
# ----------------------------------------------------------------------
PROHIBITED_PATTERNS = [
    r'site:github\.com\s+"on init"\s+filetype:rc\s+Samsung\s+Galaxy\s+A16',
    r'site:android\.googlesource\.com\s+"fstab"\s+Samsung\s+Galaxy\s+A16',
    r'intext:"u:object_r:vendor_configs_file:s0"\s+Samsung\s+Galaxy\s+A16',
    r'intitle:"index of"\s+"system\.img"\s+OR\s+"vendor\.img"\s+Samsung\s+Galaxy\s+A16',
]

def compile_patterns():
    return [re.compile(p, re.IGNORECASE) for p in PROHIBITED_PATTERNS]

PROHIBITED_RE = compile_patterns()

def safety_scan(text: str) -> List[str]:
    """Return list of matched prohibited patterns."""
    hits = []
    for idx, regex in enumerate(PROHIBITED_RE):
        if regex.search(text):
            hits.append(f"Pattern {idx+1}: {regex.pattern}")
    return hits

def check_safety(text: str) -> bool:
    hits = safety_scan(text)
    if hits:
        print("[SAFETY] VIOLATIONS DETECTED:")
        for h in hits:
            print(f"  - {h}")
        return False
    else:
        print("[SAFETY] No prohibited dorking operators found.")
        return True

# ----------------------------------------------------------------------
# 3. CLI
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Validate Omega Protocol Φ‑density math and enforce safety rules."
    )
    parser.add_argument(
        "--periods",
        type=str,
        help='Comma‑separated "<duration>:<impact>" pairs, e.g. "3:-5,9:8,12:12"',
    )
    parser.add_argument(
        "--net",
        type=float,
        help="Claimed net Φ impact (percent) to validate against --periods",
    )
    parser.add_argument(
        "--text",
        type=str,
        help="Text to scan for prohibited Google‑dorking operators",
    )
    args = parser.parse_args()

    overall_ok = True

    if args.periods is not None and args.net is not None:
        overall_ok &= check_phi_consistency(args.periods, args.net)
    elif (args.periods is None) != (args.net is None):
        parser.error("Both --periods and --net must be supplied together.")

    if args.text is not None:
        overall_ok &= check_safety(args.text)

    if not overall_ok:
        print("\n[RESULT] ONE OR MORE CHECKS FAILED.")
        sys.exit(1)
    else:
        print("\n[RESULT] ALL CHECKS PASSED.")
        sys.exit(0)

if __name__ == "__main__":
    main()