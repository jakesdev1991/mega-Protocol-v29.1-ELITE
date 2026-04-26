# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator
----------------------------------
Input:  proposal (dict) with the following optional keys:
    - 'action'          : str or sympy expression representing the Omega Action S[φ]
    - 'phi_N'           : expression for Newtonian mode Φ_N
    - 'phi_Delta'       : expression for Asymmetry mode Φ_Δ
    - 'invariants'      : dict with keys 'psi', 'xi_N', 'xi_Delta'
    - 'boundaries'      : dict with keys 'shredding', 'freeze'
    - 'entropy'         : expression for Shannon entropy or topological impedance
    - 'eom'             : list of equations of motion (str or sympy)
    - 'derivation'      : description of how eom follows from action (optional)

Output: (pass_bool, diagnostics_list)
"""

import sympy as sp
from typing import Any, Dict, List, Tuple

def _has_key(d: Dict, *keys) -> bool:
    return all(k in d for k in keys)

def _is_derived_from_action(action: Any, target: Any) -> bool:
    """
    Very light‑weight check: does `target` contain a term that looks like
    ∂S/∂φ (Euler‑Lagrange) or δS/δφ? We look for the pattern
    sp.diff(action, phi) or sp.Function('deltaS') etc.
    """
    if not isinstance(action, sp.Expr):
        return False
    # Symbolic differentiation w.r.t. any field symbol present in action
    field_symbols = [s for s in action.free_symbols if s.name.startswith('phi')]
    for phi in field_symbols:
        EL = sp.diff(action, phi) - sp.diff(sp.diff(action, sp.Derivative(phi, sp.Symbol('t'))), sp.Symbol('t'))
        # Check if target contains EL (structurally) – simple string fallback
        if str(EL) in str(target):
            return True
    return False

def validate_omega_proposal(proposal: Dict[str, Any]) -> Tuple[bool, List[str]]:
    diag = []
    pass_all = True

    # 1. Covariant decomposition -------------------------------------------------
    if not (_has_key(proposal, 'phi_N', 'phi_Delta') and
            isinstance(proposal['phi_N'], sp.Expr) and
            isinstance(proposal['phi_Delta'], sp.Expr)):
        diag.append("Missing or non‑symbolic Φ_N / Φ_Δ definitions.")
        pass_all = False
    else:
        # Require that they be expressed as background + perturbation from an action
        if not _has_key(proposal, 'action'):
            diag.append("No Omega Action provided – cannot verify covariant split.")
            pass_all = False
        else:
            act = proposal['action']
            # Check that each mode contains a term derivable from the action
            if not (_is_derived_from_action(act, proposal['phi_N']) and
                    _is_derived_from_action(act, proposal['phi_Delta'])):
                diag.append("Φ_N / Φ_Δ not shown to arise from action variation (missing eigen‑mode projection).")
                pass_all = False

    # 2. Invariants --------------------------------------------------------------
    if not _has_key(proposal, 'invariants'):
        diag.append("Invariants block (psi, xi_N, xi_Delta) absent.")
        pass_all = False
    else:
        inv = proposal['invariants']
        required = {'psi', 'xi_N', 'xi_Delta'}
        missing = required - set(inv.keys())
        if missing:
            diag.append(f"Missing invariant definitions: {', '.join(missing)}.")
            pass_all = False
        else:
            # Quick sanity: psi should be ln of a scalar field
            psi_expr = inv['psi']
            if not (isinstance(psi_expr, sp.Expr) and
                    any(str(psi_expr).startswith('log') or 'ln' in str(psi_expr) for _ in [0])):
                diag.append("ψ does not appear as ln(φ_n) or equivalent.")
                pass_all = False

    # 3. Boundaries --------------------------------------------------------------
    if not _has_key(proposal, 'boundaries'):
        diag.append("Boundaries (Shredding Event / Informational Freeze) not defined.")
        pass_all = False
    else:
        bd = proposal['boundaries']
        if 'shredding' not in bd or 'freeze' not in bd:
            diag.append("Both shredding and freeze horizons must be present.")
            pass_all = False
        else:
            # Boundaries must be expressed via invariants
            for name, expr in bd.items():
                if not isinstance(expr, sp.Expr):
                    diag.append(f"Boundary '{name}' is not a symbolic expression.")
                    pass_all = False
                    continue
                # crude check: expression should contain at least one invariant symbol
                inv_symbols = [str(v) for v in proposal['invariants'].values()]
                if not any(sym in str(expr) for sym in inv_symbols):
                    diag.append(f"Boundary '{name}' does not appear to be a function of the invariants.")
                    pass_all = False

    # 4. Entropy -----------------------------------------------------------------
    if not _has_key(proposal, 'entropy'):
        diag.append("Entropy gauge (Shannon or topological impedance) missing.")
        pass_all = False
    else:
        ent = proposal['entropy']
        if not isinstance(ent, sp.Expr):
            diag.append("Entropy entry is not a symbolic expression.")
            pass_all = False
        else:
            # Look for Shannon form -∑ p_i log p_i (we approximate by presence of log and sum)
            if 'log' not in str(ent) and 'ln' not in str(ent):
                diag.append("Entropy does not contain a logarithmic term; unlikely Shannon form.")
                pass_all = False

    # 5. Equation‑level derivation ------------------------------------------------
    if not _has_key(proposal, 'eom'):
        diag.append("No equations of motion supplied.")
        pass_all = False
    else:
        eoms = proposal['eom'] if isinstance(proposal['eom'], list) else [proposal['eom']]
        derived_any = False
        for eq in eoms:
            if _is_derived_from_action(proposal.get('action', sp.S(0)), eq):
                derived_any = True
                break
        if not derived_any:
            diag.append("At least one EoM must be traceable to the Omega Action via variational principle.")
            pass_all = False

    return pass_all, diag


# -------------------------------------------------------------------------------
# Example usage (replace with real proposal dict when auditing):
if __name__ == "__main__":
    # Mock deficient proposal (similar to the critiqued ISS‑Ω)
    mock_proposal = {
        # action omitted on purpose -> will fail covariant check
        "phi_N": sp.Symbol('Phi_N0') + sp.tanh(sp.Symbol('ISI')),
        "phi_Delta": sp.Symbol('Phi_Delta0') + sp.Symbol('ISI')**2,
        "invariants": {},                     # empty -> fail
        "boundaries": {},                     # empty -> fail
        "entropy": sp.Symbol('Gini'),         # not Shannon -> fail
        "eom": [sp.Eq(sp.Symbol('Phi_N'), sp.Symbol('Phi_N0'))],  # no derivation
    }

    passed, messages = validate_omega_proposal(mock_proposal)
    print("OMEGA VALIDATION RESULT:", "PASS" if passed else "FAIL")
    for m in messages:
        print(" -", m)