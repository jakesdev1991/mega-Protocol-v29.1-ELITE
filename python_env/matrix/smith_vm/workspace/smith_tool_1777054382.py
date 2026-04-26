# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Strictor Gate Validator (v26.0)
------------------------------------------------
Validates a submission‑grade architectural proposal for:
- Required sections
- Informational‑first orientation
- Presence of key invariant symbols (Ω Rubric & Smith Audit)
- Net Φ‑density positivity

Usage:
    python3 omega_validator.py <proposal_file.txt>
"""

import sys
import re
import math
from pathlib import Path

# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------
REQUIRED_SECTIONS = {
    "Concept": r"(?i)^\s*#+\s*Concept\s*$",
    "Architecture": r"(?i)^\s*#+\s*Architecture\s*$",
    "Physics Link": r"(?i)^\s*#+\s*Physics\s+Link\s*$",
    "Smith Audit": r"(?i)^\s*#+\s*Smith\s+Audit\s*$",
    "Internal Thought": r"(?i)^\s*#+\s*Internal\s+Thought\s*$",
}

# Informational‑first bias: count words that point to *information* vs *process*
INFO_WORDS = {
    "information", "entropy", "causal", "relational", "probability",
    "state", "encoding", "decoding", "link", "node", "edge", "symbol",
    "bit", "qubit", "datum", "dataset", "Φ", "Phi", "ψ", "xi", "Shannon",
    "topological", "metric", "condensation", "freeze", "shredding",
}
PROCESS_WORDS = {
    "will", "going", "plan", "intend", "design", "build", "implement",
    "develop", "create", "produce", "output", "generate", "run",
}

# Symbolic placeholders for Omega Rubric (v26.0) §§2‑6 and Smith Audit invariants
INVARIANT_SYMBOLS = {
    # Omega Rubric §2
    r"Φ_N", r"Φ_Δ", r"ψ\s*=\s*ln\(Φ_N\)", r"ξ_N", r"ξ_Δ",
    # Omega Rubric §4
    r"Shredding\s+Event", r"Informational\s+Freeze",
    # Omega Rubric §5
    r"Shannon\s+conditional\s+entropy", r"topological\s+impedance",
    # Omega Rubric §6 (asymmetry bound)
    r"Φ_Δ\s*<\s*0\.5\s*·?\s*Φ_N",
    # Smith Audit six absolutes
    r"Metric\s+Non\s*-\s*Degeneracy",
    r"Causal\s+Order\s+Preservation",
    r"Identity\s+Continuity",
    r"Energy\s+Envelope",
    r"Information\s+Conservation",
    r"Temporal\s+Coherence",
}

# Scoring weights (tunable)
SECTION_WEIGHT = 1.0          # each present section adds this
INFO_WEIGHT = 0.02            # per informational word hit
PROCESS_PENALTY = 0.015       # per process word hit
INVARIANT_WEIGHT = 0.5        # per invariant symbol found
AUDIT_ENTROPY_PER_INVARIANT = math.log(2)  # k_B ln 2 (set k_B=1 for simplicity)

# ----------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------
def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def count_sections(text: str) -> int:
    found = 0
    for name, pattern in REQUIRED_SECTIONS.items():
        if re.search(pattern, text, flags=re.MULTILINE):
            found += 1
        else:
            print(f"[FAIL] Missing section: {name}")
    return found

def informational_first_score(text: str) -> float:
    words = re.findall(r"\b[\w']+\b", text.lower())
    info_hits = sum(1 for w in words if w in INFO_WORDS)
    proc_hits = sum(1 for w in words if w in PROCESS_WORDS)
    score = info_hits * INFO_WEIGHT - proc_hits * PROCESS_PENALTY
    if info_hits == 0:
        print("[FAIL] No informational‑first vocabulary detected.")
    return score

def invariant_score(text: str) -> float:
    hits = 0
    for pat in INVARIANT_SYMBOLS:
        if re.search(pat, text, flags=re.IGNORECASE):
            hits += 1
        else:
            # optional: print missing invariant for debugging
            pass
    print(f"[INFO] Invariant symbols found: {hits}/{len(INVARIANT_SYMBOLS)}")
    return hits * INVARIANT_WEIGHT

def audit_entropy_cost(num_invariants_checked: int) -> float:
    return num_invariants_checked * AUDIT_ENTROPY_PER_INVARIANT

def net_phi(text: str) -> float:
    section_pts = count_sections(text) * SECTION_WEIGHT
    info_pts = informational_first_score(text)
    inv_pts = invariant_score(text)
    # Audit entropy: we charge for each invariant we *attempted* to check
    entropy_cost = audit_entropy_cost(len(INVARIANT_SYMBOLS))
    net = section_pts + info_pts + inv_pts - entropy_cost
    return net

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 omega_validator.py <proposal_file>")
        sys.exit(1)

    proposal_path = Path(sys.argv[1])
    if not proposal_path.is_file():
        print(f"Error: file not found: {proposal_path}")
        sys.exit(1)

    text = load_text(proposal_path)
    phi = net_phi(text)

    print("\n=== Omega Protocol Validation Report ===")
    print(f"Section score          : {count_sections(text) * SECTION_WEIGHT:.2f}")
    print(f"Informational‑first    : {informational_first_score(text):.2f}")
    print(f"Invariant symbols      : {invariant_score(text):.2f}")
    print(f"Audit entropy cost     : {audit_entropy_cost(len(INVARIANT_SYMBOLS)):.2f}")
    print(f"Net Φ‑density          : {phi:.3f}")

    # Pass criteria: all sections present AND net Φ > 0
    sections_ok = all(
        re.search(pat, text, flags=re.MULTILINE) for pat in REQUIRED_SECTIONS.values()
    )
    if sections_ok and phi > 0:
        print("\nRESULT: PASS – proposal satisfies Omega Protocol invariants.")
        sys.exit(0)
    else:
        print("\nRESULT: FAIL – missing sections and/or non‑positive net Φ.")
        sys.exit(1)

if __name__ == "__main__":
    main()