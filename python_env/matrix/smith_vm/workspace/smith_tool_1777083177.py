# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import random
from typing import Tuple, List

# ======================
# Constants (matching C++)
# ======================
COD_THRESHOLD = 0.85
COD_FLOOR = 0.39
PSI_INTEGRITY_THRESHOLD = 0.95
CORRELATION_LENGTH_THRESHOLD = 0.70
SHEAR_FLOW_MIN = 0.50
TENSOR_LEAK_MAX = 0.50
STIFFNESS_MAX_DELTA = 0.10
PHI_DELTA_MAX = 0.50
B1_HOMOLOGY_MAX = 0.80

LAMBDA_COUPLING = 0.5
KAPPA_CONFINEMENT = 0.5
ETA_TENSOR_LEAK = 0.3
MU_CORRELATION = 0.4

AUDIT_ENTROPY_PER_CHECK = 0.02
AUDIT_CHECKS = 9  # hardcoded in the C++ Operate method

DENSITY_GRADIENT_EXPONENT = 0.5
BETA_EXPONENT = 0.3
SHEAR_EXPONENT = 0.7

# ======================
# Helper functions
# ======================
def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def fidelity(diag: List[complex], plasma: List[complex]) -> float:
    """Compute diagnostic-plasma alignment fidelity (C++ version)."""
    size = min(len(diag), len(plasma))
    if size == 0:
        return 0.0
    dot = 0.0
    magD = 0.0
    magP = 0.0
    for i in range(size):
        dot += abs(diag[i].conjugate() * plasma[i])
        magD += abs(diag[i]) ** 2
        magP += abs(plasma[i]) ** 2
    if magD == 0.0 or magP == 0.0:
        return 0.0
    f = dot / (math.sqrt(magD) * math.sqrt(magP))
    return clamp(f, 0.0, 1.0)

def instability_penalty(h_inst: float) -> float:
    return math.exp(-LAMBDA_COUPLING * h_inst)

def confinement_penalty(xi_conf: float) -> float:
    return math.exp(-KAPPA_CONFINEMENT * xi_conf)

def exposure_penalty(theta_leak: float) -> float:
    return math.exp(-ETA_TENSOR_LEAK * theta_leak)

def correlation_penalty(corr_mean: float) -> float:
    return math.exp(-MU_CORRELATION * (1.0 - corr_mean))

def calculate_COD(diag: List[complex], plasma: List[complex],
                  h_inst: float, xi_conf: float, theta_leak: float,
                  corr_par: float, corr_perp: float) -> float:
    fid = fidelity(diag, plasma)
    corr_mean = (corr_par + corr_perp) / 2.0
    return (fid *
            instability_penalty(h_inst) *
            confinement_penalty(xi_conf) *
            exposure_penalty(theta_leak) *
            correlation_penalty(corr_mean))

def correlation_length_calc(density_grad: float, collisionality: float,
                            beta: float, shear: float) -> float:
    gf = density_grad ** DENSITY_GRADIENT_EXPONENT
    bf = beta ** BETA_EXPONENT
    sf = shear ** SHEAR_EXPONENT
    damp = math.exp(-0.5 * collisionality)
    raw = gf * bf * sf * damp
    return clamp(raw, 0.0, 1.0)

def LH_proximity(corr_len: float, shear: float) -> float:
    if shear < SHEAR_FLOW_MIN:
        return 0.0
    prox = (corr_len - 0.5) / 0.5
    return clamp(prox, 0.0, 1.0)

def shear_flow_modulation(state: dict, dt_hours: float) -> dict:
    """Apply one step of the ShearFlowModulationOperator (simplified)."""
    GAMMA = 0.005
    SHEAR_GAMMA = 0.003

    # Unpack
    xi_conf = state['xi_confinement']
    z_depth = state['z_plasma_depth']
    theta_leak = state['theta_tensor_leak']
    shear = state['shear_flow_strength']
    h_inst = state['h_instability']
    beta = state['beta_parameter']

    # Adiabatic modulation of confinement stiffness
    exp_term = math.exp(-GAMMA * dt_hours)
    new_xi_conf = xi_conf * exp_term + z_depth * (1.0 - exp_term)

    # Reduce exposure
    new_theta_leak = max(0.0, theta_leak * exp_term)

    # Shear flow buildup (using l_h_proximity as target)
    l_h_prox = state['l_h_proximity']
    shear_exp = math.exp(-SHEAR_GAMMA * dt_hours)
    new_shear = shear * shear_exp + l_h_prox * (1.0 - shear_exp)

    # Recalc correlation lengths (using placeholder gradients)
    calc_len_par = correlation_length_calc(0.7, h_inst, beta, new_shear)
    calc_len_perp = correlation_length_calc(0.6, h_inst, beta, new_shear)

    # Update L‑H proximity
    new_l_h_prox = LH_proximity((calc_len_par + calc_len_perp) / 2.0, new_shear)

    # Recalc COD (diagnostic vectors omitted -> assume unit fidelity for test)
    dummy_diag = [1.0+0j]
    dummy_plasma = [1.0+0j]
    new_cod = calculate_COD(dummy_diag, dummy_plasma,
                            h_inst, new_xi_conf, new_theta_leak,
                            calc_len_par, calc_len_perp)

    # Update state
    state.update({
        'xi_confinement': new_xi_conf,
        'theta_tensor_leak': new_theta_leak,
        'shear_flow_strength': new_shear,
        'l_h_proximity': new_l_h_prox,
        'correlation_length_parallel': calc_len_par,
        'correlation_length_perp': calc_len_perp,
        'cod': new_cod,
        'phi_N': new_cod  # as in C++
    })
    return state

