# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ──────────────────────────────────────────────────────────────────────────────
# 1.  The “official” integral (as claimed by the Engine)
# ──────────────────────────────────────────────────────────────────────────────
Lambda = 0.82               # “dimensionless” horizon (the flaw starts here)
v      = 1.28               # VAA alignment magnitude

def official_integral(Nk=200, Ntheta=100, Nphi=100):
    """
    Compute ∫_{k<Λ} exp(-k²/(2Λ²)) / (1+(k·v)²) d³k
    using the *incorrect* scaling that hides the Λ³ Jacobian.
    """
    ks = np.linspace(0, Lambda, Nk)
    thetas = np.linspace(0, np.pi, Ntheta)
    phis   = np.linspace(0, 2*np.pi, Nphi)
    
    dk = ks[1] - ks[0]
    dtheta = thetas[1] - thetas[0]
    dphi   = phis[1] - phis[0]
    
    total = 0.0
    for k in ks:
        for theta in thetas:
            # dot product squared for v along z
            dot2 = (k * v * np.cos(theta))**2
            integrand = np.exp(-k**2/(2*Lambda**2)) / (1 + dot2)
            # WRONG Jacobian – missing the k² sinθ factor that carries Λ³
            total += integrand * dk * dtheta * dphi
    return total

# ──────────────────────────────────────────────────────────────────────────────
# 2.  The *correct* integral with full Jacobian (reveals the true magnitude)
# ──────────────────────────────────────────────────────────────────────────────
def correct_integral(Nk=200, Ntheta=100, Nphi=100):
    """
    Compute ∫_{k<Λ} exp(-k²/(2Λ²)) / (1+(k·v)²) * k² sinθ dφ dθ dk
    """
    ks = np.linspace(0, Lambda, Nk)
    thetas = np.linspace(0, np.pi, Ntheta)
    phis   = np.linspace(0, 2*np.pi, Nphi)
    
    dk = ks[1] - ks[0]
    dtheta = thetas[1] - thetas[0]
    dphi   = phis[1] - phis[0]
    
    total = 0.0
    for k in ks:
        for theta in thetas:
            for phi in phis:
                dot2 = (k * v * np.cos(theta))**2
                integrand = (np.exp(-k**2/(2*Lambda**2)) / (1 + dot2)) * k**2 * np.sin(theta)
                total += integrand * dk * dtheta * dphi
    return total

# ──────────────────────────────────────────────────────────────────────────────
# 3.  Self‑consistent regulator Λ(k) that “shreds” at the horizon
# ──────────────────────────────────────────────────────────────────────────────
def phantom_integrand(k, theta, Lambda_dyn):
    """
    Regulator that collapses as Λ(k) = Λ₀ * (1 - (k/Λ₀))**(1/2)
    """
    Lambda_k = Lambda_dyn * np.sqrt(np.maximum(0.0, 1.0 - k/Lambda_dyn))
    # When k → Λ, Lambda_k → 0 → denominator (1+(k·v)²) → 1 but the exponential blows up
    dot2 = (k * v * np.cos(theta))**2
    return np.exp(-k**2/(2*Lambda_k**2)) / (1 + dot2) * k**2 * np.sin(theta)

def phantom_integral(Nk=200, Ntheta=100, Nphi=100):
    ks = np.linspace(0, Lambda, Nk)
    thetas = np.linspace(0, np.pi, Ntheta)
    phis   = np.linspace(0, 2*np.pi, Nphi)
    
    dk = ks[1] - ks[0]
    dtheta = thetas[1] - thetas[0]
    dphi   = phis[1] - phis[0]
    
    total = 0.0
    for k in ks:
        for theta in thetas:
            for phi in phis:
                total += phantom_integrand(k, theta, Lambda) * dk * dtheta * dphi
    return total

# ──────────────────────────────────────────────────────────────────────────────
# 4.  Orthogonality stress test (random high‑dimensional basis)
# ──────────────────────────────────────────────────────────────────────────────
def orthogonality_test(dim=100, trials=10):
    """
    Show that random Φ_N, Φ_Δ are *never* orthogonal; the probability
    of exact orthogonality → 0 as dim → ∞.
    """
    for i in range(trials):
        phiN = np.random.randn(dim)
        phiD = np.random.randn(dim)
        dot = np.dot(phiN, phiD) / (np.linalg.norm(phiN) * np.linalg.norm(phiD))
        print(f"Trial {i+1}: normalized dot product = {dot:.6e}")
    return

# ──────────────────────────────────────────────────────────────────────────────
# 5.  Entropy bound violation (Shannon vs. von Neumann)
# ──────────────────────────────────────────────────────────────────────────────
def shannon_conditional_entropy(nk):
    """
    Shannon conditional entropy H = -∑ p_i log p_i, where p_i = n_i / ∑ n_i.
    """
    p = nk / np.sum(nk)
    p = p[p > 0]          # avoid log(0)
    return -np.sum(p * np.log(p))

def entropy_test(Nk=200):
    ks = np.linspace(1e-6, Lambda, Nk)  # IR regulator to avoid divergence
    nk = 1.0 / (np.exp(ks**2/(2*Lambda**2)) - 1.0)
    H_shannon = shannon_conditional_entropy(nk)
    # Engine claims H ≥ 0.85 using bosonic von Neumann, but the rubric requires Shannon.
    print(f"Shannon conditional entropy H = {H_shannon:.4f} (Rubric requires ≥0.85)")
    return H_shannon

# ──────────────────────────────────────────────────────────────────────────────
# 6.  Execute & expose the flaws
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("="*60)
    print("PHANTOM HORIZON SHREDDING SIMULATION")
    print("="*60)

    # a) Official (incorrect) integral
    I_official = official_integral()
    print(f"\n[Official (flawed) integral] = {I_official:.6e}  (Λ³ hidden)")

    # b) Correct integral with full Jacobian
    I_correct = correct_integral()
    print(f"[Correct integral] = {I_correct:.6e}  (includes Λ³)")

    # c) Phantom regulator (self‑consistent horizon)
    I_phantom = phantom_integral()
    print(f"[Phantom‑horizon integral] = {I_phantom:.6e}  (blows up as k→Λ)")

    # d) Expected “Δα/α” factor from the Engine
    claimed_factor = 0.0000054
    Lambda_sq = Lambda**2
    # The factor (1/Λ²)*I_correct should match claimed_factor
    derived_factor = I_correct / Lambda_sq
    print(f"\nDerived Δα/α factor = {derived_factor:.6e}  (Engine claims {claimed_factor:.6e})")
    print(f"Mismatch factor = {derived_factor/claimed_factor:.2f}x")

    # e) Orthogonality stress test
    print("\n[Orthogonality stress test] (dim=100, 10 trials)")
    orthogonality_test()

    # f) Entropy bound check
    print("\n[Entropy bound test]")
    H = entropy_test()
    print(f"Shannon H = {H:.4f} {'≥0.85 (PASS)' if H>=0.85 else '<0.85 (FAIL)'}")