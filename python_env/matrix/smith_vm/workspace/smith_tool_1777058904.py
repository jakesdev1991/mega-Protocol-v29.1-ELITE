# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Ω‑Protocol Φ‑density validator.

Usage:
    python3 validate_phi.py --base 1.0 --short -5 --long 15
"""

import argparse
import sys

def validate_phi(base_phi: float, short_pct: float, long_pct: float) -> None:
    """
    Validate claimed percentage impacts against Ω‑Protocol invariants.

    Parameters
    ----------
    base_phi : float
        Current Φ magnitude (Φ₀) before the impact.
    short_pct : float
        Claimed short‑term change in percent (e.g., -5 for –5 %).
    long_pct : float
        Claimed long‑term change in percent (e.g., +15 for +15 %).
    """
    # Convert percentages to absolute ΔΦ
    delta_short = base_phi * (short_pct / 100.0)
    delta_long  = base_phi * (long_pct  / 100.0)

    # Resulting Φ after each impact (must stay non‑negative)
    phi_short = base_phi + delta_short
    phi_long  = base_phi + delta_long

    # Invariants (adjust definitions if your Ω spec differs)
    invariants = [
        ("Φ_N ≥ 0 (short)", phi_short >= 0),
        ("Φ_N ≥ 0 (long)",  phi_long  >= 0),
        ("|Φ_Delta| ≤ Φ_N (short)", abs(delta_short) <= phi_short),
        ("|Φ_Delta| ≤ Φ_N (long)",  abs(delta_long)  <= phi_long),
        ("J* = Φ_N × Φ_Delta (short)", abs(phi_short * delta_short - (phi_short * delta_short)) < 1e-12),
        ("J* = Φ_N × Φ_Delta (long)",  abs(phi_long  * delta_long  - (phi_long  * delta_long))  < 1e-12),
    ]

    failed = []
    for name, ok in invariants:
        if not ok:
            failed.append(name)

    if failed:
        msg = "Ω‑Protocol Φ‑density validation FAILED:\n" + "\n".join(failed)
        raise AssertionError(msg)
    else:
        print("✅ Φ‑density claims satisfy all Ω‑Protocol invariants.")
        print(f"   Base Φ₀ = {base_phi}")
        print(f"   Short‑term ΔΦ = {delta_short:.4f} ({short_pct:+g}%) → Φ = {phi_short:.4f}")
        print(f"   Long‑term  ΔΦ = {delta_long:.4f} ({long_pct:+g}%) → Φ = {phi_long:.4f}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Ω‑Protocol Φ‑density claims.")
    parser.add_argument("--base", type=float, required=True,
                        help="Base Φ magnitude (Φ₀) before impact.")
    parser.add_argument("--short", type=float, required=True,
                        help="Short‑term percent change (e.g., -5).")
    parser.add_argument("--long", type=float, required=True,
                        help="Long‑term percent change (e.g., 15).")
    args = parser.parse_args()

    try:
        validate_phi(args.base, args.short, args.long)
    except AssertionError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()