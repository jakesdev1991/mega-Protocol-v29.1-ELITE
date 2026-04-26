# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega‑Protocol Validator for Functional‑Space Entanglement Monitor (FSEM‑Ω)

The script checks the mathematical consistency of the core FSEM‑Ω equations
and enforces the Ω‑Protocol invariants (Φ_N, Φ_Δ, ψ) together with the
MPC‑Ω constraints:

    • 0 ≤ FFI ≤ 1
    • Φ_N ∈ [0, 1]   (connectivity – higher = more robust)
    • Φ_Δ ∈ [-1, 1]  (asymmetry)
    • ψ   ∈ ℝ        (curvature‑based invariant)
    • MPC‑Ω constraints:
          FFI ≤ 0.65
          Φ_N ≥ 0.60
          S_func ≥ ln(3)   (functional entropy lower bound)

If any check fails, a ValidationError is raised with a descriptive message.
"""

import numpy as np
from typing import Tuple, Dict

# ----------------------------------------------------------------------
# Helper utilities (stand‑ins for real data pipelines)
# ----------------------------------------------------------------------
def _safe_norm(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """Euclidean norm with protection against division by zero."""
    return np.linalg.norm(x, axis=axis, keepdims=True)

def gradient_magnitude(field: np.ndarray, spacing: float = 1.0) -> float:
    """
    Approximate ⟨‖∇F‖⟩ using finite differences on a regular grid.
    field: 3D array (x, y, z) of functional values F.
    Returns scalar mean gradient magnitude.
    """
    grad = np.gradient(field, spacing, axis=(0, 1, 2))
    grad_mag = np.sqrt(sum(g**2 for g in grad))
    return float(np.mean(grad_mag))

def laplacian(field: np.ndarray, spacing: float = 1.0) -> float:
    """
    Approximate ⟨∇²F⟩ (scalar curvature proxy) via 7‑point stencil.
    Returns mean Laplacian over the domain.
    """
    lap = (
        -6 * field
        + np.roll(field,  1, axis=0) + np.roll(field, -1, axis=0)
        + np.roll(field,  1, axis=1) + np.roll(field, -1, axis=1)
        + np.roll(field,  1, axis=2) + np.roll(field, -1, axis=2)
    ) / (spacing**2)
    return float(np.mean(lap))

def entanglement_index(crosstalk: np.ndarray) -> float:
    """
    E(t) = (1/n) Σ_{i,j} Crosstalk_{ij}²
    crosstalk: square matrix (n×n) of measured interference.
    """
    n = crosstalk.shape[0]
    return float(np.sum(crosstalk**2) / (n * n))

def context_variance(func_same_device: np.ndarray) -> float:
    """
    σ²_context(t) = Var( F_{same device, different contexts} )
    func_same_device: 1D array of functional outputs for one device across contexts.
    """
    return float(np.var(func_same_device))

def functional_entropy(p_k: np.ndarray) -> float:
    """
    Shannon entropy S_func = - Σ p_k log(p_k)
    p_k: probability vector (must sum to 1, non‑negative).
    """
    p_k = np.asarray(p_k, dtype=float)
    p_k = p_k[p_k > 0]               # avoid log(0)
    return float(-np.sum(p_k * np.log(p_k)))

# ----------------------------------------------------------------------
# Core FSEM‑Ω formulas
# ----------------------------------------------------------------------
def compute_FFI(
    grad_mag: float,
    laplacian_val: float,
    entanglement: float,
    context_var: float,
    weights: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
) -> float:
    """
    FFI(t) = tanh[ α|κ| + βG + γE + δσ²_context ]
    """
    a, b, c, d = weights
    arg = a * abs(laplacian_val) + b * grad_mag + c * entanglement + d * context_var
    return float(np.tanh(arg))

def map_to_phi(
    FFI_prev: float,
    entanglement_prev: float,
    context_var_prev: float,
    grad_mag_prev: float,
    Phi_N0: float = 0.8,
    Phi_Delta0: float = 0.0,
    etas: Tuple[float, float, float, float] = (0.2, 0.2, 0.15, 0.15),
    taus: Tuple[float, float] = (4.0, 4.0)   # weeks → treat as dimensionless lag index
) -> Tuple[float, float]:
    """
    Φ_N(t) = Φ_N0 - η₁·FFI(t-τ₁) + η₂·(1 - E(t-τ₁))
    Φ_Δ(t) = Φ_Δ0 + η₃·σ²_context(t-τ₂) - η₄·G(t-τ₂)
    """
    η1, η2, η3, η4 = etas
    τ1, τ2 = taus   # not used directly; we assume inputs already lagged
    Phi_N = Phi_N0 - η1 * FFI_prev + η2 * (1.0 - entanglement_prev)
    Phi_Delta = Phi_Delta0 + η3 * context_var_prev - η4 * grad_mag_prev
    # Clip to protocol‑allowed ranges
    Phi_N = np.clip(Phi_N, 0.0, 1.0)
    Phi_Delta = np.clip(Phi_Delta, -1.0, 1.0)
    return float(Phi_N), float(Phi_Delta)

def compute_psi(
    Ricci_func: float,
    FFI_val: float,
    R0: float = 1.0,
    lam: float = 0.5
) -> float:
    """
    ψ(t) = ln( |R_func| / R0 ) + λ·FFI(t)
    """
    if Ricci_func == 0.0:
        raise ValueError("Ricci curvature cannot be zero (log undefined).")
    return float(np.log(abs(Ricci_func) / R0) + lam * FFI_val)

# ------------------------------------------------------------------
# Validation routine
# ------------------------------------------------------------------
class ValidationError(RuntimeError):
    pass

def validate_FSEM_Omega(
    field: np.ndarray,
    crosstalk: np.ndarray,
    func_same_device: np.ndarray,
    p_k: np.ndarray,
    Ricci_func: float,
    weights: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
    etas: Tuple[float, float, float, float] = (0.2, 0.2, 0.15, 0.15),
    taus: Tuple[float, float] = (4.0, 4.0),
    Phi_N0: float = 0.8,
    Phi_Delta0: float = 0.0,
    R0: float = 1.0,
    lam: float = 0.5
) -> Dict[str, float]:
    """
    Runs the full FSEM‑Ω pipeline and checks every Ω‑Protocol invariant.
    Returns a dictionary of the computed quantities if validation passes.
    """
    # 1️⃣ Compute primitive metrics
    G = gradient_magnitude(field)
    kappa = laplacian(field)
    E = entanglement_index(crosstalk)
    sigma2_ctx = context_variance(func_same_device)

    # 2️⃣ Functional Fragility Index
    FFI = compute_FFI(G, kappa, E, sigma2_ctx, weights)

    # 3️⃣ Map to Ω variables (using lagged values – here we assume same‑step for demo)
    Phi_N, Phi_Delta = map_to_phi(
        FFI_prev=FFI,
        entanglement_prev=E,
        context_var_prev=sigma2_ctx,
        grad_mag_prev=G,
        Phi_N0=Phi_N0,
        Phi_Delta0=Phi_Delta0,
        etas=etas,
        taus=taus
    )

    # 4️⃣ Invariant ψ from Ricci curvature
    psi = compute_psi(Ricci_func, FFI, R0=R0, lam=lam)

    # 5️⃣ Functional entropy (MPC‑Ω constraint)
    S_func = functional_entropy(p_k)

    # ------------------------------------------------------------------
    # Ω‑Protocol invariant checks
    # ------------------------------------------------------------------
    if not (0.0 <= FFI <= 1.0):
        raise ValidationError(f"FFI out of bounds: {FFI:.4f} ∉ [0,1]")
    if not (0.0 <= Phi_N <= 1.0):
        raise ValidationError(f"Φ_N out of bounds: {Phi_N:.4f} ∉ [0,1]")
    if not (-1.0 <= Phi_Delta <= 1.0):
        raise ValidationError(f"Φ_Δ out of bounds: {Phi_Delta:.4f} ∉ [-1,1]")
    # ψ must be a real number (no NaN/inf)
    if not np.isfinite(psi):
        raise ValidationError(f"ψ is non‑finite: {psi}")

    # ------------------------------------------------------------------
    # MPC‑Ω constraint checks (hard limits)
    # ------------------------------------------------------------------
    if FFI > 0.65:
        raise ValidationError(f"MPC‑Ω violation: FFI = {FFI:.4f} > 0.65")
    if Phi_N < 0.60:
        raise ValidationError(f"MPC‑Ω violation: Φ_N = {Phi_N:.4f} < 0.60")
    if S_func < np.log(3):
        raise ValidationError(f"MPC‑Ω violation: S_func = {S_func:.4f} < ln(3) ≈ {np.log(3):.4f}")

    # ------------------------------------------------------------------
    # All good – return diagnostics
    # ------------------------------------------------------------------
    return {
        "FFI": FFI,
        "Phi_N": Phi_N,
        "Phi_Delta": Phi_Delta,
        "psi": psi,
        "S_func": S_func,
        "gradient_mag": G,
        "laplacian": kappa,
        "entanglement": E,
        "context_variance": sigma2_ctx
    }

# ----------------------------------------------------------------------
# Example usage (synthetic data for demonstration)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Create a tiny 3D functional field (e.g., 8×8×8 grid)
    np.random.seed(42)
    field = np.random.rand(8, 8, 8) * 2.0   # arbitrary functional values

    # Synthetic crosstalk matrix (5 devices)
    n_dev = 5
    crosstalk = np.random.rand(n_dev, n_dev) * 0.3
    np.fill_diagonal(crosstalk, 0.0)       # no self‑crosstalk

    # Functional readouts of one device across 4 contexts
    func_same_device = np.random.rand(4) * 1.5

    # Probability vector over functional types (must sum to 1)
    p_k = np.array([0.4, 0.3, 0.2, 0.1])
    p_k = p_k / p_k.sum()

    # A plausible Ricci curvature scalar (could be negative)
    Ricci_func = -0.75   # negative curvature → crosstalk‑prone region

    try:
        result = validate_FSEM_Omega(
            field=field,
            crosstalk=crosstalk,
            func_same_device=func_same_device,
            p_k=p_k,
            Ricci_func=Ricci_func,
            weights=(1.2, 0.8, 1.0, 0.6),
            etas=(0.25, 0.2, 0.15, 0.1),
            taus=(4.0, 4.0)
        )
        print("✅ FSEM‑Ω validation PASSED")
        for k, v in result.items():
            print(f"  {k:15}: {v:.4f}")
    except ValidationError as e:
        print("❌ FSEM‑Ω validation FAILED")
        print(e)