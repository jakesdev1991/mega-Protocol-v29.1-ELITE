# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# Constants
c = 299792.458  # km/s (speed of light)
# Consensus rounds needed for Byzantine fault tolerance (PBFT: pre‑prepare, prepare, commit)
ROUNDS = 3

def min_sync_time(distance_km: float) -> float:
    """Minimum time to achieve consensus across a given distance (one‑way per round)."""
    return ROUNDS * distance_km / c  # seconds

# Typical artillery separation distances (km)
distances = np.array([50, 100, 200, 300, 500, 1000])
# Required firing simultaneity precision (ms) for effective saturation fire
required_precision_ms = 1.0

print("Distance (km) | Min sync time (ms) | Feasible?")
for d in distances:
    t_ms = min_sync_time(d) * 1000
    feasible = t_ms <= required_precision_ms
    print(f"{d:>12} | {t_ms:>18.2f} | {feasible}")

# Demonstrate that even for a modest 200 km front, the latency exceeds 1 ms.
# At 200 km, t_ms ≈ 3 * 200 / 299792.458 * 1000 ≈ 2.00 ms > 1 ms → INFEASIBLE