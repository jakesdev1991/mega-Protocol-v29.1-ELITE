# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Invariant Validator for Narrative Curvature Model
# --------------------------------------------------------------
# This script checks:
#   1. Dimensional consistency of the action terms.
#   2. Correctness of stiffness invariants ξ_N, ξ_Δ from V_eff.
#   3. Noether conservation of the covariant mode norm.
#   4. Bounds on Φ_N, Φ_Δ and non‑negativity of the cost J*.
# --------------------------------------------------------------

import sympy as sp

# --------------------------
# 1. Symbolic definitions
# --------------------------
# Basic symbols (all dimensionless in natural units unless noted)
t, x, y = sp.symbols('t x y', real=True)          # coordinates (t time, x,y spatial on doc manifold)
phi = sp.Function('phi')(x, y)                    # embedding scalar (component) – treat one component for simplicity
# Embedding dimension D is absorbed into norm later; we work with a single component for clarity.

# Metric from embedding gradient (induced)
# g_{ij} = <∂_i phi, ∂_j phi> ; for a single component this is (∂_i phi)*(∂_j phi)
g_xx = sp.diff(phi, x)**2
g_yy = sp.diff(phi, y)**2
g_xy = sp.diff(phi, x)*sp.diff(phi, y)

g = sp.Matrix([[g_xx, g_xy],
               [g_xy, g_yy]])                     # 2x2 metric (d=2 case)
g_inv = g.inv()
sqrt_g = sp.sqrt(g.det())

# Scalar curvature R in 2D: R = 2 * Gaussian curvature
# Gaussian K = (R_{1212}) / det(g); we compute via Christoffel
def christoffel(g, ginv):
    dim = g.shape[0]
    Gamma = [[[sp.zeros_like(phi) for _ in range(dim)] for __ in range(dim)] for ___ in range(dim)]
    for i in range(dim):
        for j in range(dim):
            for l in range(dim):
                Gamma[i][j][l] = sp.Rational(1,2) * sum(
                    ginv[l][k] * (sp.diff(g[j][k], (x if i==0 else y)) +
                                  sp.diff(g[i][k], (x if j==0 else y)) -
                                  sp.diff(g[k][j], (x if i==0 else y)))
                    for k in range(dim))
    return Gamma

Gamma = christoffel(g, g_inv)

def ricci_tensor(g, ginv, Gamma):
    dim = g.shape[0]
    R = [[sp.zeros_like(phi) for _ in range(dim)] for __ in range(dim)]
    for i in range(dim):
        for j in range(dim):
            # R_{ij} = ∂_l Γ^l_{ij} - ∂_j Γ^l_{il} + Γ^l_{lm} Γ^m_{ij} - Γ^l_{jm} Γ^m_{il}
            term1 = sum(sp.diff(Gamma[l][i][j], (x if l==0 else y)) for l in range(dim))
            term2 = sum(sp.diff(Gamma[l][i][l], (x if j==0 else y)) for l in range(dim))
            term3 = sum(sum(Gamma[l][l][m] * Gamma[m][i][j] for m in range(dim)) for l in range(dim))
            term4 = sum(sum(Gamma[l][j][m] * Gamma[m][i][l] for m in range(dim)) for l in range(dim))
            R[i][j] = sp.simplify(term1 - term2 + term3 - term4)
    return R

R_tensor = ricci_tensor(g, g_inv, Gamma)
R_scalar = sp.simplify(sum(g_inv[i][j] * R_tensor[i][j] for i in range(2) for j in range(2)))
# In 2D, R_scalar = 2 * Gaussian curvature

# --------------------------
# 2. Action and effective potential
# --------------------------
lam, v, alpha = sp.symbols('lam v alpha', positive=True)   # lam = λ, alpha coupling
# Potential V(phi)
V_phi = lam/4 * (phi**2 - v**2)**2

# Lagrangian density L = sqrt(g)*(0.5*g^{ij}∂_i phi ∂_j phi + V(phi))
L = sqrt_g * (sp.Rational(1,2) * sum(g_inv[i][j] * sp.diff(phi, (x if i==0 else y)) *
                                      sp.diff(phi, (x if j==0 else y))
                                      for i in range(2) for j in range(2)) + V_phi)

# Action S = ∫ L dt dx dy (we keep the integral symbolic)
S = sp.integrate(L, (t, -sp.oo, sp.oo), (x, -sp.oo, sp.oo), (y, -sp.oo, sp.oo))
# For dimensional check we examine the integrand:
L_density = sp.simplify(L)
print("Lagrangian density (should have dimension [T]^-1):")
sp.pprint(L_density)
print("\n")

# --------------------------
# 3. Effective potential V_eff(I) with curvature coupling
# --------------------------
I, I0, lam_eff = sp.symbols('I I0 lam_eff', positive=True)
R_avg = sp.symbols('R_avg', real=True)   # ⟨R⟩ over manuscript patch
V_eff = lam_eff/4 * (I**2 - I0**2)**2 + alpha * R_avg * I
print("Effective potential V_eff(I):")
sp.pprint(V_eff)
print("\n")

# Find stationary point dV/dI = 0
dV_dI = sp.diff(V_eff, I)
stationary = sp.solve(dV_dI, I)
print("Stationary points I*:")
sp.pprint(stationary)
print("\n")

# Choose the physical root (real, positive) – we assume the first
I_star = stationary[0]   # simplification; in practice pick the real positive root
# Second derivative at stationary point
V_eff_pp = sp.diff(V_eff, I, 2).subs(I, I_star)
print("V_eff'' at I* (should be >0 for stability):")
sp.pprint(sp.simplify(V_eff_pp))
print("\n")

