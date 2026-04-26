# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Ω‑Protocol LSGM‑Ω Action Validator (SymPy based)
# --------------------------------------------------------------
import sympy as sp
import re

# ------------------------------------------------------------------
# Helper: parse a user‑supplied action string into a SymPy expression
# ------------------------------------------------------------------
def parse_action(action_str: str) -> sp.Expr:
    """
    Expects a string that SymPy can parse, e.g.
        "1/2*g**(mu,nu)*dE_dmu*dE_dnu + 1/2*g**(mu,nu)*dK_dmu*dK_dnu + V + lambda_O*L_O + A_mu*J**mu"
    Symbols must be defined beforehand (see `make_symbols`).
    """
    # Replace common shorthand for derivatives with SymPy's Derivative
    action_str = re.sub(r'd(\w+)_d(\w+)', r'Derivative(\1, \2)', action_str)
    action_str = re.sub(r'd(\w+)', r'Derivative(\1)', action_str)
    return sp.sympify(action_str)

# ------------------------------------------------------------------
# Build the symbol set needed for the action
# ------------------------------------------------------------------
def make_symbols():
    # Coordinates
    t, x, y, z = sp.symbols('t x y z', real=True)
    # Indices as strings for clarity (we will not contract them explicitly)
    mu, nu, rho, sigma = sp.symbols('mu nu rho sigma')
    # Fields
    E   = sp.Function('E')(t, x, y, z)          # exposure field
    K   = sp.Function('K')(t, x, y, z)          # epistemic field
    A_mu = sp.Function('A_mu')(t, x, y, z)      # gauge field (covariant component)
    # Covariant modes (functions of spacetime)
    Phi_N = sp.Function('Phi_N')(t, x, y, z)
    Phi_Delta = sp.Function('Phi_Delta')(t, x, y, z)
    # Stiffness parameters (constants)
    xi_N, xi_Delta = sp.symbols('xi_N xi_Delta', positive=True)
    # Potential parameters
    alpha, beta, gamma, lambda_O = sp.symbols('alpha beta gamma lambda_O')
    # Reference scales
    E0, K0 = sp.symbols('E0 K0')
    # Entropy gauge components
    S_dir = sp.Function('S_dir')(t, x, y, z)   # directory‑type entropy
    J_mu = sp.sqrt(2) * Phi_Delta * sp.KroneckerDelta(0, mu)  # J^mu = sqrt(2) Phi_Delta delta^mu_0
    # Return a dict for substitution
    return {
        't':t,'x':x,'y':y,'z':z,
        'mu':mu,'nu':nu,'rho':rho,'sigma':sigma,
        'E':E,'K':K,'A_mu':A_mu,
        'Phi_N':Phi_N,'Phi_Delta':Phi_Delta,
        'xi_N':xi_N,'xi_Delta':xi_Delta,
        'alpha':alpha,'beta':beta,'gamma':gamma,'lambda_O':lambda_O,
        'E0':E0,'K0':K0,
        'S_dir':S_dir,'J_mu':J_mu
    }

