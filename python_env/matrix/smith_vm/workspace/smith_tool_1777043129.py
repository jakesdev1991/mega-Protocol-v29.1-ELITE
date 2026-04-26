# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Invariant Validator for COAGN (Causal‑Optimized Artillery Governance Nexus)
------------------------------------------------------------------------------------
Checks the three Absolute Invariants (Φ‑1, Φ‑2, Φ‑3) that any submission must satisfy.
If all return True, the proposal is *invariant‑compliant*; otherwise it fails.

Dependencies: numpy, scipy (for persistent homology via ripser), scikit‑learn (for entropy).
Install with: pip install numpy scipy scikit-learn ripser
"""

import numpy as np
from scipy.spatial.distance import pdist, squareform
from sklearn.neighbors import KernelDensity
from ripser import ripser
from persim import plot_diagrams  # optional, for visual debugging

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def causal_fidelity(sensor_stream, firing_vectors, dt, c_local=1.0):
    """
    Φ‑1: No decision propagates faster than local causal speed.
    sensor_stream: list of dicts (unused here, just for length)
    firing_vectors: np.ndarray shape (T, D)
    dt: time step between consecutive entries
    c_local: maximal allowed speed (set to 1.0 in normalized units)
    Returns True if max finite‑difference speed <= c_local.
    """
    v = np.asarray(firing_vectors)
    if v.ndim != 2:
        raise ValueError("firing_vectors must be (T, D)")
    diff = np.linalg.norm(v[1:] - v[:-1], axis=1) / dt
    return np.all(diff <= c_local + 1e-12)  # tiny tolerance for FP error


def informational_mass_conservation(initial_deviation_samples,
                                    current_deviation_samples,
                                    max_extra_frac=0.03):
    """
    Φ‑2: Shannon entropy of firing‑deviation distribution may grow at most
    `max_extra_frac` (3 %) over the initial entropy.
    Samples are 1‑D arrays of scalar deviation metrics (e.g., miss distance).
    Uses a KDE to estimate differential entropy.
    """
    def entropy_from_samples(samples):
        # Reshape for KDE
        X = np.atleast_2d(samples).T
        kde = KernelDensity(bandwidth='scott', kernel='gaussian')
        kde.fit(X)
        # Differential entropy approximation: -∫ p log p ≈ -mean(log p)
        log_dens = kde.score_samples(X)
        return -np.mean(log_dens)

    H0 = entropy_from_samples(np.asarray(initial_deviation_samples))
    Ht = entropy_from_samples(np.asarray(current_deviation_samples))
    return Ht <= H0 * (1.0 + max_extra_frac + 1e-12)


def topological_integrity(turret_positions):
    """
    Φ‑3: Configuration space of turrets must stay homotopy‑equivalent to T³.
    We compute Betti numbers via Vietoris‑Rips persistence (using ripser).
    For a 3‑torus we expect β0=1, β1=3, β2=3, β3=1.
    Tolerates small noise: we allow ±1 on each Betti number.
    """
    # turret_positions: list/array shape (T, N, 3) -> flatten time dimension
    T, N, _ = np.asarray(turret_positions).shape
    points = np.asarray(turret_positions).reshape(T * N, 3)  # point cloud
    # Compute persistence up to dimension 3
    diagrams = ripser(points, maxdim=3)['dgms']
    betti = [np.isfinite(dgm).sum() for dgm in diagrams]  # count finite intervals
    # Ensure we have at least 4 dimensions (pad with zeros)
    while len(betti) < 4:
        betti.append(0)
    expected = [1, 3, 3, 1]
    tol = 1  # allow one extra/missing feature due to sampling noise
    return all(abs(b - e) <= tol for b, e in zip(betti, expected))


# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def validate_coagn(sensor_stream,
                   firing_vectors,
                   dt,
                   initial_deviation_samples,
                   current_deviation_samples,
                   turret_positions):
    """
    Returns a dict with the result of each invariant and an overall flag.
    All inputs must be provided by the caller (simulated or logged data).
    """
    results = {}
    results['Phi_1_causal_fidelity'] = causal_fidelity(
        sensor_stream, firing_vectors, dt)
    results['Phi_2_informational_mass'] = informational_mass_conservation(
        initial_deviation_samples, current_deviation_samples)
    results['Phi_3_topological_integrity'] = topological_integrity(turret_positions)

    results['overall_compliant'] = all(results.values())
    return results


# ----------------------------------------------------------------------
# Example usage (mock data) – replace with real logs in the VM
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Mock parameters – in a real audit these come from system logs
    T = 200                     # timesteps
    N = 9                       # turrets (3×3 grid)
    D = 3                       # firing vector dimension (e.g., azimuth, elevation, power)
    dt = 0.05                   # 50 ms control cycle

    # Simulated sensor stream (placeholder)
    sensor_stream = [{'time': t*dt} for t in range(T)]

    # Simulated firing vectors: slow‑varying, well below causal speed
    t = np.arange(T) * dt
    firing_vectors = np.stack([
        0.1 * np.sin(0.5 * t),          # azimuth
        0.1 * np.cos(0.3 * t),          # elevation
        0.5 + 0.05 * np.sin(0.2 * t)    # power
    ], axis=1)

    # Deviation samples: scalar miss‑distance (m)
    rng = np.random.default_rng(42)
    initial_deviation_samples = rng.normal(loc=0.0, scale=0.5, size=500)
    current_deviation_samples = rng.normal(loc=0.0, scale=0.55, size=500)  # slight increase

    # Turret positions: a 3×3 grid that slowly rotates (preserves T³ topology)
    xs = np.linspace(-10, 10, 3)
    ys = np.linspace(-10, 10, 3)
    xx, yy = np.meshgrid(xs, ys)
    base = np.stack([xx.ravel(), yy.ravel(), np.zeros_like(xx.ravel())], axis=1)  # (N,3)
    angles = 0.02 * t  # slow rotation about Z
    rot_mats = np.array([
        [[np.cos(a), -np.sin(a), 0],
         [np.sin(a),  np.cos(a), 0],
         [0,          0,         1]]
        for a in angles
    ])  # (T,3,3)
    turret_positions = np.einsum('tij,nj->tni', rot_mats, base)  # (T,N,3)

    # Run validation
    report = validate_coagn(
        sensor_stream=sensor_stream,
        firing_vectors=firing_vectors,
        dt=dt,
        initial_deviation_samples=initial_deviation_samples,
        current_deviation_samples=current_deviation_samples,
        turret_positions=turret_positions
    )

    print("Omega‑Protocol Invariant Validation Report:")
    for k, v in report.items():
        print(f"  {k}: {v}")