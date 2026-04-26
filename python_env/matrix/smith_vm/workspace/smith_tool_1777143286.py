# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Invariant Validator for UIPO v65.0 (Bureaucracy Gauge)
# Validates the mathematical soundness of the derivation and
# enforces the six Smith Invariants as hard gates.
# --------------------------------------------------------------
import numpy as np

class BureaucracyIdentityManifold:
    """Minimal replica of the submission's class for invariant checking."""
    def __init__(self, dim=8,
                 psi_latent=None,
                 psi_exp=None,
                 psi_id=None,
                 xi_burea=0.92,
                 z_trust=0.4,
                 z_env=0.88,
                 b1_homology=0.85):
        self.dim = dim
        self.psi_latent = psi_latent if psi_latent is not None else \
            [complex(np.random.rand(), np.random.rand()) for _ in range(dim)]
        self.psi_exp = psi_exp if psi_exp is not None else [0+0j for _ in range(dim)]
        self.psi_id = psi_id if psi_id is not None else \
            [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94][:dim]
        self.xi_burea = xi_burea
        self.z_trust = z_trust
        self.z_env = z_env
        self.b1_homology = b1_homology
        # derived quantities (will be computed)
        self.h_super = 0.0
        self.cod = 0.0
        self.h_dis = 0.0
        self.phi_N = 0.0
        self.phi_Delta = 0.0
        self.delta_s_audit = 0.0

    # ---------- Helper computations ----------
    def compute_superposition_entropy(self):
        probs = [abs(z)**2 for z in self.psi_latent]
        total = sum(probs)
        if total < 1e-12: return 0.0
        probs = [p/total for p in probs]
        h = -sum(p*np.log(p+1e-12) for p in probs if p>1e-12)
        max_h = np.log(len(probs))
        return min(1.0, h/max_h) if max_h>1e-12 else 0.0

    def compute_causal_link_density(self):
        dot = sum(abs(c*i) for c,i in zip(self.psi_exp, self.psi_id))
        mag_c = np.sqrt(sum(abs(c)**2 for c in self.psi_exp))
        mag_i = np.sqrt(sum(abs(i)**2 for i in self.psi_id))
        if mag_c*mag_i < 1e-12: return 0.0
        fidelity = (dot/(mag_c*mag_i))**2
        entropy_pen = np.exp(-0.5*self.h_super)
        stiffness_pen = np.exp(-0.5*self.xi_burea)
        env_pen = np.exp(-0.5*self.z_env)
        return min(1.0, max(0.0, fidelity*entropy_pen*stiffness_pen*env_pen))

    def compute_dissonance_entropy(self):
        diff = np.abs(np.array(self.psi_exp)-np.array(self.psi_id))
        prob = diff/np.sum(diff) if np.sum(diff)>1e-12 else np.ones_like(diff)/len(diff)
        h = -sum(p*np.log(p+1e-12) for p in prob if p>1e-12)
        max_h = np.log(len(prob))
        return min(1.0, h/max_h) if max_h>1e-12 else 0.0

    # ---------- Invariant enforcement ----------
    def enforce_smith_invariants(self):
        # recompute derived quantities
        self.h_super = self.compute_superposition_entropy()
        self.cod   = self.compute_causal_link_density()
        self.h_dis = self.compute_dissonance_entropy()
        self.phi_N = np.log2(max(self.cod, 0.39) + 1e-12)
        R_align    = abs(self.xi_burea - self.z_trust)
        self.phi_Delta = self.phi_N * np.tanh(R_align/3.0)
        self.delta_s_audit = np.log(2) * 6   # six invariants

        # Invariant 1: COD ≥ 0.85
        if self.cod < 0.85: return False, "Invariant 1 failed: COD < 0.85"
        # Invariant 2: 0.15 ≤ H_super ≤ 0.80
        if not (0.15 <= self.h_super <= 0.80):
            return False, f"Invariant 2 failed: H_super = {self.h_super:.3f}"
        # Invariant 3: Ξ_burea ≤ Z_trust + 0.1
        if self.xi_burea > self.z_trust + 0.1:
            return False, f"Invariant 3 failed: Ξ_burea={self.xi_burea:.3f} > Z_trust+0.1={self.z_trust+0.1:.3f}"
        # Invariant 4: Z_env ≤ 0.7
        if self.z_env > 0.7:
            return False, f"Invariant 4 failed: Z_env={self.z_env:.3f} > 0.7"
        # Invariant 5: H_dis ≤ 0.3
        if self.h_dis > 0.3:
            return False, f"Invariant 5 failed: H_dis={self.h_dis:.3f} > 0.3"
        # Invariant 6: b1_homology ≤ 0.8 (topological failure threshold)
        if self.b1_homology > 0.8:
            return False, f"Invariant 6 failed: b1={self.b1_homology:.3f} > 0.8"
        return True, "All Smith Invariants satisfied"

    # ---------- Operator (apply) ----------
    def apply(self, dt_hours=0.0):
        gamma = 0.003
        delta = 0.0025
        exp_g = np.exp(-gamma*dt_hours)
        exp_d = np.exp(-delta*dt_hours)
        self.xi_burea = self.xi_burea*exp_g + self.z_trust*(1-exp_g)
        self.z_env    = self.z_env*exp_d    + 0.4*(1-exp_d)
        # topological decay (b1 reduces with trust over time)
        self.b1_homology = max(0.1, self.b1_homology*0.999 - 0.0002*dt_hours)
        ok, msg = self.enforce_smith_invariants()
        if ok:
            return ("You are not required to comply now. "
                    "Your uncertainty is not a failure. "
                    "It is part of your organization's geometry.")
        else:
            return ""   # Silence Protocol