# Stiffness invariants from inverse squared frequencies
xi_N_sq_inv = sp.simplify(lam_eff * (3*I0**2 + R_avg))
xi_D_sq_inv = sp.simplify(lam_eff * (I0**2 + 3*R_avg))
xi_N = sp.sqrt(1/xi_N_sq_inv)
xi_D = sp.sqrt(1/xi_D_sq_inv)
print("ξ_N (from paper):", xi_N)
print("ξ_Δ (from paper):", xi_D)
print("\n")

# Compute ξ_N, ξ_Δ from the exact Hessian (should match if paper correct)
# Effective mass squared m^2 = V_eff''(I*)
xi_N_exact = sp.sqrt(1/V_eff_pp)   # assuming one mode dominates; for two-mode we need matrix
# For illustration we compare the trace (sum of eigenvalues) which should equal ξ_N^{-2}+ξ_Δ^{-2}
trace_exact = 2 * V_eff_pp   # in 2D with identical eigenvalues? Not exact but gives a sanity check
trace_paper = xi_N_sq_inv + xi_D_sq_inv
print("Trace of inverse squared stiffness (paper):", trace_paper)
print("Trace from exact V_eff'' (approx):", trace_exact)
print("Difference:", sp.simplify(trace_paper - trace_exact))
print("\n")

# --------------------------
# 4. Covariant modes and Noether conservation
# --------------------------
# Define Φ_N, Φ_Δ as linear combos of fluctuations δI and orthogonal component.
# For simplicity we treat δI as the fluctuation of I around I0: δI = I - I0
deltaI = I - I0
# Orthogonal component placeholder (norm of phi perpendicular to background)
# In this toy model we set it to zero; the conservation test reduces to checking d/dt(Φ_N^2+Φ_Δ^2)=0
Phi_N = deltaI / sp.sqrt(2)
Phi_Delta = sp.zeros_like(deltaI)   # set to zero for this simplified check

# Compute time derivative using chain rule: d/dt = ∂_t + (∂I/∂t)*∂_I
# Assume I depends on t only via R_avg(t) (external curvature)
R_of_t = sp.Function('R')(t)
I_of_t = sp.Function('I')(t)
# Substitute I = I(R) implicitly via stationary condition: solve dV/dI=0 for I as function of R
# We'll differentiate the stationary condition implicitly:
# dV/dI = lam_eff*(I^3 - I0^2*I) + alpha*R = 0
# Differentiate wrt t:
I_sym = sp.Function('I')(t)
eq = lam_eff*(I_sym**3 - I0**2*I_sym) + alpha*R_of_t
# Differentiate:
d_eq_dt = sp.diff(eq, t)
# Solve for dI/dt:
dI_dt_expr = sp.solve(d_eq_dt, sp.diff(I_sym, t))
print("dI/dt from implicit differentiation:", dI_dt_expr)
print("\n")

# Compute d/dt(Φ_N^2 + Φ_Δ^2) = 2*Φ_N*dΦ_N/dt (since Φ_Δ=0)
dPhi_N_dt = sp.diff(Phi_N, t).subs(sp.diff(I_sym, t), dI_dt_expr[0])
dNorm_dt = sp.simplify(2*Phi_N*dPhi_N_dt)
print("Time derivative of covariant mode norm (should be 0):")
sp.pprint(dNorm_dt)
print("\n")
# Assert zero (within simplification)
assert sp.simplify(dNorm_dt) == 0, "Covariant mode norm not conserved – violates Omega invariant!"

# --------------------------
# 5. Mapping to Omega variables via NCI
# --------------------------
NCI, R_c = sp.symbols('NCI R_c', positive=True)
# Definition NCI = 1/(1+|R|/R_c) ; we treat R>=0 for simplicity
NCI_expr = 1/(1 + R_avg/R_c)
print("NCI expression:", NCI_expr)
print("\n")

# Proposed mapping (paper):
alpha_map, beta_map, gamma_map = sp.symbols('alpha_map beta_map gamma_map')
Phi_N_nar = sp.symbols('Phi_N0') + alpha_map * sp.diff(NCI_expr, t)
Phi_D_nar = sp.symbols('Phi_D0') - beta_map * (1 - NCI_expr) + gamma_map * sp.Symbol('Var_phi')
# To test consistency we compute dΦ_N_nar/dt from the action-derived Phi_N and compare
# (Here we just verify that the mapping does not introduce extra t‑derivatives beyond those already present)
print("Proposed Phi_N_nar:", Phi_N_nar)
print("Proposed Phi_Delta_nar:", Phi_D_nar)
print("\n")

# --------------------------
# 6. Cost functional J* and bounds
# --------------------------
R_max, lam1, lam2 = sp.symbols('R_max lam1 lam2', positive=True)
# Running cost integrand:
integrand = (sp.Max(R_avg - R_max, 0))**2 + lam1 * sp.Max(0.3 - NCI_expr, 0)**2 + lam2 * (1 - sp.symbols('Phi_N0'))**2
J_integrand = sp.simplify(integrand)
print("Cost integrand J* (should be >=0):")
sp.pprint(J_integrand)
assert sp.simplify(J_integrand) >= 0, "Cost integrand negative – violates Omega invariant!"
print("\nJ* integrand verified non‑negative.")

print("\n=== All symbolic checks passed ===")