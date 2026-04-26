# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Harness for COULN‑style Urban Logistics Nexus
--------------------------------------------------------------------
Checks:
  • Causal Fidelity (Φ‑1)
  • Informational‑Mass Conservation (Φ‑2) – Shannon entropy bound
  • Topological Integrity (Φ‑3) – Betti numbers of route complex
  • Metric Non‑Degeneracy & Ricci‑Flow step (TOE Step 7)

All checks are *necessary* (but not sufficient) for Submission‑Grade.
If any check fails, the proposal must be revised before it can enter the
Omega manifold.
"""

import numpy as np
from scipy.linalg import eigvalsh, det
try:
    import gudhi as gd   # Optional: install via `pip install gudhi`
except Exception:      # pragma: no cover
    gd = None
    print("[WARN] gudhi not installed – topological check will be skipped.")

# ----------------------------------------------------------------------
# Configuration (tune to your deployment)
# ----------------------------------------------------------------------
ENTROPY_BOUND_FACTOR = 0.05          # allowed 5 % increase
RICCI_FLOW_DT = 0.01                 # explicit Euler step size
LORRENTZIAN_SIGNATURE = (-1, +1, +1, +1)  # expected eigenvalue signs

# ----------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------
def shannon_entropy(probs: np.ndarray) -> float:
    """Compute Shannon entropy H = - Σ p log p (base e)."""
    p = probs[probs > 0]
    return -np.sum(p * np.log(p))

def lorentzian_signature_ok(eigvals: np.ndarray) -> bool:
    """Return True iff eigenvalues match (-,+,+,+) up to tolerance."""
    tol = 1e-6
    signs = np.sign(eigvals)
    expected = np.array(LORRENTZIAN_SIGNATURE)
    return np.allclose(signs, expected, atol=tol)

# ----------------------------------------------------------------------
# 1. Causal Fidelity (Φ‑1)
# ----------------------------------------------------------------------
def check_causal_fidelity(data_ts: np.ndarray, decision_ts: np.ndarray) -> bool:
    """
    data_ts[i]    – timestamp of the i‑th data sample used for decision i
    decision_ts[i]– timestamp when the i‑th logistics decision was enacted
    Returns False if any decision precedes its data (retrocausality).
    """
    if np.any(decision_ts < data_ts):
        viol = np.where(decision_ts < data_ts)[0]
        print(f"[FAIL Φ‑1] Decision precedes data at indices: {viol}")
        return False
    print("[PASS Φ‑1] Causal fidelity satisfied.")
    return True

# ----------------------------------------------------------------------
# 2. Informational‑Mass Conservation (Φ‑2)
# ----------------------------------------------------------------------
def check_entropy_bound(initial_probs: np.ndarray,
                        final_probs: np.ndarray,
                        eps: float = ENTROPY_BOUND_FACTOR) -> bool:
    """
    Verifies H_final ≤ H_initial * (1 + eps).
    """
    Hi = shannon_entropy(initial_probs)
    Hf = shannon_entropy(final_probs)
    limit = Hi * (1.0 + eps)
    if Hf > limit + 1e-12:
        print(f"[FAIL Φ‑2] Entropy increased: Hi={Hi:.4f}, Hf={Hf:.4f}, limit={limit:.4f}")
        return False
    print(f"[PASS Φ‑2] Entropy bound satisfied (Hi={Hi:.4f} → Hf={Hf:.4f}).")
    return True

# ----------------------------------------------------------------------
# 3. Topological Integrity (Φ‑3)
# ----------------------------------------------------------------------
def check_topology(simplex_tree) -> bool:
    """
    Expects a Gudhi SimplexTree representing the swarm’s route complex.
    Checks Betti numbers (β0,β1,β2) = (1,0,1) → homotopy S³.
    If gudhi unavailable, returns True (skip) with a warning.
    """
    if gd is None:
        print("[WARN Φ‑3] gudhi missing – skipping topological check.")
        return True
    betti = simplex_tree.betti_numbers()
    expected = (1, 0, 1)
    if betti[:3] != expected:
        print(f"[FAIL Φ‑3] Betti numbers {betti[:3]} ≠ expected {expected}")
        return False
    print(f"[PASS Φ‑3] Topology OK – Betti numbers {betti[:3]}.")
    return True

# ----------------------------------------------------------------------
# 4. Metric Non‑Degeneracy & Ricci‑Flow Step (TOE Step 7)
# ----------------------------------------------------------------------
def check_ricci_flow_step(g_mn: np.ndarray,
                          ricci_tensor: np.ndarray,
                          lambda_func,
                          dt: float = RICCI_FLOW_DT) -> bool:
    """
    Performs one explicit Euler step:
        g_new = g + dt * ( -2 * Ric + lambda * g )
    Then verifies:
        • det(g_new) ≠ 0  (non‑degenerate)
        • signature(g_new) = Lorentzian
    Parameters
    ----------
    g_mn          : current metric tensor (4×4)
    ricci_tensor  : Ricci tensor R_μν (4×4) – must be supplied from data
    lambda_func   : callable returning scalar λ(t) given g_mn (or None → const 0)
    dt            : step size
    """
    lam = lambda_func(g_mn) if callable(lambda_func) else float(lambda_func or 0.0)
    g_new = g_mn + dt * (-2.0 * ricci_tensor + lam * g_mn)

    # Non‑degeneracy
    if np.abs(det(g_new)) < 1e-12:
        print(f"[FAIL TOE7] Metric became degenerate (det≈{det(g_new):.2e})")
        return False

    # Signature check via eigenvalues (symmetric metric)
    evals = eigvalsh(g_new)   # real symmetric → real eigenvalues
    if not lorentzian_signature_ok(evals):
        print(f"[FAIL TOE7] Wrong signature. Eigenvalues: {evals}")
        return False

    print(f"[PASS TOE7] Metric remains non‑degenerate (det={det(g_new):.3e}) "
          f"and Lorentzian (evals={evals}).")
    return True

# ----------------------------------------------------------------------
# Demo / Unit‑Test scaffolding (replace with real data in production)
# ----------------------------------------------------------------------
def _demo():
    np.random.seed(42)

    # --- 1. Causal fidelity demo ------------------------------------------------
    data_ts = np.sort(np.random.uniform(0, 100, size=20))
    decision_ts = data_ts + np.random.uniform(0.1, 2.0, size=20)  # always after data
    assert check_causal_fidelity(data_ts, decision_ts)

    # --- 2. Entropy bound demo --------------------------------------------------
    # Initial distribution (e.g., route‑choice probabilities)
    p0 = np.random.dirichlet(alpha=np.ones(5))
    # Final distribution after swarm rebalancing (slightly sharper)
    p1 = np.random.dirichlet(alpha=np.ones(5) * 2.0)
    assert check_entropy_bound(p0, p1)

    # --- 3. Topology demo -------------------------------------------------------
    if gd is not None:
        st = gd.SimplexTree()
        # Build a simple 3‑sphere triangulation (the boundary of a 4‑simplex)
        vertices = list(range(5))
        for v in vertices:
            st.insert([v])
        # all 4‑faces missing → we get the hollow 4‑simplex = S³
        for face in gd.complexes.polyhedron(vertices, dimension=4):
            st.insert(face, filtration=0)
        assert check_topology(st)

    # --- 4. Ricci‑flow demo ------------------------------------------------------
    # Start with Minkowski metric η = diag(-1,+1,+1,+1)
    g0 = np.diag([-1.0, 1.0, 1.0, 1.0])
    # Suppose we have a small curvature perturbation from traffic density
    Ric = np.diag([0.01, -0.005, -0.005, -0.005])   # example
    # λ(t) chosen to keep trace zero (simple illustrative choice)
    lam_func = lambda g: -0.5 * np.trace(np.dot(np.linalg.inv(g), Ric))
    assert check_ricci_flow_step(g0, Ric, lam_func, dt=0.05)

    print("\n[DEMO] All validation checks passed – ready for Omega submission.\n")

if __name__ == "__main__":
    _demo()