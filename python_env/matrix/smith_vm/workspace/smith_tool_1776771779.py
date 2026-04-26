# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Validation script for Coupled Stability Omega (CSO‑Ω) proposal
# Checks mathematical consistency of the field‑theoretic derivation,
# definitions of invariants, entropy gauge, and MPC‑Ω constraints.
# Uses sympy for symbolic algebra and numpy for numeric examples.

import sympy as sp
import numpy as np

# ------------------------------------------------------------------
# 1. Symbolic definitions (field‑theoretic core)
# ------------------------------------------------------------------
# Parameters (all positive, dimensionless after field normalization)
m_theta, m_psi, gamma = sp.symbols('m_theta m_psi gamma', positive=True)
# Velocities appearing in gradient terms (set to 1 for simplicity; can be kept symbolic)
v_theta, v_psi = sp.symbols('v_theta v_psi', positive=True)

# Hessian of the coupling potential V = 1/2 m_theta^2 θ^2 + 1/2 m_psi^2 Ψ^2 - γ θ Ψ
H = sp.Matrix([[m_theta**2, -gamma],
               [-gamma, m_psi**2]])

# Eigenvalues (stiffness inverses)
lambda_plus, lambda_minus = H.eigenvals()
# sympy returns a dict; extract and order
eig_vals = sorted([lambda_plus, lambda_minus], key=lambda x: x)
lambda_plus_val, lambda_minus_val = eig_vals[0], eig_vals[1]  # λ+ ≥ λ-

# Stiffness invariants (inverse squared correlation lengths)
xi_N_sq_inv   = lambda_plus_val   # ξ_N^{-2}
xi_Delta_sq_inv = lambda_minus_val # ξ_Δ^{-2}

# Correlation length associated with the softer (Archive) mode
# For a massive scalar field, ξ ∼ 1/√(mass^2) → we identify ξ ∝ 1/√λ_minus
xi = 1 / sp.sqrt(lambda_minus_val)   # up to a velocity factor; we keep v=1

# Metric coupling invariant ψ = ln(ξ/ξ0) (dimensionless)
xi0 = sp.symbols('xi0', positive=True)
psi = sp.log(xi / xi0)

# ------------------------------------------------------------------
# 2. Relate field quantities to log‑derived coupling invariants
# ------------------------------------------------------------------
# Assume proportionality constants (all dimensionless) for clarity
k_rho, k_tau, k_width = sp.symbols('k_rho k_tau k_width', positive=True)

# Peak correlation ρ_max ∝ γ / (m_theta m_psi)
rho_max = k_rho * gamma / (m_theta * m_psi)

# Optimal lag τ_opt ∝ ξ / v (take v = sqrt(v_theta*v_psi) as effective speed)
v_eff = sp.sqrt(v_theta * v_psi)
tau_opt = k_tau * xi / v_eff

# Correlation width Δτ ∝ ξ
Delta_tau = k_width * xi

# ------------------------------------------------------------------
# 3. Secondary stiffness invariants (sensitivities)
# ------------------------------------------------------------------
# ξ_c = ∂ρ_max/∂ψ , ξ_τ = ∂τ_opt/∂psi
xi_c   = sp.diff(rho_max, psi)
xi_tau = sp.diff(tau_opt, psi)

# ------------------------------------------------------------------
# 4. Entropy gauge from distribution of ρ_max across a population
# ------------------------------------------------------------------
# Model ρ_max as Gaussian with mean μ_ρ and variance σ_ρ^2 (both >0)
mu_rho, sigma_rho = sp.symbols('mu_rho sigma_rho', positive=True)
# Probability density
p_rho = 1/(sp.sqrt(2*sp.pi)*sigma_rho) * sp.exp(-(sp.Symbol('rho') - mu_rho)**2/(2*sigma_rho**2))
# Shannon entropy S = -∫ p ln p dρ
S_coup = -sp.integrate(p_rho * sp.log(p_rho), (sp.Symbol('rho'), -sp.oo, sp.oo))
# Simplify known Gaussian entropy: S = 0.5 * ln(2π e σ^2)
S_coup_simplified = sp.simplify(S_coup)
# Gauge potential A_μ = ∂_μ S_coup (here we treat μ as a generic coordinate x)
x = sp.symbols('x')
# For demonstration, let S depend on x via μ_ρ(x) = a*x + b
a, b = sp.symbols('a b')
mu_rho_func = a*x + b
S_coup_x = sp.simplify(-sp.integrate(
        1/(sp.sqrt(2*sp.pi)*sigma_rho) * sp.exp(-(sp.Symbol('rho') - mu_rho_func)**2/(2*sigma_rho**2)) *
        sp.log(1/(sp.sqrt(2*sp.pi)*sigma_rho) * sp.exp(-(sp.Symbol('rho') - mu_rho_func)**2/(2*sigma_rho**2))),
        (sp.Symbol('rho'), -sp.oo, sp.oo)))
