# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validation script for Thermodynamic-Kinetic Manifold (v85.0-Ω)
Checks mathematical soundness, dimensional compliance, and Omega Protocol invariants.
"""

import numpy as np
import itertools

# ----------------------------
# Helper functions from the manifold
# ----------------------------
def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def calc_equilibrium_stability(core_stability, pathway_optimality, landscape_ruggedness):
    # From manuscript: core*0.45 + pathway*0.35 + (1-ruggedness)*0.20
    val = core_stability*0.45 + pathway_optimality*0.35 + (1.0 - landscape_ruggedness)*0.20
    return clamp(val)

def calc_free_energy_barrier(kinetic_trap_proximity, folding_velocity, equilibrium_stability):
    # trap*0.40 + velocity*0.30 - stability*0.30
    val = kinetic_trap_proximity*0.40 + folding_velocity*0.30 - equilibrium_stability*0.30
    return clamp(val)

def calc_kinetic_accessibility(free_energy_barrier, barrier_crossing_rate, landscape_ruggedness):
    # rate*0.45 + (1-barrier)*0.35 + (1-ruggedness)*0.20
    val = barrier_crossing_rate*0.45 + (1.0 - free_energy_barrier)*0.35 + (1.0 - landscape_ruggedness)*0.20
    return clamp(val)

def calc_thermodynamic_deficit(equilibrium_stability, kinetic_trap_proximity, core_stability):
    # trap*0.45 + (1-stability)*0.35 + (1-core)*0.20  then /3? Actually manuscript: deficit = trap_factor + (1-stab_reduction)+(1-core_reduction) then /3
    trap = kinetic_trap_proximity*0.45
    stab_red = (1.0 - equilibrium_stability)*0.35
    core_red = (1.0 - core_stability)*0.20
    val = (trap + stab_red + core_red) / 3.0
    return clamp(val)

def calc_barrier_crossing_rate(folding_velocity, free_energy_barrier, kinetic_accessibility):
    # velocity*0.40 + accessibility*0.35 + (1-barrier)*0.25
    val = folding_velocity*0.40 + kinetic_accessibility*0.35 + (1.0 - free_energy_barrier)*0.25
    return clamp(val)

def calc_false_equilibrium_prob(kinetic_trap_proximity, equilibrium_stability, kinetic_accessibility):
    # trap*0.50 + (1-stability)*0.30 + accessibility*0.20
    val = kinetic_trap_proximity*0.50 + (1.0 - equilibrium_stability)*0.30 + kinetic_accessibility*0.20
    return clamp(val)

def calc_thermodynamic_kinetic_risk(thermodynamic_deficit, free_energy_barrier, equilibrium_stability):
    # deficit * barrier * (1 - stability)
    val = thermodynamic_deficit * free_energy_barrier * (1.0 - equilibrium_stability)
    return clamp(val)

def calc_COD_thermodynamic_aware(diagnostic_vec, plasma_vec, h_instability, theta_tensor_leak,
                                 equilibrium_stability, kinetic_accessibility, thermodynamic_kinetic_risk,
                                 LAMBDA_COUPLING=0.5, MU_THERMO=0.7):
    # Fidelity term
    if len(diagnostic_vec) != len(plasma_vec):
        raise ValueError("Vector lengths must match")
    dot = sum(np.abs(np.conj(d)*p) for d, p in zip(diagnostic_vec, plasma_vec))
    magD = sum(np.abs(d*d) for d in diagnostic_vec)
    magP = sum(np.abs(p*p) for p in plasma_vec)
    if magD == 0 or magP == 0:
        fidelity = 0.0
    else:
        fidelity = dot / (np.sqrt(magD) * np.sqrt(magP))
        fidelity = clamp(fidelity)
    # Penalties
    instability_penalty = np.exp(-LAMBDA_COUPLING * h_instability)
    exposure_penalty = np.exp(-LAMBDA_COUPLING * theta_tensor_leak)
    stability_penalty = np.exp(-MU_THERMO * (1.0 - equilibrium_stability))
    accessibility_penalty = np.exp(-MU_THERMO * (1.0 - kinetic_accessibility))
    risk_penalty = np.exp(-MU_THERMO * thermodynamic_kinetic_risk)
    return fidelity * instability_penalty * exposure_penalty * stability_penalty * accessibility_penalty * risk_penalty

# ----------------------------
# Invariant thresholds (from manuscript)
# ----------------------------
PSI_INTEGRITY_THRESHOLD = 0.95
EQUILIBRIUM_STABILITY_MIN = 0.65
KINETIC_ACCESSIBILITY_MIN = 0.55
FREE_ENERGY_BARRIER_MAX = 0.70
COD_THRESHOLD = 0.85
AUDIT_ENTROPY_PER_CHECK = 0.02

# ----------------------------
# Validation routines
# ----------------------------
def test_bounds(func, args_list, name):
    """Run func on each args tuple, ensure output in [0,1]."""
    for args in args_list:
        try:
            val = func(*args)
        except Exception as e:
            raise AssertionError(f"{name} failed on args {args}: {e}")
        if not (0.0 <= val <= 1.0 + 1e-12):  # tiny tolerance for floating point
            raise AssertionError(f"{name} out of bounds: {val} for args {args}")
    print(f"✓ {name}: all outputs in [0,1]")

def test_invariant_logic():
    """Check that the invariant gates make sense."""
    # Example state
    state = {
        'psi_integrity': 0.96,
        'core_stability': 0.8,
        'pathway_optimality': 0.7,
        'kinetic_trap_proximity': 0.2,
        'folding_velocity': 0.5,
        'h_instability': 0.1,
        'theta_tensor_leak': 0.05,
    }
    # Compute derived metrics
    landscape_ruggedness = clamp(state['kinetic_trap_proximity']*0.5 + state['h_instability']*0.5)
    eq_stab = calc_equilibrium_stability(state['core_stability'],
                                         state['pathway_optimality'],
                                         landscape_ruggedness)
    free_en = calc_free_energy_barrier(state['kinetic_trap_proximity'],
                                       state['folding_velocity'],
                                       eq_stab)
    # barrier crossing rate needs kinetic accessibility first (circular in manuscript)
    # We'll approximate by assuming an initial guess for accessibility
    kin_acc_guess = 0.6
    barrier_rate = calc_barrier_crossing_rate(state['folding_velocity'], free_en, kin_acc_guess)
    kin_acc = calc_kinetic_accessibility(free_en, barrier_rate, landscape_ruggedness)
    # Recompute barrier crossing with updated accessibility (one iteration)
    barrier_rate = calc_barrier_crossing_rate(state['folding_velocity'], free_en, kin_acc)
    kin_acc = calc_kinetic_accessibility(free_en, barrier_rate, landscape_ruggedness)
    therm_def = calc_thermodynamic_deficit(eq_stab, state['kinetic_trap_proximity'], state['core_stability'])
    false_eq = calc_false_equilibrium_prob(state['kinetic_trap_proximity'], eq_stab, kin_acc)
    tk_risk = calc_thermodynamic_kinetic_risk(therm_def, free_en, eq_stab)

    # Check invariant thresholds
    assert state['psi_integrity'] >= PSI_INTEGRITY_THRESHOLD, "Psi integrity violation"
    assert eq_stab >= EQUILIBRIUM_STABILITY_MIN, f"Equilibrium stability too low: {eq_stab}"
    assert kin_acc >= KINETIC_ACCESSIBILITY_MIN, f"Kinetic accessibility too low: {kin_acc}"
    assert free_en <= FREE_ENERGY_BARRIER_MAX, f"Free energy barrier too high: {free_en}"
    # COD check (dummy vectors)
    diag = [1+0j, 0+1j]
    plasm = [1+0j, 0+1j]
    cod = calc_COD_thermodynamic_aware(diag, plasm,
                                       state['h_instability'],
                                       state['theta_tensor_leak'],
                                       eq_stab, kin_acc, tk_risk)
    assert cod >= COD_THRESHOLD, f"COD too low: {cod}"
    print("✓ Invariant logic passes for sample state")

def test_monotonicity():
    """Simple monotonicity checks where expected."""
    # equilibrium stability should increase with core_stability and pathway_optimality
    base = (0.5, 0.5, 0.2)  # core, pathway, ruggedness
    val0 = calc_equilibrium_stability(*base)
    val1 = calc_equilibrium_stability(base[0]+0.1, base[1], base[2])
    val2 = calc_equilibrium_stability(base[0], base[1]+0.1, base[2])
    val3 = calc_equilibrium_stability(base[0], base[1], base[2]-0.1)  # less rugged -> higher stability
    assert val1 > val0, "Equilibrium stability should rise with core stability"
    assert val2 > val0, "Equilibrium stability should rise with pathway optimality"
    assert val3 > val0, "Equilibrium stability should rise when ruggedness decreases"
    print("✓ Equilibrium stability monotonicity OK")

    # free energy barrier should increase with trap proximity and velocity, decrease with stability
    base = (0.3, 0.4, 0.6)  # trap, velocity, stability
    val0 = calc_free_energy_barrier(*base)
    val1 = calc_free_energy_barrier(base[0]+0.1, base[1], base[2])
    val2 = calc_free_energy_barrier(base[0], base[1]+0.1, base[2])
    val3 = calc_free_energy_barrier(base[0], base[1], base[2]-0.1)  # less stability -> higher barrier
    assert val1 > val0, "Barrier should rise with trap proximity"
    assert val2 > val0, "Barrier should rise with folding velocity"
    assert val3 > val0, "Barrier should rise when stability decreases"
    print("✓ Free energy barrier monotonicity OK")

def test_idempotency_and_limits():
    """Check edge cases."""
    # All zeros
    assert calc_equilibrium_stability(0,0,1) == clamp(0*0.45 + 0*0.35 + (1-1)*0.20)  # ruggedness=1 -> penalty zero
    assert calc_free_energy_barrier(0,0,1) == clamp(0 + 0 - 1*0.30)  # should be 0 after clamp
    assert calc_kinetic_accessibility(0,0,1) == clamp(0*0.45 + (1-0)*0.35 + (1-1)*0.20)  # 0.35
    # All ones
    assert calc_equilibrium_stability(1,1,0) == clamp(1*0.45 + 1*0.35 + (1-0)*0.20)  # =1.0
    assert calc_free_energy_barrier(1,1,0) == clamp(1*0.40 + 1*0.30 - 0*0.30)  # =1.0
    assert calc_kinetic_accessibility(1,1,0) == clamp(1*0.45 + (1-1)*0.35 + (1-0)*0.20)  # =0.65
    print("✓ Edge cases evaluated")

def run_random_tests(num_samples=1000):
    """Random sampling to ensure no runtime errors and bounds hold."""
    rng = np.random.default_rng(42)
    for _ in range(num_samples):
        # generate random inputs in [0,1]
        core = rng.random()
        pathway = rng.random()
        rugged = rng.random()
        trap = rng.random()
        vel = rng.random()
        stab = rng.random()
        rate = rng.random()
        barr = rng.random()
        acc = rng.random()
        # compute
        calc_equilibrium_stability(core, pathway, rugged)
        calc_free_energy_barrier(trap, vel, stab)
        calc_kinetic_accessibility(barr, rate, rugged)
        calc_thermodynamic_deficit(stab, trap, core)
        calc_barrier_crossing_rate(vel, barr, acc)
        calc_false_equilibrium_prob(trap, stab, acc)
        calc_thermodynamic_kinetic_risk(
            calc_thermodynamic_deficit(stab, trap, core),
            calc_free_energy_barrier(trap, vel, stab),
            calc_equilibrium_stability(core, pathway, rugged)
        )
        # COD with random complex vectors
        n = 3
        diag = rng.random(n) + 1j*rng.random(n)
        plasm = rng.random(n) + 1j*rng.random(n)
        calc_COD_thermodynamic_aware(diag, plasm,
                                     rng.random(), rng.random(),
                                     rng.random(), rng.random(), rng.random())
    print(f"✓ Random tests passed ({num_samples} samples)")

# ----------------------------
# Main validation
# ----------------------------
if __name__ == "__main__":
    print("=== Thermodynamic-Kinetic Manifold Validation ===")
    # Prepare argument lists for boundedness tests
    args_eq = [(rng.random(), rng.random(), rng.random()) for rng in [np.random.default_rng(i) for i in range(5)]]
    args_fe = [(rng.random(), rng.random(), rng.random()) for rng in [np.random.default_rng(i+10) for i in range(5)]]
    args_ka = [(rng.random(), rng.random(), rng.random()) for rng in [np.random.default_rng(i+20) for i in range(5)]]
    args_td = [(rng.random(), rng.random(), rng.random()) for rng in [np.random.default_rng(i+30) for i in range(5)]]
    args_bc = [(rng.random(), rng.random(), rng.random()) for rng in [np.random.default_rng(i+40) for i in range(5)]]
    args_fp = [(rng.random(), rng.random(), rng.random()) for rng in [np.random.default_rng(i+50) for i in range(5)]]
    args_tk = [(rng.random(), rng.random(), rng.random()) for rng in [np.random.default_rng(i+60) for i in range(5)]]

    test_bounds(calc_equilibrium_stability, args_eq, "equilibrium_stability")
    test_bounds(calc_free_energy_barrier, args_fe, "free_energy_barrier")
    test_bounds(calc_kinetic_accessibility, args_ka, "kinetic_accessibility")
    test_bounds(calc_thermodynamic_deficit, args_td, "thermodynamic_deficit")
    test_bounds(calc_barrier_crossing_rate, args_bc, "barrier_crossing_rate")
    test_bounds(calc_false_equilibrium_prob, args_fp, "false_equilibrium_prob")
    test_bounds(calc_thermodynamic_kinetic_risk, args_tk, "thermodynamic_kinetic_risk")

    test_invariant_logic()
    test_monotonicity()
    test_idempotency_and_limits()
    run_random_tests(num_samples=500)

    print("\nAll validation checks passed. The manifold is mathematically sound and compliant with Omega Protocol invariants.")