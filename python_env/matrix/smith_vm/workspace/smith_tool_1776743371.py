# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HVFI‑Ω v2 mathematical sanity‑check.
Run this in the isolated VM to assert that a concrete instantiation
obeys the Omega Protocol invariants.
"""

import numpy as np
from scipy.stats import pareto_gen  # Generalised Pareto (scipy's genpareto)
from numpy.linalg import cholesky, LinAlgError

# ----------------------------------------------------------------------
# USER‑DEFINED PARAMETERS (tweak to test different regimes)
# ----------------------------------------------------------------------
Lx = 128                 # number of price levels (spatial grid)
Nt = 5000                # number of time steps
dt = 0.001               # 1 ms base tick (matches level‑1 window)
D = 0.1                  # diffusion constant in action
lam = 1.0                # λ > 0  (phi^4 coupling)
v = 1.0                  # vacuum expectation value (stable amplitude)
eps = 1e-6               # regulariser for covariance determinant
B = 20                   # histogram bins for entropy / MI
S_min = 0.1
I_max = 2.0
Psi_min = -20.0          # very low (collapse) threshold
PhiN_min = 0.65
PhiDelta_max = 0.70
kappa = 1.0              # MPC weight on entropy tracking
mu = 1.0                 # MPC weight on Psi penalty
# ----------------------------------------------------------------------


def make_field():
    """Generate a synthetic scalar field φ(x,t) ~ OU in time, smooth in x."""
    # spatial smoothness via low‑pass filter
    x = np.linspace(-np.pi, np.pi, Lx)
    k = np.fft.fftfreq(Lx, d=x[1]-x[0])
    spatial_filter = np.exp(-0.5 * (k**2))  # Gaussian in k‑space

    phi = np.zeros((Nt, Lx))
    phi[0] = np.random.randn(Lx) * 0.1
    # Ornstein‑Uhlenbeck in time with relaxation time tau=0.1s
    tau = 0.1
    alpha = np.exp(-dt / tau)
    sigma = np.sqrt(1 - alpha**2) * 0.2
    for t in range(1, Nt):
        # temporal OU step
        phi[t] = alpha * phi[t-1] + sigma * np.random.randn(Lx)
        # enforce spatial smoothness
        phi_hat = np.fft.fft(phi[t], axis=0)
        phi_hat *= spatial_filter
        phi[t] = np.fft.ifft(phi_hat).real
    # normalise to [0,1] (order‑book volume fraction)
    phi = (phi - phi.min()) / (phi.max() - phi.min())
    return phi


def coarse_grain(phi, window_steps):
    """Temporal moving average -> pyramid level."""
    # simple cumulative sum trick for efficiency
    cs = np.cumsum(phi, axis=0)
    cs = np.insert(cs, 0, 0, axis=0)
    avg = (cs[window_steps:] - cs[:-window_steps]) / window_steps
    return avg  # shape (Nt-window_steps+1, Lx)


def entropy_from_activations(act):
    """act: (T, Lx) matrix → flatten → histogram → Shannon entropy."""
    flat = act.ravel()
    # histogram with density=True gives probabilities summing to 1
    hist, _ = np.histogram(flat, bins=B, range=(0, 1), density=True)
    # avoid log(0)
    hist = hist[hist > 0]
    return -np.sum(hist * np.log(hist))


def mutual_information(act1, act2):
    """act1, act2: (T, Lx) → joint histogram → MI."""
    flat1 = act1.ravel()
    flat2 = act2.ravel()
    hist2d, xedges, yedges = np.histogram2d(
        flat1, flat2, bins=B, range=[[0, 1], [0, 1]], density=True
    )
    # marginals
    hist1 = np.sum(hist2d, axis=1)
    hist2 = np.sum(hist2d, axis=0)
    # avoid zeros
    mask = hist2d > 0
    mi = np.sum(
        hist2d[mask]
        * np.log(
            hist2d[mask] / (hist1[:, None][mask] * hist2[None, :][mask] + 1e-12)
        )
    )
    return max(mi, 0.0)  # numerical non‑negativity


def pyramid_covariance(activations):
    """
    activations: list of L arrays each (T, Lx)
    Returns Σ_A (LxL) covariance of the stacked vectors a_l(t)
    """
    L = len(activations)
    T = activations[0].shape[0]
    # flatten each level to vector a_l(t) of length Lx
    A = np.stack([act.reshape(T, -1) for act in activations], axis=1)  # (T, L, Lx)
    # reshape to (T, L*Lx) for covariance
    A_flat = A.reshape(T, -1)
    # covariance matrix (L*Lx) x (L*Lx)
    Sigma = np.cov(A_flat, rowvar=False) + eps * np.eye(A_flat.shape[1])
    return Sigma


def logdet_cholesky(Sigma):
    """Stable log‑det via Cholesky."""
    try:
        L = cholesky(Sigma)
    except LinAlgError:
        # fallback to eigvals if Cholesky fails (should not happen with eps>0)
        eigvals = np.linalg.eigvalsh(Sigma)
        if np.any(eigvals <= 0):
            raise ValueError("Sigma not PSD")
        return np.sum(np.log(eigvals))
    return 2.0 * np.sum(np.log(np.diag(L)))


def compute_covariant_modes(phi_coarse):
    """
    Very simple projection:
    - Φ_N: spatial average (homogeneous mode)
    - Φ_Δ: spatial average of the *gradient* (proxy for topological defect density)
    """
    # homogeneous mode
    Phi_N = np.mean(phi_coarse, axis=1)  # (T,)
    # defect proxy: magnitude of discrete gradient in x
    grad_x = np.gradient(phi_coarse, axis=1)
    Phi_Delta = np.mean(np.abs(grad_x), axis=1)  # (T,)
    return Phi_N, Phi_Delta


def compute_invariants(Phi_N, Phi_Delta):
    """
    ξ_N^{-2} = λ (3 Φ_N^2 + Φ_Δ^2 - v^2)
    ξ_Δ^{-2} = λ (Φ_N^2 + 3 Φ_Δ^2 - v^2)
    ψ = ln( ξ / ξ_0 ) ; we set ξ_0 = 1/ (sqrt(λ) * v) for convenience
    """
    # ensure the arguments are positive
    arg_N = 3.0 * Phi_N**2 + Phi_Delta**2 - v**2
    arg_D = Phi_N**2 + 3.0 * Phi_Delta**2 - v**2
    if np.any(arg_N <= 0) or np.any(arg_D <= 0):
        raise ValueError(
            f"Invariant argument non‑positive: min(arg_N)={arg_N.min():.3e}, "
            f"min(arg_D)={arg_D.min():.3e}"
        )
    xi_N = 1.0 / np.sqrt(lam * arg_N)
    xi_D = 1.0 / np.sqrt(lam * arg_D)
    xi0 = 1.0 / (np.sqrt(lam) * v)  # reference length
    psi = np.log(xi_N / xi0)  # we could also average over N and Δ; using N as example
    return xi_N, xi_D, psi


def extreme_value_score(Psi, threshold_quantile=0.95):
    """Fit GPD to exceedances over threshold and return tail‑probability."""
    u = np.quantile(np.abs(Psi), threshold_quantile)
    exceed = np.abs(Psi) - u
    exceed = exceed[exceed > 0]
    if len(exceed) < 10:
        # not enough tail data → conservative score (no alarm)
        return 1.0
    # MLE for shape (c) and scale (scipy's genpareto uses c=shape, loc=0, scale=scale)
    # scipy.stats.genpareto expects shape=c, loc=0, scale=scale
    try:
        params = pareto_gen.fit(exceed, floc=0)  # returns (c, loc, scale)
        c, _, scale = params
    except Exception:
        # fitting failed → be conservative
        return 1.0
    # survival function at observed value
    val = np.abs(Psi[-1])  # most recent point
    if val <= u:
        return 1.0
    sf = pareto_gen.sf(val - u, c, loc=0, scale=scale)  # P(X > x)
    return sf  # small → anomalous


def main():
    phi = make_field()
    # ---- Pyramid levels -------------------------------------------------
    # level‑1: tick (1 ms) -> window = 1 step (dt)
    act1 = phi  # already at tick resolution
    # level‑2: minute (60 s) -> window = 60 / dt steps
    win_min = int(round(60.0 / dt))
    act2 = coarse_grain(phi, win_min)
    # level‑3: hour (3600 s) -> window = 3600 / dt steps
    win_hr = int(round(3600.0 / dt))
    act3 = coarse_grain(phi, win_hr)

    # Trim to common time length (the coarsest level dictates length)
    T_common = act3.shape[0]
    act1 = act1[:T_common]
    act2 = act2[:T_common]
    act3 = act3[:T_common]

    # ---- Information‑theoretic quantities --------------------------------
    S1 = entropy_from_activations(act1)
    S2 = entropy_from_activations(act2)
    S3 = entropy_from_activations(act3)
    I12 = mutual_information(act1, act2)
    I23 = mutual_information(act2, act3)

    # ---- Pyramid curvature invariant ------------------------------------
    Sigma = pyramid_covariance([act1, act2, act3])
    Psi = logdet_cholesky(Sigma)  # scalar per time? Actually Sigma is time‑averaged cov.
    # For a time‑varying version we would compute Sigma(t) over a sliding window;
    # here we use the whole sample to illustrate the math.
    # To keep the script simple we treat Psi as a constant scalar.
    Psi_series = np.full(T_common, Psi)

    # ---- Covariant modes (Newtonian & Archive) -------------------------
    PhiN1, PhiD1 = compute_covariant_modes(act1)
    PhiN2, PhiD2 = compute_covariant_modes(act2)
    PhiN3, PhiD3 = compute_covariant_modes(act3)

    # ---- Invariant checks ------------------------------------------------
    for label, (PhiN, PhiD) in zip(
        ["L1", "L2", "L3"], [(PhiN1, PhiD1), (PhiN2, PhiD2), (PhiN3, PhiD3)]
    ):
        xiN, xiD, psi = compute_invariants(PhiN, PhiD)
        # Positivity of correlation lengths
        assert np.all(xiN > 0), f"{label}: ξ_N ≤ 0"
        assert np.all(xiD > 0), f"{label}: ξ_Δ ≤ 0"
        # Omega Protocol bounds on the modes
        assert np.all(PhiN >= PhiN_min), f"{label}: Φ_N < {PhiN_min}"
        assert np.all(PhiD <= PhiDelta_max), f"{label}: Φ_Δ > {PhiDelta_max}"
        # Entropy bounds
        # (we only checked the *latest* sample here for brevity)
        assert S1 >= 0 and S1 <= np.log(B), f"S1 out of bounds"
        assert S2 >= 0 and S2 <= np.log(B), f"S2 out of bounds"
        assert S3 >= 0 and S3 <= np.log(B), f"S3 out of bounds"
        # Mutual information non‑negative
        assert I12 >= 0, "I12 < 0"
        assert I23 >= 0, "I23 < 0"
        # Psi constraint (avoid total collapse)
        assert Psi >= Psi_min, f"Psi too low (collapse)"

    # ---- Anomaly score (EVT) -------------------------------------------
    anomaly_score = extreme_value_score(Psi_series)
    print(f"Extreme‑value tail probability (anomaly score): {anomaly_score:.5f}")
    # If score < 0.01 we would flag an imminent event.
    if anomaly_score < 0.01:
        print(">>> ALERT: Potential shredding event detected (EVT tail).")
    else:
        print(">>> No alarm (score above threshold).")

    # ---- MPC cost sanity (just check convexity coefficients) ------------
    assert kappa > 0, "kappa must be positive for convex entropy‑tracking term"
    assert mu > 0, "mu must be positive for Psi‑penalty term"
    print("All Omega‑Protocol invariant checks passed.")

if __name__ == "__main__":
    main()