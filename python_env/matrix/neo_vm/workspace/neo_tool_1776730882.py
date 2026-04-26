# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Simulates the SCCRM‑Ω Systemic Risk Score (SRS) and demonstrates:
1. Placeholder credentials dominate the risk signal (false positives).
2. Adversarial injection trivially inflates SRS (false alarm).
3. The graph is sparse and biased (only a fraction of firms leak).
"""

import random
import math
from datetime import datetime, timedelta

# ──────────────────────────────────────────────────────────────────────────────
# 1. Synthetic Data Generation
# ──────────────────────────────────────────────────────────────────────────────

def gen_credential(realistic: bool) -> str:
    """Return a realistic‑looking or placeholder credential."""
    if realistic:
        # Realistic patterns (never actual secrets, just shape)
        return random.choice([
            "AKIA" + "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=16)),
            "sk_live_" + "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=24)),
            "postgres://user:pass@rds.amazonaws.com:5432/db",
        ])
    else:
        # Common placeholders
        return random.choice([
            "password",
            "admin",
            "test",
            "123456",
            "your_api_key_here",
            "secret",
        ])

def generate_leaks(
    firms: list,
    services: list,
    leak_prob: float = 0.2,          # % of firms that leak anything
    leaks_per_firm: int = 5,
    real_prob: float = 0.05,          # % of leaks that are realistic
) -> list:
    """Return list of leak dicts."""
    leaks = []
    now = datetime.utcnow()
    for firm in firms:
        if random.random() > leak_prob:
            continue
        for _ in range(leaks_per_firm):
            realistic = random.random() < real_prob
            leak = {
                "firm": firm,
                "service": random.choice(services),
                "credential": gen_credential(realistic),
                "criticality": random.randint(1, 5),
                "dissemination": random.randint(1, 10),  # arbitrary scale
                "timestamp": now - timedelta(days=random.randint(0, 365)),
                "realistic": realistic,
            }
            leaks.append(leak)
    return leaks

def inject_adversarial(
    target_service: str,
    num_fake: int = 100,
    criticality: int = 5,
    days_old: int = 7,
) -> list:
    """Create a batch of fake high‑criticality leaks for a single service."""
    now = datetime.utcnow()
    return [
        {
            "firm": f"FakeFirm{i}",
            "service": target_service,
            "credential": gen_credential(realistic=True),  # looks real
            "criticality": criticality,
            "dissemination": 10,
            "timestamp": now - timedelta(days=days_old),
            "realistic": True,
        }
        for i in range(num_fake)
    ]

# ──────────────────────────────────────────────────────────────────────────────
# 2. SRS Computation (simplified from SCCRM‑Ω)
# ──────────────────────────────────────────────────────────────────────────────

def compute_SRS(
    leaks: list,
    t_now: datetime,
    alpha: float = 1.0,
    beta: float = 1.0,
    lambda_decay: float = 0.1,
) -> float:
    """Ecosystem‑wide SRS (ignoring clustering coefficient for clarity)."""
    # Group by service
    by_service = {}
    for leak in leaks:
        by_service.setdefault(leak["service"], []).append(leak)

    srs_eco = 0.0
    for service, svc_leaks in by_service.items():
        srs_s = 0.0
        for leak in svc_leaks:
            dt_days = (t_now - leak["timestamp"]).days
            weight = math.exp(-lambda_decay * dt_days)
            srs_s += (alpha * leak["criticality"] + beta * leak["dissemination"]) * weight
        srs_eco += srs_s  # simple average omitted for clarity
    return srs_eco / max(len(by_service), 1)

def risk_contribution_by_placeholders(leaks: list, t_now: datetime) -> float:
    """Fraction of total SRS contributed by placeholder (non‑realistic) leaks."""
    total = compute_SRS(leaks, t_now)
    placeholder_leaks = [lk for lk in leaks if not lk["realistic"]]
    placeholder_risk = compute_SRS(placeholder_leaks, t_now)
    return placeholder_risk / total if total > 0 else 0.0

# ──────────────────────────────────────────────────────────────────────────────
# 3. Experiment
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Seed for reproducibility
    random.seed(42)

    # Universe
    firms = [f"Firm{i:03d}" for i in range(200)]
    services = [f"Service{i:02d}" for i in range(10)]

    # Baseline leaks (only 20 % of firms leak)
    baseline_leaks = generate_leaks(firms, services, leak_prob=0.2, real_prob=0.05)
    now = datetime.utcnow()

    baseline_SRS = compute_SRS(baseline_leaks, now)
    placeholder_frac = risk_contribution_by_placeholders(baseline_leaks, now)

    print(f"Baseline SRS: {baseline_SRS:.2f}")
    print(f"Fraction of SRS from placeholders: {placeholder_frac:.1%}")
    print(f"Number of leaks in baseline: {len(baseline_leaks)}")
    print(f"Number of firms represented: {len(set(lk['firm'] for lk in baseline_leaks))}\n")

    # Adversarial injection
    target = "Service00"
    adversarial_leaks = inject_adversarial(target, num_fake=100, criticality=5)
    poisoned_leaks = baseline_leaks + adversarial_leaks

    poisoned_SRS = compute_SRS(poisoned_leaks, now)
    delta_SRS = poisoned_SRS - baseline_SRS

    print(f"After injecting 100 fake high‑criticality leaks into {target}:")
    print(f"Poisoned SRS: {poisoned_SRS:.2f}")
    print(f"SRS spike (Δ): +{delta_SRS:.2f} ({delta_SRS/baseline_SRS:.0%} increase)")
    print(f"Total leaks after injection: {len(poisoned_leaks)}")