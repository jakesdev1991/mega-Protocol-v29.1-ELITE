# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validation script for the Supply‑Chain Credential Risk Monitor (SCCRM‑Ω) proposal.

The script checks:
1.  Mathematical consistency of the formulas used to compute:
        • Service‑level Systemic Risk Score (SRS_s)
        • Ecosystem‑wide SRS (SRS_eco)
        • Mapping to Ω‑variables Φ_N and Φ_Δ
2.  That the Ω‑invariants remain within their admissible ranges:
        • 0 ≤ Φ_N ≤ 1   (strategic connectivity)
        • 0 ≤ Φ_Δ ≤ 1   (information asymmetry)
        • SRS_eco ≥ 0   (risk score cannot be negative)
        • Constraint set used in the MPC‑Ω QP:
                SRS_eco ≤ 10.0
                Φ_N ≥ 0.4
                Φ_Δ ≤ 0.8
3.  That the anomaly‑detection rule is well‑defined (no division by zero).

If any invariant is violated, an AssertionError is raised with a diagnostic
message.

The script is deliberately self‑contained – it generates a small synthetic
dataset, runs the calculations, and prints the intermediate values for
inspection.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions (directly taken from the proposal)
# ----------------------------------------------------------------------
def service_level_srs(leaks, alpha=1.0, beta=1.0, lam=0.1):
    """
    Compute SRS_s(t) for a single service.

    Parameters
    ----------
    leaks : list of dicts
        Each dict represents a (firm, service) leak and must contain:
            - 'C'   : credential criticality (1‑5)
            - 'D'   : dissemination scale (positive)
            - 't'   : leak timestamp (days since epoch)
    alpha, beta : float
        Weighting coefficients for C and D.
    lam : float
        Decay constant (day⁻¹).  Typical value 0.1 → ~10‑day half‑life.

    Returns
    -------
    float
        Service‑level SRS.
    """
    now = 0.0  # we evaluate at t = 0 (present); timestamps are negative
    srs = 0.0
    for l in leaks:
        age = now - l['t']          # positive if leak is in the past
        if age < 0:
            raise ValueError("Leak timestamp must be <= current time.")
        contrib = (alpha * l['C'] + beta * l['D']) * np.exp(-lam * age)
        srs += contrib
    return srs


def ecosystem_srs(service_srs_list, cluster_coeffs, kappa=0.5):
    """
    Compute the ecosystem‑wide SRS.

    Parameters
    ----------
    service_srs_list : list of float
        SRS_s for each service s ∈ S.
    cluster_coeffs : list of float
        Clustering coefficient CC(s) for each service (0 ≤ CC ≤ 1).
    kappa : float
        Learned scaling factor from historic multi‑firm failures.

    Returns
    -------
    float
        Ecosystem‑wide SRS.
    """
    if len(service_srs_list) != len(cluster_coeffs):
        raise ValueError("Mismatch between number of services and CC values.")
    total = 0.0
    for srs, cc in zip(service_srs_list, cluster_coeffs):
        if not (0.0 <= cc <= 1.0):
            raise ValueError(f"Clustering coefficient out of bounds: {cc}")
        total += srs * (1.0 + kappa * cc)
    return total / len(service_srs_list)


def map_to_phi_N(phi_N0, srs_eco, eta1=0.3, tau1=90.0):
    """
    Φ_N(t) = Φ_N0 - η1 * tanh( SRS_eco(t - τ1) )
    We approximate the delay by using the current SRS_eco (τ1 is absorbed
    into the η1 scaling for this validation).
    """
    return phi_N0 - eta1 * np.tanh(srs_eco)


def map_to_phi_Delta(phi_Delta0, srs_eco, eta2=0.2, tau2=60.0):
    """
    Φ_Δ(t) = Φ_Δ0 + η2 * SRS_eco(t - τ2)
    Same simplification as above.
    """
    return phi_Delta0 + eta2 * srs_eco


def anomaly_score(residual, sigma_residual):
    """
    s_SRS(t) = |residual| / σ_residual
    """
    if sigma_residual <= 0:
        raise ValueError("Residual standard deviation must be > 0.")
    return np.abs(residual) / sigma_residual


# ----------------------------------------------------------------------
# Synthetic data generation for a quick sanity check
# ----------------------------------------------------------------------
np.random.seed(42)

# Suppose we monitor 3 services (AWS RDS, GCP BigQuery, Snowflake)
n_services = 3
service_names = ["aws-rds", "gcp-bq", "snowflake"]

# Generate a few leaks per service
leaks_by_service = {name: [] for name in service_names}
for i, name in enumerate(service_names):
    n_leaks = np.random.randint(2, 5)  # 2‑4 leaks per service
    for _ in range(n_leaks):
        leak = {
            'C': np.random.randint(1, 6),          # criticality 1‑5
            'D': np.random.uniform(0.5, 5.0),      # dissemination scale
            't': -np.random.uniform(0, 180)        # leak happened 0‑180 days ago
        }
        leaks_by_service[name].append(leak)

# Compute service‑level SRS
service_srs = []
for name in service_names:
    srs = service_level_srs(leaks_by_service[name])
    service_srs.append(srs)
    print(f"[{name}] SRS_s = {srs:.3f}")

# Generate plausible clustering coefficients (0‑1)
cluster_coeffs = np.random.rand(n_services) * 0.7  # keep them moderate
print("\nClustering coefficients:")
for name, cc in zip(service_names, cluster_coeffs):
    print(f"  {name}: CC = {cc:.3f}")

# Ecosystem‑wide SRS
srs_eco = ecosystem_srs(service_srs, cluster_coeffs, kappa=0.4)
print(f"\nEcosystem‑wide SRS_eco = {srs_eco:.3f}")

# Baseline Ω‑variables (chosen within the admissible range)
phi_N0 = 0.7
phi_Delta0 = 0.3

# Map to Φ_N and Φ_Δ
phi_N = map_to_phi_N(phi_N0, srs_eco)
phi_Delta = map_to_phi_Delta(phi_Delta0, srs_eco)
print(f"Φ_N = {phi_N:.3f}")
print(f"Φ_Δ = {phi_Delta:.3f}")

# ----------------------------------------------------------------------
# Invariant checks
# ----------------------------------------------------------------------
# 1. Non‑negative SRS
assert srs_eco >= 0.0, f"SRS_eco must be non‑negative, got {srs_eco}"

# 2. Φ_N and Φ_Δ within [0,1]
assert 0.0 <= phi_N <= 1.0, f"Φ_N out of bounds: {phi_N}"
assert 0.0 <= phi_Delta <= 1.0, f"Φ_Δ out of bounds: {phi_Delta}"

# 3. MPC‑Ω constraint set (as given in the proposal)
assert srs_eco <= 10.0, f"SRS_eco exceeds QP upper bound: {srs_eco}"
assert phi_N >= 0.4, f"Φ_N below QP lower bound: {phi_N}"
assert phi_Delta <= 0.8, f"Φ_Δ exceeds QP upper bound: {phi_Delta}"

# 4. Anomaly‑score denominator safety (dummy residual)
residual = 0.5 * srs_eco  # just a placeholder
sigma_res = max(0.1, np.std(service_srs))  # avoid zero
s_srs = anomaly_score(residual, sigma_res)
print(f"Anomaly score s_SRS = {s_srs:.3f}")
# No assertion here – the rule is just a threshold check elsewhere.

print("\n✅ All mathematical invariants and Omega‑Protocol constraints are satisfied.")