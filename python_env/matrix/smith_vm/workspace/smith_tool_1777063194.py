# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for SOUL-N (Self‑Optimizing Urban Logistics Nexus)

Inputs (to be provided by the calling system):
    obs_times   : list/np.ndarray of observation timestamps (s)
    dec_times   : list/np.ndarray of decision timestamps (s)
    dec_routes  : list of lists, each inner list = route edge IDs chosen at that decision
    actual_delays: list/np.ndarray of observed delay (s) for each decision
    vehicle_positions: np.ndarray shape (N,3) of vehicle coordinates (m) at a common snapshot
    max_causal_speed: float, maximum speed of causal influence (m/s)
    initial_entropy: float, Shannon entropy of baseline delay distribution (bits)
    entropy_bins : list/np.ndarray of bin edges for delay discretisation

Outputs:
    dict with keys 'Phi1', 'Phi2', 'Phi3' -> bool (True = invariant satisfied)
    plus optional diagnostic strings.
"""

import numpy as np
from scipy.spatial.distance import pdist, squareform

# Optional: persistent homology via ripser (if available)
try:
    from ripser import ripser
    HAVE_RIPSER = True
except Exception:  # pragma: no cover
    HAVE_RIPSER = False

def shannon_entropy(samples, bins):
    """Compute Shannon entropy (base 2) of samples binned by `bins`."""
    hist, _ = np.histogram(samples, bins=bins, density=True)
    # Remove zero probabilities to avoid log2(0)
    hist = hist[hist > 0]
    return -np.sum(hist * np.log2(hist))

def causal_fidelity(obs_times, dec_times, max_causal_speed, positions=None):
    """
    Φ‑1: Ensure no decision precedes the earliest possible causal influence.
    If `positions` and sensor locations are known we could compute exact light‑cone,
    but a conservative check is: decision time >= observation time + min_latency,
    where min_latency = 0 (i.e., decision cannot be *before* observation).
    Here we simply enforce dec_times >= obs_times (element‑wise) and
    optionally add a propagation delay based on max distance / max_causal_speed.
    """
    obs = np.asarray(obs_times)
    dec = np.asarray(dec_times)
    if obs.shape != dec.shape:
        raise ValueError("obs_times and dec_times must have same length")
    # Basic causality: decision cannot be earlier than observation
    if np.any(dec < obs):
        return False, "Some decisions precede their observations (retrocausal)."
    # If we have sensor positions we could add a propagation term:
    if positions is not None:
        # Assume each observation corresponds to the nearest sensor;
        # compute max distance to any sensor (conservative)
        dists = pdist(positions)
        max_dist = np.max(dists) if len(dists) > 0 else 0.0
        min_prop = max_dist / max_causal_speed
        if np.any(dec < obs + min_prop):
            return False, f"Decision too fast: need ≥ {min_prop:.3f}s propagation delay."
    return True, "Causal fidelity satisfied."

def entropy_conservation(actual_delays, initial_entropy, entropy_bins, tolerance=0.025):
    """
    Φ‑2: Total entropy ≤ initial + 2.5%.
    Compute Shannon entropy of the observed delay distribution.
    """
    H_final = shannon_entropy(np.asarray(actual_delays), entropy_bins)
    allowed = initial_entropy * (1.0 + tolerance)
    return H_final <= allowed + 1e-12, f"H_final={H_final:.4f} bits, allowed={allowed:.4f} bits."

def topological_integrity(vehicle_positions):
    """
    Φ‑3: Logistics mesh homotopy‑equivalent to a 3‑torus.
    We compute Betti numbers β0,β1,β2,β3 via Vietoris‑Rips filtration.
    For a perfect 3‑torus: β0=1, β1=3, β2=3, β3=1.
    We allow a small deviation due to noise (±1 in each Betti).
    """
    if not HAVE_RIPSER:
        return False, "ripser library not installed; cannot compute persistent homology."
    # ripser expects a point cloud; we compute distance matrix
    dist_matrix = squareform(pdist(vehicle_positions, metric='euclidean'))
    # Ripser works with distance matrix if distance_matrix=True
    diagrams = ripser(dist_matrix, distance_matrix=True, maxdim=3)['dgms']
    # diagrams[i] -> list of [birth, death] for H_i
    betti = []
    for i in range(4):
        dgm = diagrams[i] if i < len(diagrams) else np.empty((0,2))
        # Count intervals that persist (death > birth + eps)
        eps = 1e-6
        pers = np.sum(dgm[:,1] - dgm[:,0] > eps) if dgm.size > 0 else 0
        betti.append(pers)
    expected = [1, 3, 3, 1]
    ok = all(abs(b - e) <= 1 for b, e in zip(betti, expected))
    msg = f"Betti numbers computed: {betti} (expected {expected} ±1)."
    return ok, msg

def validate_soul_n(obs_times, dec_times, dec_routes, actual_delays,
                    vehicle_positions, max_causal_speed,
                    initial_entropy, entropy_bins):
    """Run all three invariant checks."""
    results = {}
    # Φ‑1
    phi1, msg1 = causal_fidelity(obs_times, dec_times, max_causal_speed,
                                 positions=vehicle_positions)
    results['Phi1'] = phi1
    # Φ‑2
    phi2, msg2 = entropy_conservation(actual_delays, initial_entropy, entropy_bins)
    results['Phi2'] = phi2
    # Φ‑3
    phi3, msg3 = topological_integrity(vehicle_positions)
    results['Phi3'] = phi3
    # Diagnostics
    results['diagnostics'] = {
        'Phi1': msg1,
        'Phi2': msg2,
        'Phi3': msg3
    }
    return results

# ----------------------------------------------------------------------
# Example usage (replace with real data from the SOUL‑N system):
if __name__ == "__main__":
    # Dummy data for illustration only
    obs_times = np.array([0.0, 1.0, 2.0, 3.0])          # s
    dec_times = np.array([0.2, 1.2, 2.2, 3.2])          # s (always after obs)
    dec_routes = [['A','B','C'], ['B','C','D'], ['C','D','E'], ['D','E','F']]
    actual_delays = np.array([12.3, 11.8, 13.0, 12.5])  # s
    # Random vehicle positions in a 100m cube (just to have something)
    vehicle_positions = np.random.uniform(0, 100, size=(20, 3))
    max_causal_speed = 2e8  # m/s (≈ speed of light in fibre)
    initial_entropy = shannon_entropy(np.array([10,12,11,13,12,11]), bins=np.arange(8,16,1))
    entropy_bins = np.arange(8, 16, 1)  # delay bins in seconds

    val = validate_soul_n(obs_times, dec_times, dec_routes, actual_delays,
                          vehicle_positions, max_causal_speed,
                          initial_entropy, entropy_bins)
    print("Invariant check results:")
    for k in ['Phi1','Phi2','Phi3']:
        print(f"  {k}: {val[k]}  ({val['diagnostics'][k]})")