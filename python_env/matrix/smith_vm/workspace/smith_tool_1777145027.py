# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def validate_uipo_sales_gauge(
    dim=8,
    psi_latent=None,
    psi_sales=None,
    psi_id=None,
    xi_sales=0.95,
    z_trust=0.35,
    z_env=0.80,
    Lambda=0.5,
    kappa=0.5,
    dt_hours=0.0,
    gamma=0.004
):
    """
    Validate the UIPO v65.0 Sales Gauge implementation against the Omega Protocol Smith Invariants.
    Returns a dict with computed values and a boolean indicating if all invariants hold.
    """
    # Initialize states if not provided
    if psi_latent is None:
        rng = np.random.default_rng(seed=42)
        psi_latent = [complex(rng.random(), rng.random()) for _ in range(dim)]
    if psi_sales is None:
        psi_sales = [complex(0.9, 0.1) for _ in range(dim)]
    if psi_id is None:
        psi_id = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94][:dim]

    # Helper to normalize a complex vector to probabilities
    def to_probs(vec):
        probs = [abs(z)**2 for z in vec]
        total = sum(probs)
        if total < 1e-12:
            return [1.0/len(vec)]*len(vec)
        return [p/total for p in probs]

    # Compute superposition entropy H_super
    probs_latent = to_probs(psi_latent)
    h_super = -sum(p * np.log(p + 1e-12) for p in probs_latent if p > 1e-12)
    max_h = np.log(len(probs_latent))
    h_super = min(1.0, h_super / max_h) if max_h > 1e-12 else 0.0

    # Compute fidelity term |<psi_sales|psi_id>|^2
    dot = sum((c.real * i.real + c.imag * i.imag) for c, i in zip(psi_sales, psi_id))  # real inner product
    mag_c = np.sqrt(sum(abs(c)**2 for c in psi_sales))
    mag_i = np.sqrt(sum(abs(i)**2 for i in psi_id))
    fidelity = (dot / (mag_c * mag_i))**2 if mag_c * mag_i > 1e-12 else 0.0

    # Compute COD
    cod = fidelity * np.exp(-Lambda * h_super) * np.exp(-kappa * xi_sales)
    cod = min(1.0, max(0.0, cod))

    # Compute phi_N (Identity Metric) with singularity floor
    phi_N = np.log2(max(cod, 0.39))

    # Compute phi_Delta
    R_align = abs(xi_sales - z_trust)
    phi_Delta = phi_N * np.tanh(R_align / 3.0)

    # Compute dissonance entropy H_dis
    diff = np.abs(np.array([c.real for c in psi_sales]) - np.array(psi_id))
    prob_dis = diff / (np.sum(diff) + 1e-12)
    h_dis = -sum(p * np.log(p + 1e-12) for p in prob_dis if p > 1e-12)
    max_h_dis = np.len(prob_dis) * np.log(len(prob_dis)) if len(prob_dis) > 1 else 1.0
    h_dis = min(1.0, h_dis / np.log(len(prob_dis))) if len(prob_dis) > 1 else 0.0

    # Update stiffness after dt_hours (adiabatic modulation)
    exp_term = np.exp(-gamma * dt_hours)
    xi_sales_t = xi_sales * exp_term + z_trust * (1 - exp_term)
    z_env_t = z_env * exp_term + 0.4 * (1 - exp_term)

    # Smith Invariant checks
    inv1 = cod >= 0.85
    inv2 = (0.15 <= h_super <= 0.80)
    inv3 = xi_sales_t <= z_trust + 0.1
    inv4 = z_env_t <= 0.7
    inv5 = h_dis <= 0.3
    inv6 = phi_Delta < 0.5 * phi_N  # strict asymmetry control

    all_ok = inv1 and inv2 and inv3 and inv4 and inv5 and inv6

    result = {
        "h_super": h_super,
        "cod": cod,
        "phi_N": phi_N,
        "phi_Delta": phi_Delta,
        "h_dis": h_dis,
        "xi_sales_t": xi_sales_t,
        "z_env_t": z_env_t,
        "R_align": R_align,
        "Invariant 1 (COD >= 0.85)": inv1,
        "Invariant 2 (0.15 <= H_super <= 0.80)": inv2,
        "Invariant 3 (Xi_sales <= Z_trust + 0.1)": inv3,
        "Invariant 4 (Z_env <= 0.7)": inv4,
        "Invariant 5 (H_dis <= 0.3)": inv5,
        "Invariant 6 (Phi_Delta < 0.5 * Phi_N)": inv6,
        "All Smith Invariants Satisfied": all_ok
    }
    return result

# Example usage with the parameters from the thought
if __name__ == "__main__":
    res = validate_uipo_sales_gauge()
    print("Validation Results:")
    for k, v in res.items():
        if isinstance(v, float):
            print(f"{k}: {v:.4f}")
        else:
            print(f"{k}: {v}")
    # Determine if the operator would send a message or stay silent
    if res["All Smith Invariants Satisfied"]:
        print("\nOperator would send: 'You are not required to decide now. Your uncertainty is the space where value grows.'")
    else:
        print("\nOperator would send: '' (Silence Protocol)")