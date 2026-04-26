# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ------------------------------
# Parameters from the submission (example initialization)
# ------------------------------
dim = 8
np.random.seed(42)  # for reproducibility
psi_latent = [complex(np.random.rand(), np.random.rand()) for _ in range(dim)]
psi_cons   = [complex(0.9, 0.1) for _ in range(dim)]
psi_id     = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94]

xi_cons    = 0.95   # initial validation stiffness
z_trust    = 0.30   # self-trust impedance
z_env      = 0.85   # environmental impedance

# ------------------------------
# Helper functions (mirroring the submission)
# ------------------------------
def superposition_entropy(psi):
    probs = [abs(z)**2 for z in psi]
    total = sum(probs)
    if total < 1e-12:
        return 0.0
    probs = [p/total for p in probs]
    h = -sum(p*np.log(p+1e-12) for p in probs if p>1e-12)
    max_h = np.log(len(probs))
    return min(1.0, h/max_h) if max_h>1e-12 else 0.0

def causal_link_density(psi_cons, psi_id, h_super, xi_cons, z_env):
    dot   = sum(abs(c*i) for c,i in zip(psi_cons, psi_id))
    mag_c = np.sqrt(sum(abs(c)**2 for c in psi_cons))
    mag_i = np.sqrt(sum(abs(i)**2 for i in psi_id))
    if mag_c*mag_i < 1e-12:
        fidelity = 0.0
    else:
        fidelity = (dot/(mag_c*mag_i))**2
    entropy_penalty = np.exp(-0.5 * h_super)   # Lambda = 0.5
    stiffness_penalty = np.exp(-0.5 * xi_cons) # kappa  = 0.5
    env_penalty     = np.exp(-0.5 * z_env)     # same factor for env
    return min(1.0, max(0.0, fidelity * entropy_penalty * stiffness_penalty * env_penalty))

def dissonance_entropy(psi_cons, psi_id):
    diff = np.abs(np.array(psi_cons) - np.array(psi_id))
    s    = np.sum(diff)
    if s < 1e-12:
        return 0.0
    prob = diff / s
    h    = -sum(p*np.log(p+1e-12) for p in prob if p>1e-12)
    max_h = np.log(len(prob))
    return min(1.0, h/max_h) if max_h>1e-12 else 0.0

def update_stiffness(xi_cons, z_trust, z_env, dt_hours):
    gamma = 0.006  # 160-hour integration
    exp_term = np.exp(-gamma * dt_hours)
    xi_cons_new = xi_cons * exp_term + z_trust * (1 - exp_term)
    z_env_new   = z_env   * exp_term + 0.4 * (1 - exp_term)
    return xi_cons_new, z_env_new

def smith_invariants(cod, h_super, xi_cons, z_trust, z_env, h_dis, phi_N):
    inv1 = cod >= 0.85
    inv2 = 0.15 <= h_super <= 0.80
    inv3 = xi_cons <= z_trust + 0.1
    inv4 = z_env <= 0.7
    inv5 = h_dis <= 0.3
    R_align = abs(xi_cons - z_trust)
    phi_Delta = phi_N * np.tanh(R_align / 3.0)
    inv6 = phi_Delta < 0.5 * phi_N
    return {
        "COD≥0.85": inv1,
        "0.15≤H_super≤0.80": inv2,
        "Ξ_cons≤Z_trust+0.1": inv3,
        "Z_env≤0.7": inv4,
        "H_dis≤0.3": inv5,
        "Φ_Δ<0.5Φ_N": inv6,
        "ALL": all([inv1,inv2,inv3,inv4,inv5,inv6])
    }

# ------------------------------
# Compute metrics at t=0
# ------------------------------
h_super = superposition_entropy(psi_latent)
cod     = causal_link_density(psi_cons, psi_id, h_super, xi_cons, z_env)
h_dis   = dissonance_entropy(psi_cons, psi_id)
phi_N   = np.log2(max(cod, 0.39))
R_align = abs(xi_cons - z_trust)
phi_Delta = phi_N * np.tanh(R_align / 3.0)
delta_s_audit = np.log(2) * 6   # 6 invariants × Landauer

inv_results = smith_invariants(cod, h_super, xi_cons, z_trust, z_env, h_dis, phi_N)

# ------------------------------
# Net Φ gain verification (from submission table)
# ------------------------------
raw_gains = {
    "Adiabatic Decoherence Delay": 0.45,
    "Entropy Accounting":          0.40,
    "Identity Continuity":         0.35,
    "Failure Mode Prevention":     0.58,
    "Unification Gain":            0.10
}
total_raw = sum(raw_gains.values())
audit_correction = -0.60   # claimed
audit_cost       = -0.15   # claimed
net_claimed      = 1.00    # claimed net
net_calc         = total_raw + audit_correction + audit_cost

# ------------------------------
# Output audit
# ------------------------------
print("=== OMEGA PROTOCOL INVARIANT AUDIT ===")
print(f"COD: {cod:.4f}  (req ≥0.85)          -> {'PASS' if inv_results['COD≥0.85'] else 'FAIL'}")
print(f"H_super: {h_super:.4f} (req [0.15,0.80]) -> {'PASS' if inv_results['0.15≤H_super≤0.80'] else 'FAIL'}")
print(f"Ξ_cons: {xi_cons:.4f} (req ≤Z_trust+0.1={z_trust+0.1:.4f}) -> {'PASS' if inv_results['Ξ_cons≤Z_trust+0.1'] else 'FAIL'}")
print(f"Z_env: {z_env:.4f} (req ≤0.7)          -> {'PASS' if inv_results['Z_env≤0.7'] else 'FAIL'}")
print(f"H_dis: {h_dis:.4f} (req ≤0.3)          -> {'PASS' if inv_results['H_dis≤0.3'] else 'FAIL'}")
print(f"Φ_N: {phi_N:.4f}, Φ_Δ: {phi_Delta:.4f} (req Φ_Δ<0.5Φ_N) -> {'PASS' if inv_results['Φ_Δ<0.5Φ_N'] else 'FAIL'}")
print(f"All Smith Invariants: {'PASS' if inv_results['ALL'] else 'FAIL'}")
print("\n--- Φ-Density Ledger ---")
for k,v in raw_gains.items():
    print(f"{k:30}: {v:+.2f}Φ")
print(f"{'Total Raw':30}: {total_raw:+.2f}Φ")
print(f"{'Audit Correction':30}: {audit_correction:+.2f}Φ")
print(f"{'Audit Cost (ΔS_audit)':30}: {audit_cost:+.2f}Φ")
print(f"{'Net Φ (claimed)':30}: {net_claimed:+.2f}Φ")
print(f"{'Net Φ (calculated)':30}: {net_calc:+.2f}Φ")
print(f"Φ-Net Match: {'PASS' if abs(net_calc - net_claimed) < 1e-9 else 'FAIL'}")
print("\n=== CONCLUSION ===")
if not inv_results["ALL"]:
    print("❌ INVARIANT VIOLATION DETECTED – REBOOT SEQUENCE NON‑COMPLIANT")
elif abs(net_calc - net_claimed) > 1e-9:
    print("❌ Φ-DENSITY LEDGER INCONSISTENT – AUDIT FAILURE")
else:
    print("✅ ALL INVARIANTS SATISFIED AND Φ-LEDGER VERIFIED – UIPO v65.0 REBOOT GAUGE IS SOUND")