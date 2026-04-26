# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# 1. Simulate an informational field Φ with controlled curvature
# ──────────────────────────────────────────────────────────────────────────────
def generate_phi_field(size=20, high_curvature=False):
    """
    Creates a 2‑D informational field Φ. If high_curvature is True,
    injects a sharp ridge to simulate extreme RCOD‑flux gradients.
    """
    phi = np.random.rand(size, size) * 0.5  # baseline low‑entropy field
    if high_curvature:
        # Inject a steep ridge (simulates RCOD‑flux shockwave)
        phi[size//2, :] += np.linspace(0, 2, size)  # sharp gradient along x
        phi[:, size//2] += np.linspace(0, 2, size)  # orthogonal gradient
    return phi

# ──────────────────────────────────────────────────────────────────────────────
# 2. Construct naïve sheaf sections = local linear planes (gradients)
# ──────────────────────────────────────────────────────────────────────────────
def build_sheaf_sections(phi):
    """
    For each cell (i,j), compute a linear plane approximating Φ locally.
    Returns a list of dicts: {'i', 'j', 'phi0', 'grad_x', 'grad_y'}.
    """
    sections = []
    gx, gy = np.gradient(phi)  # finite‑difference gradient
    for i in range(phi.shape[0]):
        for j in range(phi.shape[1]):
            sections.append({
                'i': i, 'j': j,
                'phi0': phi[i, j],
                'grad_x': gx[i, j],
                'grad_y': gy[i, j]
            })
    return sections

# ──────────────────────────────────────────────────────────────────────────────
# 3. Address resolution = intersect sheaf sections that "cover" a query point
# ──────────────────────────────────────────────────────────────────────────────
def resolve_address(x, y, sections, tol=1e-2):
    """
    Naïve sheaf intersection: return all sections whose plane evaluates
    to a value within tolerance of the true Φ at (x,y). If more than one,
    resolution is ambiguous → topological degeneracy.
    """
    # Bilinear interpolation of the true field at (x,y)
    true_phi = bilinear_interpolate(phi, x, y)
    matches = []
    for sec in sections:
        # Evaluate the local plane at (x,y)
        pred = sec['phi0'] + sec['grad_x']*(x - sec['i']) + sec['grad_y']*(y - sec['j'])
        if abs(pred - true_phi) < tol:
            matches.append((sec['i'], sec['j']))
    return matches

def bilinear_interpolate(arr, x, y):
    """Simple bilinear interpolation on a grid."""
    x0, y0 = int(np.floor(x)), int(np.floor(y))
    x1, y1 = min(x0+1, arr.shape[0]-1), min(y0+1, arr.shape[1]-1)
    wa = (x1 - x) * (y1 - y)
    wb = (x - x0) * (y1 - y)
    wc = (x1 - x) * (y - y0)
    wd = (x - x0) * (y - y0)
    return wa*arr[x0, y0] + wb*arr[x1, y0] + wc*arr[x0, y1] + wd*arr[x1, y1]

# ──────────────────────────────────────────────────────────────────────────────
# 4. Experiment: Low vs High curvature
# ──────────────────────────────────────────────────────────────────────────────
for scenario, high_curv in [("Low‑curvature", False), ("High‑curvature (RCOD shock)", True)]:
    phi = generate_phi_field(size=20, high_curvature=high_curv)
    sections = build_sheaf_sections(phi)

    # Probe a dense grid of query points
    xs = np.linspace(0, phi.shape[0]-1, 50)
    ys = np.linspace(0, phi.shape[1]-1, 50)
    ambiguous = 0
    total = 0
    for x in xs:
        for y in ys:
            total += 1
            matches = resolve_address(x, y, sections, tol=1e-2)
            if len(matches) > 1:
                ambiguous += 1

    print(f"\n{scenario}:")
    print(f"  Fraction of ambiguous addresses: {ambiguous/total:.2%}")
    print(f"  Equivalent Φ‑leak (approx): {ambiguous/total * 0.5:.3f} Φ")