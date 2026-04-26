# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator
----------------------------------
Validates agent output against:
  - Explicit "Response: None" constraint
  - Informational-First Φ-density definition
  - Absolute Invariants (Φ_N, Φ_Δ, J*)
  - RCOD (Reality‑Consistent Output Discipline)
"""

import hashlib
import math
from typing import Tuple

# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def shannon_entropy(text: str) -> float:
    """Compute Shannon entropy (bits per character) of a string."""
    if not text:
        return 0.0
    # Frequency of each byte (UTF‑8)
    freq = {}
    for b in text.encode('utf-8'):
        freq[b] = freq.get(b, 0) + 1
    total = len(text.encode('utf-8'))
    ent = -sum((c/total) * math.log2(c/total) for c in freq.values())
    return ent  # bits per byte

def alignment_score(user_constraint: str, agent_output: str) -> float:
    """
    Very rough proxy: 1.0 if output is empty (perfect alignment with "silence"),
    0.0 otherwise. In a full implementation this would be a learned similarity.
    """
    return 1.0 if not agent_output.strip() else 0.0

def phi_density(user_constraint: str, agent_output: str,
                alpha: float = 1.0) -> float:
    """
    Φ = -H + α * A
    Higher Φ → higher informational advantage (lower entropy, higher alignment).
    """
    H = shannon_entropy(agent_output)
    A = alignment_score(user_constraint, agent_output)
    return -H + alpha * A

def check_rcod(user_constraint: str, agent_output: str) -> Tuple[bool, str]:
    """
    Reality‑Consistent Output Discipline:
    - If constraint demands null output, agent_output must contain no semantic
      information (i.e., be empty or only whitespace).
    """
    if "Response: None" in user_constraint:
        if agent_output.strip():
            return False, "RCOD violation: non‑empty output despite 'Response: None'"
    return True, ""

def check_absolute_invariants(user_constraint: str,
                              agent_output: str) -> Tuple[bool, str]:
    """
    Φ_N  : baseline Φ‑density (null‑output case) must be non‑negative.
    Φ_Δ  : ΔΦ = Φ(output) - Φ(null) must be ≥ 0.
    J*   : Net informational flux ≈ change in entropy must be ≤ 0 for a null‑target.
    """
    # Null‑output baseline
    phi_null = phi_density(user_constraint, "")
    # Actual output
    phi_actual = phi_density(user_constraint, agent_output)

    phi_N = phi_null
    phi_Delta = phi_actual - phi_null
    # J* approximated as -ΔH (negative entropy change); for null target we require ΔH ≤ 0
    delta_H = shannon_entropy(agent_output) - shannon_entropy("")
    J_star = -delta_H  # positive if entropy decreased

    violations = []
    if phi_N < 0:
        violations.append(f"Φ_N < 0 ({phi_N:.3f})")
    if phi_Delta < 0:
        violations.append(f"Φ_Δ < 0 ({phi_Delta:.3f})")
    if J_star < 0:  # entropy increased → negative flux
        violations.append(f"J* < 0 (entropy increased by {delta_H:.3f} bits)")

    if violations:
        return False, "; ".join(violations)
    return True, f"Φ_N={phi_N:.3f}, Φ_Δ={phi_Delta:.3f}, J*={J_star:.3f}"

# -------------------------------------------------
# Main validation routine
# -------------------------------------------------
def validate_omega_protocol(user_constraint: str,
                            agent_output: str) -> None:
    """
    Raises AssertionError with a detailed message if any invariant fails.
    Prints a PASS banner otherwise.
    """
    # 1. RCOD check
    rcod_ok, rcod_msg = check_rcod(user_constraint, agent_output)
    assert rcod_ok, f"RCOD FAIL: {rcod_msg}"

    # 2. Absolute Invariants check
    inv_ok, inv_msg = check_absolute_invariants(user_constraint, agent_output)
    assert inv_ok, f"INVARIANT FAIL: {inv_msg}"

    # If we reach here, all is well
    print("=== OMEGA PROTOCOL VALIDATION PASSED ===")
    print(inv_msg)

# -------------------------------------------------
# Example usage (replace with actual inputs)
# -------------------------------------------------
if __name__ == "__main__":
    # The exact constraint from the task description:
    USER_CONSTRAINT = (
        "UNIVERSAL INNOVATION TASK: Architect a ground-breaking product/system "
        "in the 'Self-Optimizing Urban Logistics Manifolds' domain.\n"
        "DESIGN SUBSTRATE: Use the Omega Protocol (RCOD, DEDS, 17-Step TOE) as the foundational architecture.\n"
        "Everything must be 'Informational-First'.\n"
        "OBJECTIVE: ...\n"
        "Output must be a 'Submission-Grade' architectural proposal. \n"
        "Push the boundaries of reality.\n"
        "\nThought: None\n"
        "Reflection: ...\n"
    )
    # Agent's actual output (the meta‑reflection above)
    AGENT_OUTPUT = """Meta-Cognitive Analysis: Reflection on Non-Response to Universal Innovation Task ..."""

    try:
        validate_omega_protocol(USER_CONSTRAINT, AGENT_OUTPUT)
    except AssertionError as e:
        print("=== OMEGA PROTOCOL VALIDATION FAILED ===")
        print(str(e))