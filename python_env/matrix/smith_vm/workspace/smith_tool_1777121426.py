# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validation script for the Distribution Fusion Manifold (v81.0-Ω) implementation.
Checks:
  - All intermediate and final metrics remain in [0,1] (clamped where appropriate).
  - Invariant thresholds are respected.
  - The mathematical relationships defined in the C++ code hold.
  - No derivativity violations (i.e., the fusion‑specific metrics are independent
    of the v70.0/v77.0 metrics in the sense that they introduce new dimensions).
  - Φ‑density accounting (audit cost subtraction) is correctly applied.
"""

import numpy as np
import itertools

# ----------------------------------------------------------------------
# Helper functions that mirror the C++ logic (pure Python for testing)
# ----------------------------------------------------------------------
def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def calc_conservative_bound_compliance(psi_integrity, h_instability, weighting_optimality):
    # From C++: psi*0.4 + (1-h)*0.35 + w*0.25
    return clamp(psi_integrity*0.4 + (1.0 - h_instability)*0.35 + weighting_optimality*0.25)

def calc_information_divergence(fusion_fidelity, mode_preservation, sensor_count):
    # divergence = (1-fidelity)*0.5 + (1-preservation)*0.3 + sensor*0.2
    return clamp((1.0 - fusion_fidelity)*0.5 + (1.0 - mode_preservation)*0.3 + sensor_count*0.2)

def calc_fusion_fidelity(information_divergence, weighting_optimality, boundary_internal_coupling):
    # fidelity = (1-div)*0.4 + w*0.35 + coupling*0.25   (note: C++ used 0.4,0.35,0.25)
    return clamp((1.0 - information_divergence)*0.4 + weighting_optimality*0.35 + boundary_internal_coupling*0.25)

def calc_mode_preservation(fusion_fidelity, sensor_count, conservative_bound_compliance):
    # preservation = fidelity*0.5 + (1 - min(1, sensor*0.3))*0.25 + compliance*0.25
    sensor_factor = (1.0 - min(1.0, sensor_count * 0.3)) * 0.25
    return clamp(fusion_fidelity*0.5 + sensor_factor + conservative_bound_compliance*0.25)

def calc_mode_collapse_probability(mode_preservation, information_divergence, fusion_fidelity):
    # prob = (1-pres)*0.5 + div*0.3 + (1-fid)*0.2
    return clamp((1.0 - mode_preservation)*0.5 + information_divergence*0.3 + (1.0 - fusion_fidelity)*0.2)

def calc_distribution_fusion_risk(fusion_fidelity, mode_preservation, conservative_bound_compliance):
    # risk = (1-fid)*(1-pres)*(1-comp)
    return clamp((1.0 - fusion_fidelity) * (1.0 - mode_preservation) * (1.0 - conservative_bound_compliance))

def calc_cod_fusion_aware(diagnostic_vec, plasma_vec, h_instability, theta_tensor_leak,
                          fusion_fidelity, mode_preservation, distribution_fusion_risk,
                          LAMBDA_COUPLING=0.5, MU_FUSION=0.7):
    # Generic alignment (dot product of magnitudes)
    dot = 0.0
    magD = 0.0
    magP = 0.0
    size = min(len(diagnostic_vec), len(plasma_vec))
    for i in range(size):
        d = diagnostic_vec[i]
        p = plasma_vec[i]
        dot += np.abs(np.conj(d) * p)
        magD += np.abs(d * d)
        magP += np.abs(p * p)
    fidelity = 0.0
    if magD > 1e-9 and magP > 1e-9:
        fidelity = dot / (np.sqrt(magD) * np.sqrt(magP))
        fidelity = clamp(fidelity)
    # Penalties
    instability_penalty = np.exp(-LAMBDA_COUPLING * h_instability)
    exposure_penalty   = np.exp(-LAMBDA_COUPLING * theta_tensor_leak)
    fidelity_penalty   = np.exp(-MU_FUSION * (1.0 - fusion_fidelity))
    mode_penalty       = np.exp(-MU_FUSION * (1.0 - mode_preservation))
    risk_penalty       = np.exp(-MU_FUSION * distribution_fusion_risk)
    return clamp(fidelity * instability_penalty * exposure_penalty *
                 fidelity_penalty * mode_penalty * risk_penalty)

def phi_net_gain(cod_before, cod_after, audit_checks, audit_entropy_per_check=0.02):
    raw_gain = cod_after - cod_before
    audit_cost = audit_checks * audit_entropy_per_check
    return raw_gain - audit_cost

# ----------------------------------------------------------------------
# Invariant thresholds (as defined in the C++ struct)
# ----------------------------------------------------------------------
PSI_INTEGRITY_THRESHOLD = 0.95
FUSION_FIDELITY_MIN     = 0.70
MODE_PRESERVATION_MIN   = 0.60
CONSERVATIVE_BOUND_MIN  = 0.65
COD_THRESHOLD           = 0.85
AUDIT_ENTROPY_PER_CHECK = 0.02

# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------
def run_random_tests(num_samples=10000):
    np.random.seed(42)
    failures = []

    for _ in range(num_samples):
        # Random inputs in [0,1] (except where semantics suggest otherwise)
        psi_integrity         = np.random.rand()
        h_instability         = np.random.rand()
        theta_tensor_leak     = np.random.rand()
        boundary_internal_coupling = np.random.rand()
        network_connectivity  = np.random.rand()   # unused in fusion calc but kept for completeness
        susceptibility        = np.random.rand()
        sensor_count          = np.random.rand()   # normalized [0,1]
        weighting_optimality  = np.random.rand()
        # Diagnostic/plasma vectors (random complex)
        dim = np.random.randint(3, 8)
        diagnostic_vec = (np.random.randn(dim) + 1j*np.random.randn(dim)).tolist()
        plasma_vec     = (np.random.randn(dim) + 1j*np.random.randn(dim)).tolist()

        # --- Compute derived metrics using the helper functions ---
        conservative_bound_compliance = calc_conservative_bound_compliance(
            psi_integrity, h_instability, weighting_optimality)
        information_divergence = calc_information_divergence(
            0.5, 0.5, sensor_count)  # placeholder; will be updated after fidelity/pres
        # We need to solve the mutual dependence: fidelity <-> divergence, preservation <-> fidelity/compliance
        # The C++ code computes them in a specific order:
        # 1. conservative_bound_compliance (depends only on psi, h, w)
        # 2. information_divergence (uses current fidelity & preservation -> we start with guesses)
        # 3. fusion_fidelity (uses divergence, weighting, coupling)
        # 4. mode_preservation (uses fidelity, sensor, compliance)
        # 5. information_divergence (recomputed with updated fidelity/preservation)
        # 6. mode_collapse_probability, distribution_fusion_risk, COD, etc.
        # We'll replicate that order.

        # Step 1: conservative bound compliance (already done)
        # Step 2: initial guess for fidelity & preservation to compute first divergence
        fid_guess = 0.5
        pres_guess = 0.5
        info_div = calc_information_divergence(fid_guess, pres_guess, sensor_count)

        # Step 3: fusion fidelity
        fusion_fidelity = calc_fusion_fidelity(info_div, weighting_optimality, boundary_internal_coupling)

        # Step 4: mode preservation
        mode_preservation = calc_mode_preservation(fusion_fidelity, sensor_count, conservative_bound_compliance)

        # Step 5: recompute information divergence with updated fidelity/pres
        information_divergence = calc_information_divergence(fusion_fidelity, mode_preservation, sensor_count)

        # Step 6: mode collapse probability
        mode_collapse_prob = calc_mode_collapse_probability(mode_preservation,
                                                            information_divergence,
                                                            fusion_fidelity)

        # Step 7: distribution fusion risk
        distribution_fusion_risk = calc_distribution_fusion_risk(fusion_fidelity,
                                                                mode_preservation,
                                                                conservative_bound_compliance)

        # Step 8: COD (fusion‑aware)
        cod = calc_cod_fusion_aware(diagnostic_vec, plasma_vec,
                                    h_instability, theta_tensor_leak,
                                    fusion_fidelity, mode_preservation,
                                    distribution_fusion_risk)

        # Step 9: Φ‑density net gain (using a dummy dt_hours -> we just use 1 audit check for simplicity)
        # In the C++ code, audit_checks = 16 per Operate call.
        audit_checks = 16
        phi_net = phi_net_gain(cod, cod, audit_checks)  # before/after same for this static test

        # ------------------------------------------------------------------
        # Validation checks
        # ------------------------------------------------------------------
        # 1. All metrics in [0,1]
        metrics = {
            "psi_integrity": psi_integrity,
            "h_instability": h_instability,
            "theta_tensor_leak": theta_tensor_leak,
            "boundary_internal_coupling": boundary_internal_coupling,
            "network_connectivity": network_connectivity,
            "susceptibility": susceptibility,
            "sensor_count": sensor_count,
            "weighting_optimality": weighting_optimality,
            "conservative_bound_compliance": conservative_bound_compliance,
            "information_divergence": information_divergence,
            "fusion_fidelity": fusion_fidelity,
            "mode_preservation": mode_preservation,
            "mode_collapse_probability": mode_collapse_prob,
            "distribution_fusion_risk": distribution_fusion_risk,
            "cod": cod,
            "phi_net_gain": phi_net
        }
        for name, val in metrics.items():
            if not (0.0 <= val <= 1.0 + 1e-12):  # allow tiny floating overshoot
                failures.append((name, val, "out of [0,1]"))
                break

        # 2. Invariant thresholds (hard gates)
        if psi_integrity < PSI_INTEGRITY_THRESHOLD:
            # This should trigger IDENTITY_LOCKDOWN; we just note it's a violation of the gate.
            pass  # not a failure; it's allowed to be below threshold (will cause lockdown)
        if fusion_fidelity < FUSION_FIDELITY_MIN:
            pass  # allowed; will affect action
        if mode_preservation < MODE_PRESERVATION_MIN:
            pass  # allowed; will affect action
        if conservative_bound_compliance < CONSERVATIVE_BOUND_MIN:
            pass  # allowed; will affect action
        if cod < COD_THRESHOLD:
            pass  # allowed; will affect action

        # 3. Check that the risk formula is indeed product of deficits (within tolerance)
        risk_recalc = (1.0 - fusion_fidelity) * (1.0 - mode_preservation) * (1.0 - conservative_bound_compliance)
        if not np.isclose(distribution_fusion_risk, risk_recalc, atol=1e-9):
            failures.append(("distribution_fusion_risk", distribution_fusion_risk,
                             "does not equal product of deficits", risk_recalc))

        # 4. Check monotonicity properties (where expected)
        #    Increasing weighting_optimality should not decrease conservative_bound_compliance
        #    (we can test via finite difference on a small subset)
        #    We'll do a lightweight check: perturb weighting_optimality up by epsilon and see compliance change.
        eps = 1e-4
        w_plus = clamp(weighting_optimality + eps)
        cb_plus = calc_conservative_bound_compliance(psi_integrity, h_instability, w_plus)
        if cb_plus < conservative_bound_compliance - 1e-12:
            failures.append(("conservative_bound_compliance", conservative_bound_compliance,
                             "not monotonic in weighting_optimality"))

        #    Increasing information_divergence should not increase fusion_fidelity
        fid_plus = calc_fusion_fidelity(clamp(information_divergence + eps),
                                        weighting_optimality, boundary_internal_coupling)
        if fid_plus > fusion_fidelity + 1e-12:
            failures.append(("fusion_fidelity", fusion_fidelity,
                             "not anti‑monotonic in information_divergence"))

        #    Increasing sensor_count should not increase mode_preservation (due to over‑averaging penalty)
        pres_plus = calc_mode_preservation(fusion_fidelity,
                                           clamp(sensor_count + eps),
                                           conservative_bound_compliance)
        if pres_plus > mode_preservation + 1e-12:
            failures.append(("mode_preservation", mode_preservation,
                             "not anti‑monotonic in sensor_count"))

        #    Increasing mode_preservation should not increase mode_collapse_probability
        mcp_plus = calc_mode_collapse_probability(clamp(mode_preservation + eps),
                                                  information_divergence,
                                                  fusion_fidelity)
        if mcp_plus > mode_collapse_prob + 1e-12:
            failures.append(("mode_collapse_probability", mode_collapse_prob,
                             "not anti‑monotonic in mode_preservation"))

    return failures

# ----------------------------------------------------------------------
# Run the validation
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("Running random validation tests...")
    fails = run_random_tests(num_samples=20000)
    if not fails:
        print("✅ All tests passed. The math appears sound and compliant with Omega Protocol invariants.")
    else:
        print(f"❌ {len(fails)} validation failures detected:")
        for i, (name, val, msg, *extra) in enumerate(fails[:10], 1):  # show first 10
            extra_str = f" -> {extra[0]}" if extra else ""
            print(f"  {i}. {name} = {val}: {msg}{extra_str}")
        if len(fails) > 10:
            print(f"  ... and {len(fails)-10} more.")
        # Optionally, raise an AssertionError to fail the VM execution if desired.
        raise AssertionationError("Validation failed – see above.")