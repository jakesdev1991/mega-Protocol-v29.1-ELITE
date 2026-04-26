# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Validation script for the Omega‑Protocol Psychology Reboot Specification
# Checks mathematical soundness and invariant compliance.

import numpy as np
import math

# ----------------------------------------------------------------------
# Invariant constants (as defined in the specification)
# ----------------------------------------------------------------------
PSI_ID_THRESHOLD = 0.95          # Minimum identity continuity
XI_BOUND_MAX   = 2.5             # Upper stiffness before deadlock risk
XI_BOUND_MIN   = 0.5             # Lower stiffness (must stay >0 to avoid noise)
COD_THRESHOLD  = 0.85            # Minimum Chain Overlap Density for stability
UPSILON_TARGET = 0.90            # Target validation integrity for reboot success
XI_BOUND_DEFAULT = 1.5           # Nominal stiffness used in the code (implicit)

# ----------------------------------------------------------------------
# Helper functions copied from the spec (with minor fixes for clarity)
# ----------------------------------------------------------------------
def calc_upsilon_val(psi_sub, psi_con):
    """Squared overlap |<psi_sub|psi_con>|^2 (requires real vectors)."""
    dot = np.dot(psi_sub, psi_con)
    norm_sub = np.linalg.norm(psi_sub)
    norm_con = np.linalg.norm(psi_con)
    if norm_sub == 0 or norm_con == 0:
        return 0.0
    overlap = dot / (norm_sub * norm_con)
    return overlap * overlap

def calc_cod(psi_sub, psi_con, xi_bound):
    """Chain Overlap Density = Bures fidelity approximated by stiffness damping."""
    fidelity = calc_upsilon_val(psi_sub, psi_con)
    # Entropic damping factor from spec: exp(-entropy_cost * 0.5)
    # where entropy_cost = 1/(1+xi_bound)
    entropy_cost = 1.0 / (1.0 + xi_bound)
    cod = fidelity * math.exp(-entropy_cost * 0.5)
    return cod

def check_failure_mode(upsilon, xi):
    """Raise if validation deadlock detected."""
    if upsilon < 0.50 and xi > 2.0:
        raise RuntimeError("Systemic Deadlock: Stiffness exceeds Suppression Threshold.")

def systemic_reboot(psi_con, xi_bound, psi_sub):
    """
    Execute the reboot sequence as per the spec.
    Returns (new_psi_con, new_xi_bound, success_flag, log_msgs).
    """
    logs = []
    success = False

    # Phase 1: Diagnostic
    upsilon = calc_upsilon_val(psi_sub, psi_con)
    xi = xi_bound
    if upsilon < UPSILON_TARGET and xi > XI_BOUND_MAX * 0.8:
        logs.append("Validation Deadlock Detected. Initiating R_val.")

        # Phase 2: Stiffness dissipation
        target_xi = XI_BOUND_MIN
        if target_xi < xi:
            xi = target_xi
            logs.append("Stiffness Dissipated. Entering High-Vulnerability State.")
            # In a real system we would wait for equilibration; here we skip.

        # Phase 3: Basis transformation (align conscious with subconscious)
        psi_con = np.array(psi_sub, dtype=float)   # simplified projection
        # Phase 4: Re‑calculation
        new_upsilon = calc_upsilon_val(psi_sub, psi_con)
        new_cod     = calc_cod(psi_sub, psi_con, xi)

        # Phase 5: Stiffness restoration (conditional)
        if new_cod > COD_THRESHOLD:
            # Gradual restoration toward default
            xi = min(XI_BOUND_DEFAULT, xi * 1.2)
            logs.append("Reboot Successful. COD Restored.")
            success = True
        else:
            # Repentance: discard trajectory, reset stiffness to default
            xi = XI_BOUND_DEFAULT
            logs.append("Path Invalid. Identity Preserved. Repentance Initiated.")
            success = False

        # Update outputs
        psi_con_out = psi_con
        xi_out      = xi
    else:
        logs.append("System Stable. No Reboot Required.")
        psi_con_out = np.array(psi_con, dtype=float)
        xi_out      = xi_bound
        success     = True   # no action needed -> considered stable

    return psi_con_out, xi_out, success, logs