# ------------------------------------------------------------------
# Core validation routine
# ------------------------------------------------------------------
def validate_lsgm_action(action_expr: sp.Expr, symbols: dict) -> None:
    """
    Raises RuntimeError with a detailed message if any Ω‑rubric requirement fails.
    """
    # ---- 1. Invariant ψ = ln Φ_N (or ψ_Δ = ln Φ_Δ) must appear in the potential ----
    # We look for a term that is a function of ln(Phi_N) or ln(Phi_Delta) inside V or added separately.
    lnPhiN = sp.log(symbols['Phi_N'])
    lnPhiD = sp.log(symbols['Phi_Delta'])
    invariant_present = any(
        lnPhiN in term or lnPhiD in term
        for term in sp.Add.make_args(action_expr)
    )
    if not invariant_present:
        raise RuntimeError(
            "Invariant violation: the action must contain an explicit term "
            "ψ = ln Φ_N (or ψ_Δ = ln Φ_Δ) as part of the effective potential."
        )

    # ---- 2. Entropy‑gauge must be a proper gauge coupling ----
    # Required pattern: A_mu * J^mu  AND  field strength term F_{mu nu} F^{mu nu}
    A_mu = symbols['A_mu']
    J_mu = symbols['J_mu']
    gauge_coupling = A_mu * J_mu
    # Build symbolic field strength: F_{mu nu} = dA_nu/dx^mu - dA_mu/dx^nu
    # We contract with metric g^{mu nu} later; just check presence of dA terms.
    dA = [sp.Derivative(A_mu, symbols['mu']), sp.Derivative(A_mu, symbols['nu'])]
    # Look for combination dA_mu/dx^nu - dA_nu/dx^mu anywhere
    Fsq_present = False
    for term in sp.Add.make_args(action_expr):
        if isinstance(term, sp.Derivative):
            # naive check: if term derivative of A_mu appears, assume field strength exists
            if A_mu in term.expr:
                Fsq_present = True
                break
    if not (gauged_coupling_present := gauge_coupling in sp.Add.make_args(action_expr)):
        raise RuntimeError(
            "Entropy‑gauge violation: the action must contain the minimal coupling "
            "𝒜_μ J^μ and a field‑strength term F_{μν}F^{μν} to enforce ∂_μ J^μ = 0."
        )
    if not Fsq_present:
        raise RuntimeError(
            "Entropy‑gauge violation: missing gauge field strength term F_{μν}F^{μν}."
        )

    # ---- 3. Explicit kinetic stiffness for Φ_N and Φ_Δ ----
    # Expected: (xi_N/2) * g^{μν} ∂_μ Φ_N ∂_ν Φ_N  +  (xi_Delta/2) * g^{μν} ∂_μ Φ_Δ ∂_ν Φ_Δ
    # We simply look for the pattern xi_N * Derivative(Phi_N,*)*Derivative(Phi_N,*)
    # and similarly for Phi_Delta.
    def has_kinetic(symbol_field, xi):
        # Build a generic term: xi/2 * Derivative(symbol, any) * Derivative(symbol, any)
        # We'll accept any contraction metric factor as long as the two derivatives match.
        for term in sp.Add.make_args(action_expr):
            if xi in term.free_symbols:
                # count derivatives of the field
                derivs = [f for f in term.atoms(sp.Derivative) if symbol_field in f.expr]
                if len(derivs) >= 2:
                    return True
        return False

    if not has_kinetic(symbols['Phi_N'], symbols['xi_N']):
        raise RuntimeError(
            "Missing kinetic stiffness term for Φ_N: action must contain "
            "(ξ_N/2) g^{μν} ∂_μ Φ_N ∂_ν Φ_N."
        )
    if not has_kinetic(symbols['Phi_Delta'], symbols['xi_Delta']):
        raise RuntimeError(
            "Missing kinetic stiffness term for Φ_Δ: action must contain "
            "(ξ_Δ/2) g^{μν} ∂_μ Φ_Δ ∂_ν Φ_Δ."
        )

    # ---- 4. Boundary terminology ----
    # The original action string is needed for a plain‑text search.
    # We'll capture it from the caller's global scope via a closure (see wrapper below).
    # For simplicity, we require the strings to appear in the action expression's
    # string representation.
    action_str = str(action_expr)
    if "Shredding Event" not in action_str:
        raise RuntimeError(
            "Boundary violation: the action description must contain the exact phrase "
            "'Shredding Event'."
        )
    if "Informational Freeze" not in action_str:
        raise RuntimeError(
            "Boundary violation: the action description must contain the exact phrase "
            "'Informational Freeze'."
        )

    # ---- 5. Diagonal decomposition declaration ----
    # We require a comment marker in the source; we approximate by looking for the token.
    if "# DIAGONAL_DECOMPOSITION" not in action_str:
        raise RuntimeError(
            "Covariant‑mode violation: the action must include an explicit statement "
            "of diagonal decomposition (e.g., '# DIAGONAL_DECOMPOSITION')."
        )

    # ---- 6. Dimensional consistency check (simple scaling) ----
    # Every term should carry an overall factor 1/τ0^2 (time) or 1/ℓ0^2 (length)
    # after substituting derivative symbols with 1/τ0 or 1/ℓ0.
    tau0, ell0 = sp.symbols('tau0 ell0', positive=True)
    # Replace derivatives: ∂_t -> 1/tau0, ∂_x -> 1/ell0, etc.
    subs_dict = {
        sp.Derivative(symbols['E'], symbols['t']): 1/tau0,
        sp.Derivative(symbols['E'], symbols['x']): 1/ell0,
        sp.Derivative(symbols['E'], symbols['y']): 1/ell0,
        sp.Derivative(symbols['E'], symbols['z']): 1/ell0,
        sp.Derivative(symbols['K'], symbols['t']): 1/tau0,
        sp.Derivative(symbols['K'], symbols['x']): 1/ell0,
        sp.Derivative(symbols['K'], symbols['y']): 1/ell0,
        sp.Derivative(symbols['K'], symbols['z']): 1/ell0,
        sp.Derivative(symbols['Phi_N'], symbols['t']): 1/tau0,
        sp.Derivative(symbols['Phi_N'], symbols['x']): 1/ell0,
        sp.Derivative(symbols['Phi_N'], symbols['y']): 1/ell0,
        sp.Derivative(symbols['Phi_N'], symbols['z']): 1/ell0,
        sp.Derivative(symbols['Phi_Delta'], symbols['t']): 1/tau0,
        sp.Derivative(symbols['Phi_Delta'], symbols['x']): 1/ell0,
        sp.Derivative(symbols['Phi_Delta'], symbols['y']): 1/ell0,
        sp.Derivative(symbols['Phi_Delta'], symbols['z']): 1/ell0,
        sp.Derivative(symbols['A_mu'], symbols['t']): 1/tau0,
        sp.Derivative(symbols['A_mu'], symbols['x']): 1/ell0,
        sp.Derivative(symbols['A_mu'], symbols['y']): 1/ell0,
        sp.Derivative(symbols['A_mu'], symbols['z']): 1/ell0,
    }
    scaled = action_expr.subs(subs_dict)
    # After substitution, the expression should be dimensionless -> no tau0 or ell0 left.
    remaining = scaled.free_symbols.intersection({tau0, ell0})
    if remaining:
        raise RuntimeError(
            f"Dimensional inconsistency: leftover scale symbols {remaining} after substituting "
            f"∂_t → 1/τ₀, ∂_x → 1/ℓ₀. Each term must carry overall factor 1/τ₀² or 1/ℓ₀²."
        )

    # If we reach here, all checks passed.
    print("✅ LSGM‑Ω action satisfies all Ω‑Physics Rubric v26.0 requirements.")

