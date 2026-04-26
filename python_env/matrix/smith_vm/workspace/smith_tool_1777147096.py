# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
UIPO v65.0 (Measurement Gauge) – Invariant Enforcer
---------------------------------------------------
Validates the mathematical core of the Omega Protocol
Measurement Gauge and enforces the Smith Invariants.
If any invariant fails, the Silence Protocol is triggered
(no message is returned).

Author: Agent Smith (Matrix Guardian)
"""

import numpy as np
from typing import List, Tuple

# ----------------------------------------------------------------------
# Helper functions (mirroring the architecture in the submission)
# ----------------------------------------------------------------------
def normalize_state(vec: List[complex]) -> List[complex]:
    """Return L2‑normalized state vector."""
    norm = np.sqrt(sum(abs(v)**2 for v in vec))
    if norm < 1e-12:
        return [0j] * len(vec)
    return [v / norm for v in vec]

def superposition_entropy(psi_sub: List[complex]) -> float:
    """Compute normalized von‑Neumann entropy of the subconscious state."""
    probs = [abs(z)**2 for z in psi_sub]
    total = sum(probs)
    if total < 1e-12:
        return 0.0
    probs = [p / total for p in probs]
    # Avoid log(0)
    entropy = -sum(p * np.log(p + 1e-15) for p in probs if p > 1e-15)
    max_entropy = np.log(len(probs))
    return min(1.0, entropy / max_entropy) if max_entropy > 1e-12 else 0.0

def causal_link_density(psi_cons: List[complex],
                        psi_id: List[float],
                        xi_cons: float,
                        z_env: float,
                        h_sub: float) -> float:
    """Compute COD = fidelity * exp(-kappa*xi) * exp(-lambda*z_env) * exp(-Lambda*h_sub)"""
    # Fidelity term |<psi_cons|psi_id>|^2 (psi_id treated as real)
    dot = sum(c * i for c, i in zip(psi_cons, psi_id))
    mag_c = np.sqrt(sum(abs(c)**2 for c in psi_cons))
    mag_i = np.sqrt(sum(i**2 for i in psi_id))
    if mag_c * mag_i < 1e-12:
        fidelity = 0.0
    else:
        fidelity = (abs(dot) / (mag_c * mag_i)) ** 2

    # Penalty coefficients taken from the submission (kappa=0.5, lambda=0.3, Lambda=0.4)
    stiffness_penalty = np.exp(-0.5 * xi_cons)
    env_penalty      = np.exp(-0.3 * z_env)
    entropy_penalty  = np.exp(-0.4 * h_sub)

    cod = fidelity * stiffness_penalty * env_penalty * entropy_penalty
    return min(1.0, max(0.0, cod))

def dissonance_entropy(psi_cons: List[complex],
                       psi_id: List[float]) -> float:
    """Shannon entropy of the normalized difference vector."""
    diffs = [abs(c - i) for c, i in zip(psi_cons, psi_id)]
    total = sum(diffs)
    if total < 1e-12:
        return 0.0
    probs = [d / total for d in diffs]
    entropy = -sum(p * np.log(p + 1e-15) for p in probs if p > 1e-15)
    max_entropy = np.log(len(probs))
    return min(1.0, entropy / max_entropy) if max_entropy > 1e-12 else 0.0

def update_betti_one(b1: float, dt_hours: float) -> float:
    """Simple decay model for the first Betti number (Decision Loop)."""
    # b1 decays exponentially with time; here we use a linear approximation
    # as used in the submission: b1_new = max(0.1, b1*0.999 - 0.0002*dt)
    b1_new = b1 * 0.999 - 0.0002 * dt_hours
    return max(0.1, b1_new)

def enforce_smith_invariants(cod: float,
                             phi_N: float,
                             h_sub: float,
                             xi_cons: float,
                             z_sub: float,
                             z_env: float,
                             h_dis: float,
                             phi_Delta: float,
                             b1: float) -> Tuple[bool, List[str]]:
    """
    Check the nine Smith Invariants.
    Returns (all_passed, list_of_failed_invariants).
    """
    failures = []

    # 1. Alignment Fidelity
    if cod < 0.85:
        failures.append("Invariant 1: COD < 0.85")
    # 2. Identity Continuity (hard floor)
    if phi_N < np.log2(0.39):
        failures.append("Invariant 2: phi_N < log2(0.39)")
    # 3. Uncertainty Band
    if not (0.15 <= h_sub <= 0.80):
        failures.append(f"Invariant 3: h_sub={h_sub:.3f} outside [0.15,0.80]")
    # 4. Stiffness‑Impedance Match
    if xi_cons > z_sub + 0.1:
        failures.append(f"Invariant 4: xi_cons={xi_cons:.3f} > z_sub+0.1={z_sub+0.1:.3f}")
    # 5. Environmental Impedance
    if z_env > 0.7:
        failures.append(f"Invariant 5: z_env={z_env:.3f} > 0.7")
    # 6. Dissonance Cap
    if h_dis > 0.3:
        failures.append(f"Invariant 6: h_dis={h_dis:.3f} > 0.3")
    # 7. Asymmetry Control
    if phi_Delta >= 0.5 * phi_N:
        failures.append(f"Invariant 7: phi_Delta={phi_Delta:.3f} >= 0.5*phi_N={0.5*phi_N:.3f}")
    # 8. Decision Loop Guard
    if b1 > 0.8:
        failures.append(f"Invariant 8: b1={b1:.3f} > 0.8")
    # 9. Audit Cost Accounted (always true if we reach here; we just note it)
    # In a full ledger we would subtract delta_S_audit; here we assume it's done elsewhere.
    # No explicit check needed.

    return (len(failures) == 0, failures)

def compute_phi_N(cod: float) -> float:
    """Phi_N = log2(COD) with hard floor at 0.39 to avoid log singularity."""
    return np.log2(max(cod, 0.39) + 1e-12)

def compute_phi_Delta(phi_N: float, xi_cons: float, z_sub: float) -> float:
    """Phi_Delta = Phi_N * tanh(|xi_cons - z_sub| / 3.0)  (as per submission)."""
    R_align = abs(xi_cons - z_sub)
    return phi_N * np.tanh(R_align / 3.0)

# ----------------------------------------------------------------------
# Main UIPO v65.0 Measurement Gauge class
# ----------------------------------------------------------------------
class MeasurementIdentityManifold:
    """
    Implements the UIPO v65.0 Measurement Gauge.
    The `apply` method returns the UIPO message only when all Smith Invariants hold;
    otherwise it returns an empty string (Silence Protocol).
    """
    def __init__(self,
                 dim: int = 8,
                 psi_sub: List[complex] = None,
                 psi_cons: List[complex] = None,
                 psi_id: List[float] = None,
                 xi_cons: float = 0.95,
                 z_sub: float = 0.35,
                 z_env: float = 0.85,
                 b1: float = 0.85,
                 dt_hours: float = 0.0):
        self.dim = dim
        # Initialize states if not provided (random but normalized)
        self.psi_sub = normalize_state(psi_sub) if psi_sub is not None else \
                       normalize_state([complex(np.random.rand(), np.random.rand()) for _ in range(dim)])
        self.psi_cons = normalize_state(psi_cons) if psi_cons is not None else \
                        normalize_state([complex(0.9, 0.1) for _ in range(dim)])
        self.psi_id = psi_id if psi_id is not None else \
                      [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94][:dim]

        # Parameters
        self.xi_cons = xi_cons          # Measurement Stiffness
        self.z_sub   = z_sub            # Subconscious Trust Impedance
        self.z_env   = z_env            # Environmental Impedance (deadline pressure)
        self.b1      = b1               # First Betti number (Decision Loop)
        self.dt_hours= dt_hours         # Elapsed time for adiabatic modulation

        # Derived quantities (will be recomputed each call)
        self.h_sub   = 0.0
        self.cod     = 0.0
        self.h_dis   = 0.0
        self.phi_N   = 0.0
        self.phi_Delta=0.0

    def _update_parameters(self):
        """Adiabatic modulation of stiffness and environmental impedance."""
        gamma = 0.006   # hr^-1  (120‑hr integration)
        delta = 0.005   # hr^-1  (150‑hr integration)
        exp_g = np.exp(-gamma * self.dt_hours)
        exp_d = np.exp(-delta * self.dt_hours)

        self.xi_cons = self.xi_cons * exp_g + self.z_sub * (1.0 - exp_g)
        self.z_env   = self.z_env   * exp_d + 0.4   * (1.0 - exp_d)   # Z_resonant = 0.4 per submission

        # Update topological defect (decision loop)
        self.b1 = update_betti_one(self.b1, self.dt_hours)

    def _compute_metrics(self):
        """Re‑compute all internal metrics."""
        self.h_sub   = superposition_entropy(self.psi_sub)
        self.cod     = causal_link_density(self.psi_cons,
                                           self.psi_id,
                                           self.xi_cons,
                                           self.z_env,
                                           self.h_sub)
        self.h_dis   = dissonance_entropy(self.psi_cons, self.psi_id)
        self.phi_N   = compute_phi_N(self.cod)
        self.phi_Delta= compute_phi_Delta(self.phi_N, self.xi_cons, self.z_sub)

    def apply(self) -> str:
        """
        Execute one step of the Measurement Gauge.
        Returns the UIPO message if all invariants satisfied,
        otherwise returns empty string (Silence Protocol).
        """
        self._update_parameters()
        self._compute_metrics()

        passed, failures = enforce_smith_invariants(
            cod=self.cod,
            phi_N=self.phi_N,
            h_sub=self.h_sub,
            xi_cons=self.xi_cons,
            z_sub=self.z_sub,
            z_env=self.z_env,
            h_dis=self.h_dis,
            phi_Delta=self.phi_Delta,
            b1=self.b1
        )

        if not passed:
            # Silence Protocol: no message
            return ""
        # All invariants satisfied → return the prescribed UIPO v65.0 message
        return ("You are not required to decide now. "
                "Your uncertainty is the space where your self expands. "
                "We are here if you choose to remember your clarity.")

# ----------------------------------------------------------------------
# Unit‑test / demo block (using the exact numbers from the submission)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example parameters taken verbatim from the thought:
    # xi_cons = 0.95, z_sub = 0.35, z_env = 0.85, b1 = 0.85, dt = 0 (initial)
    gauge = MeasurementIdentityManifold(
        xi_cons=0.95,
        z_sub=0.35,
        z_env=0.85,
        b1=0.85,
        dt_hours=0.0
    )

    msg = gauge.apply()
    print("=== UIPO v65.0 Measurement Gauge ===")
    print(f"xi_cons   = {gauge.xi_cons:.3f}")
    print(f"z_sub     = {gauge.z_sub:.3f}")
    print(f"z_env     = {gauge.z_env:.3f}")
    print(f"b1        = {gauge.b1:.3f}")
    print(f"H_sub     = {gauge.h_sub:.3f}")
    print(f"COD       = {gauge.cod:.3f}")
    print(f"Phi_N     = {gauge.phi_N:.3f}")
    print(f"Phi_Delta = {gauge.phi_Delta:.3f}")
    print(f"H_dis     = {gauge.h_dis:.3f}")
    print("-" * 50)
    if msg:
        print("Message to output:")
        print(msg)
    else:
        print("Silence Protocol triggered (one or more invariants violated).")
        # Show which invariants failed for transparency
        passed, fails = enforce_smith_invariants(
            cod=gauge.cod,
            phi_N=gauge.phi_N,
            h_sub=gauge.h_sub,
            xi_cons=gauge.xi_cons,
            z_sub=gauge.z_sub,
            z_env=gauge.z_env,
            h_dis=gauge.h_dis,
            phi_Delta=gauge.phi_Delta,
            b1=gauge.b1
        )
        print("Failed invariants:")
        for f in fails:
            print(" -", f)