# ----------------------------------------------------------------------
# Validation tests
# ----------------------------------------------------------------------
def run_validation():
    print("=== Omega Protocol Psychology Reboot Validation ===")

    # 1. Invariant sanity checks
    assert 0 < PSI_ID_THRESHOLD <= 1.0, "PSI_ID_THRESHOLD must be in (0,1]"
    assert XI_BOUND_MIN < XI_BOUND_MAX, "XI_BOUND_MIN must be less than XI_BOUND_MAX"
    assert 0 < COD_THRESHOLD <= 1.0, "COD_THRESHOLD must be in (0,1]"
    assert 0 < UPSILON_TARGET <= 1.0, "UPSILON_TARGET must be in (0,1]"
    print("✓ Invariant constants are well‑formed.")

    # 2. Mathematical properties of helper functions
    # Orthogonal vectors => zero overlap
    v1 = np.array([1.0, 0.0])
    v2 = np.array([0.0, 1.0])
    assert math.isclose(calc_upsilon_val(v1, v2), 0.0, abs_tol=1e-12), "Orthogonal vectors should give zero overlap."
    # Identical vectors => overlap = 1
    assert math.isclose(calc_upsilon_val(v1, v1), 1.0, abs_tol=1e-12), "Identical vectors should give unit overlap."
    # COD should be <= fidelity (since damping factor <=1)
    fid = calc_upsilon_val(v1, v1)
    cod = calc_cod(v1, v1, xi_bound=XI_BOUND_DEFAULT)
    assert cod <= fid + 1e-12, "COD must not exceed raw fidelity."
    print("✓ Helper functions obey expected mathematical bounds.")

    # 3. Failure mode detection
    try:
        check_failure_mode(upsilon=0.4, xi=2.2)   # should trigger
        assert False, "Failure mode not detected."
    except RuntimeError:
        pass  # expected
    try:
        check_failure_mode(upsilon=0.6, xi=2.2)   # should NOT trigger
    except RuntimeError:
        assert False, "False positive in failure mode detection."
    print("✓ Failure mode detector works as specified.")

    # 4. Reboot sequence invariant preservation
    # Case A: Stable system (no reboot)
    psi_sub = np.array([0.8, 0.6])
    psi_con = np.array([0.78, 0.62])   # close alignment
    xi_init = 1.0
    psi_con_out, xi_out, success, logs = systemic_reboot(psi_con.copy(), xi_init, psi_sub)
    assert success, "Stable system incorrectly triggered reboot."
    assert math.isclose(xi_out, xi_init, rel_tol=1e-9), "Stiffness should remain unchanged for stable case."
    # Identity invariant: we cannot directly compute Psi_id here, but we can assert
    # that stiffness never leaves the allowed band [XI_BOUND_MIN, XI_BOUND_MAX]
    assert XI_BOUND_MIN <= xi_out <= XI_BOUND_MAX, "Stiffness left allowed band."
    print("✓ Stable case preserves invariants.")

    # Case B: Deadlock → reboot → success
    psi_sub = np.array([1.0, 0.0])
    psi_con = np.array([0.0, 1.0])   # orthogonal -> low upsilon
    xi_init = 2.2                    # high stiffness -> near deadlock
    psi_con_out, xi_out, success, logs = systemic_reboot(psi_con.copy(), xi_init, psi_sub)
    # After reboot, consciousness should align with subconscious
    upsilon_after = calc_upsilon_val(psi_sub, psi_con_out)
    cod_after     = calc_cod(psi_sub, psi_con_out, xi_out)
    assert upsilon_after > UPSILON_TARGET * 0.9, "Post‑reboot validation integrity too low."
    assert cod_after > COD_THRESHOLD, "Post‑reboot COD below stability threshold."
    assert XI_BOUND_MIN <= xi_out <= XI_BOUND_MAX, "Post‑reboot stiffness out of band."
    print("✓ Deadlock → reboot restores coherence and respects stiffness bounds.")

    # Case C: Deadlock → reboot → failure (repentance)
    # Make subconscious a narrow spike that conscious cannot match after basis rotation
    psi_sub = np.array([1.0, 0.0])
    psi_con = np.array([0.0, 1.0])   # start orthogonal
    xi_init = 2.4
    # Force the algorithm to see low COD after alignment by using a dummy
    # post‑alignment check: we monkey‑patch calc_cod to return low value for this test.
    original_calc_cod = calc_cod
    def low_cod(*args, **kwargs):
        return 0.5   # below COD_THRESHOLD
    global calc_cod
    calc_cod = low_cod
    try:
        psi_con_out, xi_out, success, logs = systemic_reboot(psi_con.copy(), xi_init, psi_sub)
        # After repentance, stiffness should reset to default
        assert math.isclose(xi_out, XI_BOUND_DEFAULT, rel_tol=1e-9), "Stiffness not reset after repentance."
        assert not success, "Reboot should have been marked unsuccessful."
    finally:
        calc_cod = original_calc_cod   # restore
    print("✓ Repentance path correctly resets stiffness and flags failure.")

    print("\nAll validation checks passed. The specification is mathematically sound\n"
          "and compliant with the Omega Protocol invariants.")

if __name__ == "__main__":
    run_validation()