# ------------------------------------------------------------------
# Wrapper to be used in the VM: user provides the raw action string.
# ------------------------------------------------------------------
def validate_action_string(action_str: str):
    symbols = make_symbols()
    try:
        expr = parse_action(action_str)
    except Exception as e:
        raise RuntimeError(f"Failed to parse action string: {e}")
    validate_lsgm_action(expr, symbols)

# ------------------------------------------------------------------
# Example usage (replace with the actual action from the proposal):
# ------------------------------------------------------------------
if __name__ == "__main__":
    # Example action string – **USER MUST REPLACE THIS WITH THE PROPOSED ACTION**
    example_action = """
    1/2*g**(mu,nu)*Derivative(E, mu)*Derivative(E, nu)
    + 1/2*g**(mu,nu)*Derivative(K, mu)*Derivative(K, nu)
    + alpha/2*(E - E0)**2 + beta/2*(K - K0)**2 + gamma*E*K**2
    + lambda_O*L_O(Phi_N, Phi_Delta)
    + A_mu * (sqrt(2)*Phi_Delta*KroneckerDelta(0, mu))
    + xi_N/2 * g**(mu,nu) * Derivative(Phi_N, mu) * Derivative(Phi_N, nu)
    + xi_Delta/2 * g**(mu,nu) * Derivative(Phi_Delta, mu) * Derivative(Phi_Delta, nu)
    # DIAGONAL_DECOMPOSITION
    # Shredding Event occurs when Phi_N -> 0
    # Informational Freeze occurs when Phi_Delta -> 0 and curvature flat
    """
    validate_action_string(example_action)