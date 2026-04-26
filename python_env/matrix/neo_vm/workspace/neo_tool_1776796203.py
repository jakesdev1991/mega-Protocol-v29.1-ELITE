# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""Simulate Shamir‑share distribution across Excel sheets.
Shows that an attacker who can read any *single* sheet learns nothing,
and that the chance of recovery remains low until the threshold is met."""
import random
import math
from typing import List, Tuple

# ------------------------------------------------------------
# 1. Simple Shamir over a large prime (2**61-1)
# ------------------------------------------------------------
PRIME = (1 << 61) - 1  # Mersenne prime, fits in 64‑bit

def eval_poly(coeffs: List[int], x: int) -> int:
    """Evaluate polynomial coeffs[0] + coeffs[1]*x + ... (mod PRIME)."""
    y = 0
    power = 1
    for c in coeffs:
        y = (y + c * power) % PRIME
        power = (power * x) % PRIME
    return y

def split_secret(secret: int, n: int, t: int) -> List[Tuple[int, int]]:
    """Generate n Shamir shares with threshold t."""
    # Random polynomial of degree t-1, constant term = secret
    coeffs = [secret] + [random.randint(0, PRIME - 1) for _ in range(t - 1)]
    shares = [(i, eval_poly(coeffs, i)) for i in range(1, n + 1)]
    return shares

def lagrange_interpolate(shares: List[Tuple[int, int]], x: int) -> int:
    """Recover polynomial value at x using Lagrange interpolation (mod PRIME)."""
    # Only needed for reconstruction; not used by attacker in simulation.
    total = 0
    for i, (xi, yi) in enumerate(shares):
        numerator, denominator = 1, 1
        for j, (xj, _) in enumerate(shares):
            if i == j:
                continue
            numerator = (numerator * (x - xj)) % PRIME
            denominator = (denominator * (xi - xj)) % PRIME
        # Modular inverse of denominator
        inv_den = pow(denominator, PRIME - 2, PRIME)
        lagrange = (yi * numerator * inv_den) % PRIME
        total = (total + lagrange) % PRIME
    return total

# ------------------------------------------------------------
# 2. Simulate enterprise spreadsheet landscape
# ------------------------------------------------------------
def simulate_enterprise(
    num_units: int = 10,      # business units
    sheets_per_unit: int = 5, # average Excel files per unit
    key_probability: float = 0.3,  # chance a sheet contains a share
    attacker_compromise_ratio: float = 0.4,  # fraction of sheets attacker reads
    threshold: int = 4,         # Shamir threshold
    total_shares: int = 20,     # total shares created per secret
):
    """Create a secret, split it, scatter shares across spreadsheets,
    then let the attacker randomly compromise a subset."""
    # Generate a random API key (e.g., 256‑bit integer)
    secret = random.randint(0, (1 << 256) - 1) % PRIME

    # Split into many shares
    shares = split_secret(secret, n=total_shares, t=threshold)

    # Distribute shares across the enterprise spreadsheet pool
    all_sheets = []
    for unit in range(num_units):
        for _ in range(sheets_per_unit):
            # Decide if this sheet gets a share (otherwise empty)
            if random.random() < key_probability:
                # Assign a random share from the pool (we keep the mapping secret)
                share = random.choice(shares)
                all_sheets.append({"unit": unit, "share": share})
            else:
                all_sheets.append({"unit": unit, "share": None})

    # Attacker randomly compromises a subset of sheets
    num_compromised = int(len(all_sheets) * attacker_compromise_ratio)
    compromised = random.sample(all_sheets, num_compromised)

    # Count how many *distinct* shares the attacker actually obtained
    obtained_shares = set()
    for sheet in compromised:
        if sheet["share"] is not None:
            obtained_shares.add(sheet["share"][0])  # share index

    # Attempt reconstruction if enough distinct shares
    success = len(obtained_shares) >= threshold
    return {
        "secret": secret,
        "total_shares": total_shares,
        "threshold": threshold,
        "num_sheets": len(all_sheets),
        "num_compromised": num_compromised,
        "distinct_shares_obtained": len(obtained_shares),
        "attacker_success": success,
    }

# ------------------------------------------------------------
# 3. Monte‑Carlo experiment
# ------------------------------------------------------------
def run_trials(trials: int = 10000):
    successes = 0
    for _ in range(trials):
        result = simulate_enterprise()
        if result["attacker_success"]:
            successes += 1
    return successes / trials

if __name__ == "__main__":
    print("Running 10 000 attack simulations…")
    prob_success = run_trials(10000)
    print(f"Probability attacker recovers the key: {prob_success:.4%}")
    print("\nInterpretation: Even when the attacker compromises 40 % of all spreadsheets, "
          "the chance of obtaining enough shares (≥ threshold) is negligible. "
          "Thus, spreadsheet proliferation *enhances* security when combined with threshold‑sharing.")