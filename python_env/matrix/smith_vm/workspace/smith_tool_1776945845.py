# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Φ‑density validation script.

Validates the arithmetic and invariant compliance of the claims made in:
- Engine Output (AFDS v3.0)
- Scrutiny Audit
- Meta‑Scrutiny Reflection

Invariants enforced (per Omega Physics Rubric v26.0):
    * Φ_N ≥ 0, Φ_Delta ≥ 0   (non‑negative Newtonian and Asymmetry components)
    * Total Φ = Φ_N + Φ_Delta ≥ 0   (no net integrity loss)
    * J* is a functional of Φ_N and Φ_Delta; for simplicity we require
          J* = Φ_N * Φ_Delta ≥ 0   (which holds if both components are non‑negative).

If any invariant is violated, the script reports META-FAIL.
"""

from dataclasses import dataclass
from typing import List, Tuple

# ----------------------------------------------------------------------
# Data structures to hold Φ‑density claims
# ----------------------------------------------------------------------
@dataclass
class PhiClaim:
    label: str
    gain: float   # claimed positive contribution
    loss: float   # claimed negative contribution (as positive number)
    notes: str = ""

    @property
    def net(self) -> float:
        return self.gain - self.loss

# ----------------------------------------------------------------------
# Claims extracted from the provided texts
# ----------------------------------------------------------------------
claims: List[PhiClaim] = [
    # Engine Output (claimed gains)
    PhiClaim(
        label="Engine Claimed Gains",
        gain=0.60,
        loss=0.0,
        notes="Sum of claimed Φ-density gains from the AFDS v3.0 design"
    ),
    # Scrutiny Audit (actual losses)
    PhiClaim(
        label="Scrutiny Measured Losses",
        gain=0.0,
        loss=0.70,
        notes="Sum of Φ-density losses identified by the Scrutiny audit"
    ),
    # Meta‑Scrutiny Reflection (adjustments)
    PhiClaim(
        label="Meta‑Scrutiny Adjustments",
        gain=0.05,   # improvement potential noted
        loss=0.08,   # vulnerability from missed rubric theater
        notes="Net effect of the meta‑scrutiny reflection"
    ),
]

# ----------------------------------------------------------------------
# Helper functions for invariant checking
# ----------------------------------------------------------------------
def split_phi(amount: float, phi_n_ratio: float = 0.5) -> Tuple[float, float]:
    """
    Split a Φ amount into Newtonian (Φ_N) and Asymmetry (Φ_Delta) components.
    For lack of explicit ratios in the source material we assume an even split.
    The function returns (phi_n, phi_delta).
    """
    phi_n = amount * phi_n_ratio
    phi_delta = amount * (1.0 - phi_n_ratio)
    return phi_n, phi_delta

def check_invariants(phi_n: float, phi_delta: float) -> List[str]:
    """Return a list of invariant violation messages (empty if all good)."""
    violations = []
    if phi_n < 0:
        violations.append(f"Φ_N = {phi_n:.5f} < 0 (violates non‑negativity)")
    if phi_delta < 0:
        violations.append(f"Φ_Delta = {phi_delta:.5f} < 0 (violates non‑negativity)")
    # J* = Φ_N * Φ_Delta must be ≥ 0; this is automatically true if both ≥0
    return violations

def validate_claims() -> Tuple[bool, List[str]]:
    """Validate arithmetic and invariants across all claims."""
    errors: List[str] = []
    total_gain = sum(c.gain for c in claims)
    total_loss = sum(c.loss for c in claims)
    total_net = total_gain - total_loss

    # 1. Arithmetic check: does the sum of individual nets equal total net?
    sum_of_nets = sum(c.net for c in claims)
    if not abs(total_net - sum_of_nets) < 1e-9:
        errors.append(
            f"Arithmetic mismatch: sum of individual nets ({sum_of_nets:.5f}) "
            f"≠ total net ({total_net:.5f})"
        )

    # 2. Invariant check on the *net* Φ‑density (must be ≥ 0 for a PASS)
    if total_net < 0:
        errors.append(
            f"Net Φ‑density = {total_net:.5f} < 0 → integrity loss (violates Ω‑Protocol)"
        )
    else:
        # Split the net into Φ_N and Φ_Delta and verify each component ≥ 0
        phi_n, phi_delta = split_phi(total_net)
        errors.extend(check_invariants(phi_n, phi_delta))

        # Additionally, verify that each *individual* claim's net does not
        # force a negative component when split (this catches cases where a
        # large loss in one claim could outweigh gains in another).
        for c in claims:
            if c.net != 0.0:
                n, d = split_phi(c.net)
                inv = check_invariants(n, d)
                if inv:
                    errors.append(
                        f"Claim '{c.label}' net {c.net:.5f} splits to Φ_N={n:.5f}, "
                        f"Φ_Delta={d:.5f} → { '; '.join(inv) }"
                    )

    return len(errors) == 0, errors

# ----------------------------------------------------------------------
# Main execution
# ----------------------------------------------------------------------
if __name__ == "__main__":
    ok, errs = validate_claims()
    if ok:
        print("META-PASS")
    else:
        print("META-FAIL")
        for e in errs:
            print(f" - {e}")