A_mu = sp.diff(S_coup_x, x)   # gauge field component

# ------------------------------------------------------------------
# 5. Mapping to Omega field variables (empirical linear model)
# ------------------------------------------------------------------
# Base values
Phi_N0, Phi_Delta0 = sp.symbols('Phi_N0 Phi_Delta0', real=True)
# Coupling coefficients
a1, a2, b1, b2 = sp.symbols('a1 a2 b1 b2', real=True)
tau_target = sp.symbols('tau_target', positive=True)

Phi_N_coup = Phi_N0 + a1*rho_max - a2*sp.Abs(tau_opt - tau_target)
Phi_Delta_coup = Phi_Delta0 + b1*(1 - rho_max) + b2*Delta_tau

# ------------------------------------------------------------------
# 6. Define MPC‑Ω stability constraints (dimensionless thresholds)
# ------------------------------------------------------------------
tau_max   = sp.symbols('tau_max', positive=True)
zeta      = sp.symbols('zeta', real=True)   # damping ratio from linearized SDEs

constraints = {
    'rho_min'   : sp.simplify(rho_max - 0.3),          # >=0
    'tau_max'   : sp.simplify(tau_max - tau_opt),     # >=0
    'zeta_low'  : sp.simplify(zeta - 0.7),            # >=0
    'zeta_high' : sp.simplify(1.3 - zeta),            # >=0
    'Phi_N_low' : sp.simplify(Phi_N_coup - 0.5),      # >=0
    'Phi_Delta_high': sp.simplify(0.6 - Phi_Delta_coup) # >=0
}

# ------------------------------------------------------------------
# 7. Numeric sanity check (sample plausible values)
# ------------------------------------------------------------------
def numeric_check():
    # Choose numbers that respect positivity and typical scales
    subs_dict = {
        m_theta: 1.0, m_psi: 1.0, gamma: 0.5,
        v_theta: 1.0, v_psi: 1.0,
        k_rho: 1.0, k_tau: 1.0, k_width: 1.0,
        xi0: 1.0,
        mu_rho: 0.5, sigma_rho: 0.2,
        a: 0.1, b: 0.0,
        Phi_N0: 0.4, Phi_Delta0: 0.2,
        a1: 0.3, a2: 0.2, b1: 0.25, b2: 0.15,
        tau_target: 0.5,
        tau_max: 2.0,
        zeta: 1.0
    }
    # Evaluate constraints
    results = {}
    for name, expr in constraints.items():
        val = float(expr.subs(subs_dict))
        results[name] = val >= -1e-9  # allow tiny numerical negative
    # Also print key invariants
    invariants = {
        'rho_max': float(rho_max.subs(subs_dict)),
        'tau_opt': float(tau_opt.subs(subs_dict)),
        'Delta_tau': float(Delta_tau.subs(subs_dict)),
        'xi_N': float(1/sp.sqrt(xi_N_sq_inv).subs(subs_dict)),
        'xi_Delta': float(1/sp.sqrt(xi_Delta_sq_inv).subs(subs_dict)),
        'psi': float(psi.subs(subs_dict)),
        'S_coup': float(S_coup_simplified.subs({sigma_rho: subs_dict[sigma_rho]})),
        'Phi_N_coup': float(Phi_N_coup.subs(subs_dict)),
        'Phi_Delta_coup': float(Phi_Delta_coup.subs(subs_dict))
    }
    return results, invariants

if __name__ == "__main__":
    # Symbolic checks
    print("=== Symbolic consistency ===")
    print("Hessian:\n", H)
    print("Eigenvalues (λ+, λ-):", lambda_plus_val, lambda_minus_val)
    print("Stiffness inverses: ξ_N^{-2} =", xi_N_sq_inv, " ; ξ_Δ^{-2} =", xi_Delta_sq_inv)
    print("Correlation length ξ =", xi)
    print("ψ = ln(ξ/ξ0) =", psi)
    print("ρ_max expression:", rho_max)
    print("τ_opt expression:", tau_opt)
    print("Δτ expression:", Delta_tau)
    print("Secondary stiffness ξ_c =", xi_c)
    print("Secondary stiffness ξ_τ =", xi_tau)
    print("Entropy gauge (Gaussian) S_coup =", S_coup_simplified)
    print("Gauge component A_μ =", A_mu)
    print("\n=== Constraint expressions ===")
    for k, v in constraints.items():
        print(f"{k}: {v}")
    print("\n=== Numeric sanity check ===")
    const_res, inv_res = numeric_check()
    print("Constraint satisfaction (True = OK):")
    for k, v in const_res.items():
        print(f"  {k}: {v}")
    print("\nInvariant values:")
    for k, v in inv_res.items():
        print(f"  {k}: {v:.4f}")
    # Overall verdict
    all_ok = all(const_res.values())
    print("\nOverall validation:", "PASS" if all_ok else "FAIL")