def invariant_check(state: dict, cod: float) -> Tuple[bool, dict]:
    """Return (all_passed, dict of individual checks)."""
    phi_N = state['phi_N']
    xi_conf = state['xi_confinement']
    z_depth = state['z_plasma_depth']
    theta_leak = state['theta_tensor_leak']
    h_inst = state['h_instability']
    shear = state['shear_flow_strength']
    b1_homology = state['b1_homology']

    # phi_delta (as in C++)
    phi_delta = phi_N * math.tanh((xi_conf - z_depth) / 3.0)

    checks = {
        'cod_ok': cod >= COD_THRESHOLD,
        'phi_floor_ok': phi_N >= COD_FLOOR,
        'correlation_ok': ((state['correlation_length_parallel'] +
                            state['correlation_length_perp']) / 2.0) >= CORRELATION_LENGTH_THRESHOLD,
        'shear_flow_ok': shear >= SHEAR_FLOW_MIN,
        'stiffness_match_ok': xi_conf <= z_depth + STIFFNESS_MAX_DELTA,
        'env_cap_ok': theta_leak <= TENSOR_LEAK_MAX,
        'dissonance_ok': True,  # placeholder
        'asymmetry_ok': phi_delta < PHI_DELTA_MAX * phi_N,
        'homology_ok': b1_homology <= B1_HOMOLOGY_MAX,
        'audit_tracked': True
    }
    all_passed = all(checks.values())
    return all_passed, checks

def silence_protocol_action(state: dict, cod: float, corr_mean: float) -> str:
    """Replicate the C++ SilenceProtocol::Decide."""
    if state['psi_integrity'] < PSI_INTEGRITY_THRESHOLD:
        return "HALT_EXPERIMENT"
    if corr_mean < CORRELATION_LENGTH_THRESHOLD:
        if state['shear_flow_strength'] > SHEAR_FLOW_MIN:
            return "AWAIT_LH_TRANSITION"
        return "FREEZE_CONFIG"
    if cod < COD_THRESHOLD:
        return "FREEZE_CONFIG"
    return "PROCEED"

def phi_density_ledger(cod_before: float, cod_after: float,
                       audit_checks: int = AUDIT_CHECKS) -> float:
    raw_gain = cod_after - cod_before
    audit_cost = audit_checks * AUDIT_ENTROPY_PER_CHECK
    return raw_gain - audit_cost

# ======================
# Test harness
# ======================
def run_validation(trials: int = 1000):
    random.seed(42)
    for t in range(trials):
        # Random state within [0,1] (except where noted)
        state = {
            'config_path': '',
            'thresholds': [],
            'xi_confinement': random.random(),
            'z_plasma_depth': random.random(),
            'theta_tensor_leak': random.random(),
            'h_instability': random.random(),
            'psi_integrity': random.random(),
            'q_factor': random.random(),
            'beta_parameter': random.random(),
            # correlation & shear placeholders (will be overwritten)
            'correlation_length_parallel': random.random(),
            'correlation_length_perp': random.random(),
            'shear_flow_strength': random.random(),
            'l_h_proximity': random.random(),
            'cod': 0.0,
            'phi_N': 0.0,
            'b1_homology': random.random()
        }

        # Compute initial COD (dummy diag/plasma vectors)
        dummy_diag = [complex(random.random(), random.random()) for _ in range(5)]
        dummy_plasma = [complex(random.random(), random.random()) for _ in range(5)]
        state['cod'] = calculate_COD(dummy_diag, dummy_plasma,
                                     state['h_instability'],
                                     state['xi_confinement'],
                                     state['theta_tensor_leak'],
                                     state['correlation_length_parallel'],
                                     state['correlation_length_perp'])
        state['phi_N'] = state['cod']

        # Evaluate invariants
        all_passed, checks = invariant_check(state, state['cod'])
        corr_mean = (state['correlation_length_parallel'] +
                     state['correlation_length_perp']) / 2.0

        # Silence protocol decision
        action = silence_protocol_action(state, state['cod'], corr_mean)

        # If protocol says PROCEED, all invariants must pass
        if action == "PROCEED":
            assert all_passed, (
                f"Trial {t}: PROCEED but invariants failed: {checks}\n"
                f"State: {state}"
            )
        # Optional: print occasional successes
        if t % 200 == 0 and action == "PROCEED":
            print(f"Trial {t}: PROCEED ✓ | COD={state['cod']:.3f}, "
                  f"corr={corr_mean:.3f}, ψ_int={state['psi_integrity']:.3f}")

    print(f"Validation complete: {trials} random states processed. "
          f"No PROCEED violations found.")

if __name__ == "__main__":
    run_validation()