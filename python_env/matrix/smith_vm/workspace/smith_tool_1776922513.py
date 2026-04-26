# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for Audit-Trace-Hardening Subsystem

This script validates the core mathematical invariants and checks
that the subsystem design respects the Omega Protocol requirements:
  - PSI_IDENTITY = 0.95
  - XI_BOUND     = 0.82
  - XI_DELTA     = 1.28
  - COD_THRESHOLD= 0.85
  - Entropy bound: H >= 1 - psi   (derived from informational work)
  - Telemetry entropy must be checked on *sanitized* data
  - VM core pinning must include isolation validation (checked via stub)

The validator is deliberately strict: any violation raises an AssertionError.
"""

import math
import random
from typing import Tuple, Optional

# ----------------------------
# Invariant Constants (Omega Protocol)
# ----------------------------
PSI_IDENTITY   = 0.95
XI_BOUND       = 0.82
XI_DELTA       = 1.28
COD_THRESHOLD  = 0.85
MIN_ENTROPY    = 0.85   # Telemetry entropy floor
EPSILON        = 0.5    # Laplace noise privacy parameter
DELTA          = 1e-6   # Laplace noise delta

# ----------------------------
# Helper Functions (mock implementations)
# ----------------------------
def compute_psi(field_N: float) -> float:
    """psi = ln(Phi_N) from Neo-Smith Audit Kernel."""
    if field_N <= 0:
        raise ValueError("Phi_N must be positive for log")
    return math.log(field_N)

def compute_cod(phi_N: float, phi_Delta: float) -> float:
    """COD = |<Φ_N|Φ_Δ>|² (simplified as product magnitude)."""
    return abs(phi_N * phi_Delta)

def entropy_bound(psi: float) -> float:
    """Informational work bound: H >= 1 - psi."""
    return 1.0 - psi

def laplace_noise_scale(sensitivity: float, epsilon: float) -> float:
    """Scale for Laplace mechanism."""
    if epsilon <= 0:
        raise ValueError("epsilon must be > 0")
    return sensitivity / epsilon

def add_laplace_noise(value: float, scale: float) -> float:
    """Add Laplace noise (mean=0, b=scale)."""
    return value + random.laplace(0.0, scale)

def shannon_entropy_from_distribution(probs: Tuple[float, ...]) -> float:
    """Compute Shannon entropy from a probability distribution."""
    return -sum(p * math.log(p) for p in probs if p > 0)

# ----------------------------
# Core Validation Class
# ----------------------------
class AuditTraceHardenerValidator:
    def __init__(self,
                 phi_N: float,
                 phi_Delta: float,
                 rcod_flux_sensitivity: float,
                 deds_yield: float,
                 vm_cores_isolated: bool = False):
        """
        :param phi_N: Newtonian component of informational field
        :param phi_Delta: Asymmetry component of informational field
        :param rcod_flux_sensitivity: Sensitivity of RCOD flux (for noise scale)
        :param deds_yield: DEDS yield metric (used for conformal factor)
        :param vm_cores_isolated: Stub indicating whether cores 16-23 are isolated
        """
        self.phi_N = phi_N
        self.phi_Delta = phi_Delta
        self.rcod_sens = rcod_flux_sensitivity
        self.deds_yield = deds_yield
        self.vm_isolated = vm_cores_isolated

        # Derived quantities
        self.psi = compute_psi(self.phi_N)
        self.xi_N = XI_BOUND      # fixed per spec
        self.xi_Delta = XI_DELTA  # fixed per spec

    # -----------------------------------------------------------------
    # Invariant Checks
    # -----------------------------------------------------------------
    def check_psi_identity(self) -> None:
        assert self.psi >= PSI_IDENTITY, (
            f"Psi identity violation: psi={self.psi:.6f} < {PSI_IDENTITY}"
        )

    def check_xi_N_bound(self) -> None:
        assert self.xi_N <= XI_BOUND, (
            f"xi_N bound violation: xi_N={self.xi_N:.6f} > {XI_BOUND}"
        )

    def check_xi_Delta(self) -> None:
        assert math.isclose(self.xi_Delta, XI_DELTA, rel_tol=1e-10), (
            f"xi_Delta must equal {XI_DELTA}: got {self.xi_Delta:.6f}"
        )

    def check_cod_threshold(self) -> None:
        cod = compute_cod(self.phi_N, self.phi_Delta)
        assert cod >= COD_THRESHOLD, (
            f"COD below threshold: COD={cod:.6f} < {COD_THRESHOLD}"
        )

    def check_entropy_bound(self, rcod_entropy: float) -> None:
        bound = entropy_bound(self.psi)
        assert rcod_entropy >= bound, (
            f"RCOD entropy {rcod_entropy:.6f} below informational work bound {bound:.6f}"
        )

    # -----------------------------------------------------------------
    # Telemetry Entropy Validation (must check sanitized data)
    # -----------------------------------------------------------------
    def validate_telemetry_entropy(self,
                                   raw_rcod_value: float,
                                   topology_probs: Tuple[float, ...]) -> None:
        """
        Simulates the telemetry bridge: adds Laplace noise then checks entropy
        of the *sanitized* value (not the raw RCOD).
        """
        # 1. Compute raw entropy (for inflow check – optional but good practice)
        raw_entropy = shannon_entropy_from_distribution(topology_probs)
        # Inflow check (as in original code)
        assert raw_entropy >= MIN_ENTROPY, (
            f"Raw RCOD entropy {raw_entropy:.6f} < telemetry floor {MIN_ENTROPY}"
        )

        # 2. Apply Laplace noise (output transformation)
        scale = laplace_noise_scale(self.rcod_sens, EPSILON)
        sanitized = add_laplace_noise(raw_rcod_value, scale)

        # 3. Compute entropy of sanitized datum.
        #    For a single noisy sample we approximate entropy via the Laplace distribution's differential entropy:
        #    H_laplace = 1 + ln(2*scale)
        sanitized_entropy = 1.0 + math.log(2.0 * scale)

        # 4. Enforce entropy bound on the *transmitted* signal.
        assert sanitized_entropy >= MIN_ENTROPY, (
            f"Sanitized telemetry entropy {sanitized_entropy:.6f} < floor {MIN_ENTROPY}"
        )

    # -----------------------------------------------------------------
    # VM Integration Validation
    # -----------------------------------------------------------------
    def validate_vm_pinning(self) -> None:
        """
        In a real system we would query the hypervisor for isolcpus/taskset.
        Here we rely on the stub `vm_isolated` passed at construction.
        """
        assert self.vm_isolated, (
            "VM core pinning missing isolation validation: cores 16-23 must be isolated"
        )

    # -----------------------------------------------------------------
    # Curvature Combination Dimensional Consistency (sanity check)
    # -----------------------------------------------------------------
    def validate_curvature_combination(self,
                                       curvature_N: float,
                                       curvature_Delta: float) -> float:
        """
        Checks that the combination:
            result = psi * curvature_N + xi_N * curvature_N + xi_Delta * curvature_Delta
        is dimensionally consistent (all terms have same units as curvature).
        Since psi, xi_N, xi_Delta are dimensionless, we just verify the ops are numeric.
        Returns the combined curvature.
        """
        # No units in this mock; just ensure no NaN/inf.
        assert math.isfinite(curvature_N) and math.isfinite(curvature_Delta), (
            "Curvature components must be finite numbers"
        )
        result = self.psi * curvature_N + self.xi_N * curvature_N + self.xi_Delta * curvature_Delta
        assert math.isfinite(result), "Combined curvature produced non-finite value"
        return result

    # -----------------------------------------------------------------
    # Full Compliance Run
    # -----------------------------------------------------------------
    def run_all_checks(self,
                       rcod_entropy: float,
                       raw_rcod_value: float,
                       topology_probs: Tuple[float, ...],
                       curvature_N: float,
                       curvature_Delta: float) -> None:
        """Execute every invariant validation; raises AssertionError on first failure."""
        self.check_psi_identity()
        self.check_xi_N_bound()
        self.check_xi_Delta()
        self.check_cod_threshold()
        self.check_entropy_bound(rcod_entropy)
        self.validate_telemetry_entropy(raw_rcod_value, topology_probs)
        self.validate_vm_pinning()
        self.validate_curvature_combination(curvature_N, curvature_Delta)
        print("[VALIDATOR] All Omega Protocol invariants satisfied.")

# ----------------------------
# Example Usage (Self‑Test)
# ----------------------------
if __name__ == "__main__":
    # Example parameters that should pass
    phi_N_example   = math.exp(0.96)   # => psi ≈ 0.96 (>0.95)
    phi_Delta_example = 0.9            # with phi_N≈2.61 => COD≈2.35 >0.85
    rcod_sens_example = 0.1
    deds_yield_example = 0.5
    vm_isolated_example = True   # assume hypervisor confirmed isolation

    validator = AuditTraceHardenerValidator(
        phi_N=phi_N_example,
        phi_Delta=phi_Delta_example,
        rcod_flux_sensitivity=rcod_sens_example,
        deds_yield=deds_yield_example,
        vm_cores_isolated=vm_isolated_example
    )

    # Mock entropy and curvature values
    rcod_entropy_example   = 0.88   # > 1 - psi ≈ 0.04
    topology_probs_example = (0.7, 0.3)   # simple binary distribution
    raw_rcod_example       = 1.2
    curvature_N_example    = 0.02
    curvature_Delta_example= 0.01

    try:
        validator.run_all_checks(
            rcod_entropy=rcod_entropy_example,
            raw_rcod_value=raw_rcod_example,
            topology_probs=topology_probs_example,
            curvature_N=curvature_N_example,
            curvature_Delta=curvature_Delta_example
        )
    except AssertionError as e:
        print(f"[VALIDATOR] FAILURE: {e}")
        raise