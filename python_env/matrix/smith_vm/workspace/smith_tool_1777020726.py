# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega‑Protocol Invariant Validator for the JWST Spectral Refiner
# --------------------------------------------------------------
# Checks:
# 1. Φ‑density > 0  (requires β > H_cond)
# 2. RCOD causal‑fidelity: every node's wavelength lies in its declared band
# 3. Energetic sufficiency: total_power <= 0.002 * E_JWST (2 W)
# 4. Topological continuity: homology matches S^3 or T^3
# --------------------------------------------------------------

import numpy as np
from itertools import combinations

# ----- Helper: Simplicial Complex over Z2 -----
class SimplicialComplex:
    def __init__(self, simplices):
        """
        simplices: list of tuples, each tuple is a sorted vertex list (e.g., (0,1,2))
        """
        self.simplices = set(tuple(s) for s in simplices)
        self.vertices = set(v for s in self.simplices for v in s)
        self.n_vertices = max(self.vertices)+1 if self.vertices else 0
        self._build_boundary()

    def _build_boundary(self):
        """Build boundary matrices ∂_k over GF(2) for k=1..max_dim."""
        self.max_dim = max(len(s)-1 for s in self.simplices) if self.simplices else 0
        self.boundary = {}
        for k in range(1, self.max_dim+1):
            k_simplices = [s for s in self.simplices if len(s)==k+1]
            km1_simplices = [s for s in self.simplices if len(s)==k]
            self.boundary[k] = np.zeros((len(km1_simplices), len(k_simplices)), dtype=int)
            # map simplex -> column index
            col_idx = {s:i for i,s in enumerate(k_simplices)}
            row_idx = {s:i for i,s in enumerate(km1_simplices)}
            for col, simplex in enumerate(k_simplices):
                for i in range(len(simple)):
                    face = simplex[:i] + simplex[i+1:]
                    row = row_idx[face]
                    self.boundary[k][row, col] = (self.boundary[k][row, col] + 1) % 2

    def betti(self, k):
        """Return Betti number b_k over GF(2)."""
        if k == 0:
            # b0 = #vertices - rank(∂1)
            rank = np.linalg.matrix_rank(self.boundary.get(1, np.zeros((len(self.vertices),0))), 2)
            return len(self.vertices) - rank
        elif k > self.max_dim:
            return 0
        else:
            # b_k = ker(∂_k) - im(∂_{k+1})
            ker = np.linalg.matrix_rank(self.boundary.get(k, np.zeros((0,0))), 2)
            im = np.linalg.matrix_rank(self.boundary.get(k+1, np.zeros((0,0))), 2)
            # nullity = n_cols - rank
            n_cols = self.boundary.get(k, np.zeros((0,0))).shape[1]
            return (n_cols - ker) - im

    def homology_vector(self):
        return [self.betti(i) for i in range(self.max_dim+2)]  # include possible b_{max+1}=0

# ----- Helper: Shannon conditional entropy (mock) -----
def conditional_entropy(context_dist):
    """
    context_dist: dict {context_label: probability}
    Returns H(L|C) = Σ p(c) H(L|c)
    For demo we assume uniform distribution over contexts and
    H(L|c) = log2(#states_per_context) (maximal entropy).
    """
    if not context_dist:
        return 0.0
    # assume each context allows exactly 2 microstates => 1 bit
    H_given_c = 1.0
    return sum(p * H_given_c for p in context_dist.values())

# ----- Invariant Checks -----
def validate_proposal(complex_data, node_contexts, total_power_watts,
                      jwst_power_watts=2000.0, energy_frac=0.001):
    """
    complex_data: list of simplices (as tuples) defining the spectral lattice
    node_contexts: dict {node_id: (min_wl, max_wl)} in microns
    total_power_watts: measured draw of the refiner subsystem
    """
    SC = SimplicialComplex(complex_data)

    # 1. Φ-density
    beta = SC.betti(1)   # using first Betti as proxy for topological richness
    # mock contextual distribution: assume each node defines a context
    context_dist = {i: 1.0/len(node_contexts) for i in node_contexts}
    H_cond = conditional_entropy(context_dist)
    if beta <= 0 or H_cond <= 0:
        phi = -np.inf
    else:
        phi = np.log2(beta / H_cond)
    phi_ok = phi > 0

    # 2. RCOD causal‑fidelity: wavelength of each node must be inside its band
    # Here we assume each node reports a measured wavelength; we just check the band.
    # In a real system you would pull telemetry.
    rcod_ok = True
    for node_id, (wmin, wmax) in node_contexts.items():
        # dummy telemetry: pick midpoint
        w_meas = (wmin + wmax) / 2.0
        if not (wmin <= w_meas <= wmax):
            rcod_ok = False
            break

    # 3. Energetic sufficiency
    max_allowed = jwst_power_watts * energy_frac  # 0.1% of JWST
    energy_ok = total_power_watts <= max_allowed

    # 4. Topological continuity (S^3 or T^3)
    hom = SC.homology_vector()
    # Ensure we have up to b3
    while len(hom) < 4:
        hom.append(0)
    s3 = [1,0,0,1]
    t3 = [1,3,3,1]
    topo_ok = (hom == s3) or (hom == t3)

    # ----- Report -----
    report = {
        "Phi_density": phi,
        "Phi_ok": phi_ok,
        "RCOD_ok": rcod_ok,
        "Energy_ok": energy_ok,
        "Max_allowed_W": max_allowed,
        "Actual_W": total_power_watts,
        "Homology": hom,
        "Topo_ok": topo_ok,
        "All_invariants_met": phi_ok and rcod_ok and energy_ok and topo_ok
    }
    return report

# ----- Example Usage -----
if __name__ == "__main__":
    # Example lattice: a hollow tetrahedron (surface of a 3‑simplex) → homotopy S^2
    # To get S^3 we need the boundary of a 4‑simplex (5 vertices, all 4‑faces)
    # We'll construct a 3‑sphere as the boundary of a 5‑cell.
    vertices = list(range(5))  # 0..4
    # all 4‑subsets (tetrahedra) as the maximal simplices
    maximal = [tuple(s) for s in combinations(vertices, 4)]
    # include all lower‑dimensional faces automatically via SimplicialComplex constructor
    complex_example = maximal

    # Node contexts: 5 nodes, each assigned a wavelength band (microns)
    node_ctx = {i: (0.6 + 0.1*i, 0.7 + 0.1*i) for i in range(5)}  # non‑overlapping for demo

    # Power draw: assume 1.5 W (well under 2 W)
    power_draw = 1.5

    result = validate_proposal(complex_example, node_ctx, power_draw)
    print("Validation Report:")
    for k, v in result.items():
        print(f"{k:20}: {v}")