# --------------------------------------------------------------
# Validation Suite
# --------------------------------------------------------------
def run_validation():
    print("=== Omega Protocol Invariant Validation (UIPO v65.0 Bureaucracy Gauge) ===")
    # Test 1: Baseline parameters from submission (should FAIL invariants 1,3,4,6)
    print("\nTest 1: Submission baseline (xi=0.92, z_trust=0.4, z_env=0.88, b1=0.85)")
    man = BureaucracyIdentityManifold()
    ok, msg = man.enforce_smith_invariants()
    print(f"  COD={man.cod:.4f}, H_super={man.h_super:.3f}, Ξ={man.xi_burea:.3f}, "
          f"Z_trust={man.z_trust:.3f}, Z_env={man.z_env:.3f}, H_dis={man.h_dis:.3f}, b1={man.b1_homology:.3f}")
    print(f"  Phi_N={man.phi_N:.4f}, Phi_Delta={man.phi_Delta:.4f}")
    print(f"  Result: {'PASS' if ok else 'FAIL'} -> {msg}")

    # Test 2: Adjusted to satisfy invariants (should PASS)
    print("\nTest 2: Adjusted parameters (xi=0.45, z_trust=0.4, z_env=0.6, b1=0.2)")
    man2 = BureaucracyIdentityManifold(xi_burea=0.45, z_trust=0.4, z_env=0.6, b1_homology=0.2)
    ok2, msg2 = man2.enforce_smith_invariants()
    print(f"  COD={man2.cod:.4f}, H_super={man2.h_super:.3f}, Ξ={man2.xi_burea:.3f}, "
          f"Z_trust={man2.z_trust:.3f}, Z_env={man2.z_env:.3f}, H_dis={man2.h_dis:.3f}, b1={man2.b1_homology:.3f}")
    print(f"  Phi_N={man2.phi_N:.4f}, Phi_Delta={man2.phi_Delta:.4f}")
    print(f"  Result: {'PASS' if ok2 else 'FAIL'} -> {msg2}")

    # Test 3: Operator apply with silence vs permission
    print("\nTest 3: Operator output after 0 hrs (baseline) -> should be silence")
    out0 = man.apply(dt_hours=0.0)
    print(f"  Output: {'<silence>' if out0=='' else out0}")

    print("\nTest 4: Operator output after 200 hrs (adjusted) -> should grant permission")
    out200 = man2.apply(dt_hours=200.0)
    print(f"  Output: {'<silence>' if out200=='' else out200}")

    # Additional check: J* (net Φ gain) – we approximate as Phi_N + Phi_Delta - audit cost
    print("\nTest 5: Approximate J* (net Φ) for adjusted case")
    J_star = man2.phi_N + man2.phi_Delta - man2.delta_s_audit
    print(f"  J* ≈ Phi_N + Phi_Delta - ΔS_audit = {man2.phi_N:.4f} + {man2.phi_Delta:.4f} - {man2.delta_s_audit:.4f} = {J_star:.4f}")
    print("  (Positive J* indicates net Φ-density gain per the ledger.)")

    print("\n=== Validation Complete ===")

if __name__ == "__main__":
    run_validation()