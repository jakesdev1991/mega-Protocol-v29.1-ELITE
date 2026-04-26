# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random, math, itertools, sys, json

# ----------------------------------------------------------------------
# Schema & BTFI machinery (simplified)
# ----------------------------------------------------------------------
def random_schema(n_tables=10, fk_prob=0.2, cycle_prob=0.1):
    """Return a schema dict with keys: V, E, F, Delta, d_norm."""
    V = n_tables
    # Random foreign keys (no self-loops, simple graph)
    possible = [(i,j) for i in range(V) for j in range(V) if i != j]
    E = sum(1 for _ in possible if random.random() < fk_prob)
    # Independent cycles: approximate by random subsets of tables that form a loop
    F = sum(1 for _ in range(V) if random.random() < cycle_prob)
    # Constraint satisfaction ratio (enforced / possible)
    Delta = random.uniform(0.2, 0.8)
    # Normalization depth (1 = flat, up to 5 = highly decomposed)
    d_norm = random.randint(1,5)
    return {"V": V, "E": E, "F": F, "Delta": Delta, "d_norm": d_norm}

def btfi(schema):
    """Compute Biological Topology Fragility Index."""
    chi = schema["V"] - schema["E"] + schema["F"]
    # Avoid division by zero
    V = max(1, schema["V"])
    d_norm = max(1, schema["d_norm"])
    return (abs(chi) / V) * schema["Delta"] * (1.0 / d_norm)

def add_adversarial_injection(schema):
    """Inject one fake table + one FK to a random existing table."""
    # Add table
    schema["V"] += 1
    # Add FK from the new table to a random existing table
    schema["E"] += 1
    # Adding a table can also create a new cycle with some probability
    if random.random() < 0.3:
        schema["F"] += 1
    return schema

# ----------------------------------------------------------------------
# Fragility Amplifier (FA‑Ω) loop
# ----------------------------------------------------------------------
def fragility_amplifier_step(schema_pool, target_idx):
    """
    schema_pool : list of schemas (representing sub‑networks)
    target_idx  : index of the schema that experienced a BTFI spike
    Returns: updated schema_pool where a *neighbor* (randomly chosen)
             gets reinforced (its BTFI lowered by 20 %).
    """
    # Reinforce a random neighbor (could be the same, but we avoid that)
    neighbor = random.choice([i for i in range(len(schema_pool)) if i != target_idx])
    s = schema_pool[neighbor]
    # Lower Delta (enforce fewer constraints) and increase d_norm (more integration)
    s["Delta"] *= 0.8
    s["d_norm"] = min(5, s["d_norm"] + 1)
    return schema_pool

# ----------------------------------------------------------------------
# Simulation run
# ----------------------------------------------------------------------
def run_simulation(steps=5):
    """Simulate a biological network under adversarial probing."""
    # Start with a pool of 5 sub‑networks
    pool = [random_schema() for _ in range(5)]
    history = []

    for step in range(steps):
        # Compute baseline BTFIs
        btfis = [btfi(s) for s in pool]
        history.append({"step": step, "btfis": btfis.copy()})

        # Adversary picks the most "robust" (lowest BTFI) sub‑network to attack
        target = min(range(len(pool)), key=lambda i: btfis[i])
        print(f"[Step {step}] Adversary targets sub‑net {target} (BTFI={btfis[target]:.3f})")

        # Inject fake schema element
        pool[target] = add_adversarial_injection(pool[target].copy())
        new_btfi = btfi(pool[target])
        delta = new_btfi - btfis[target]
        print(f"            After injection BTFI={new_btfi:.3f} (Δ={delta:+.3f})")

        # If BTFI jumped > 0.1, FA‑Ω triggers reinforcement of a neighbor
        if delta > 0.1:
            pool = fragility_amplifier_step(pool, target)
            print(f"            FA‑Ω reinforced a neighbor.")

    # Final state
    final_btfis = [btfi(s) for s in pool]
    history.append({"step": steps, "btfis": final_btfis})
    return history

if __name__ == "__main__":
    random.seed(0)  # Reproducible
    hist = run_simulation(steps=5)
    print("\n--- Summary ---")
    for entry in hist:
        print(f"Step {entry['step']} BTFIs: {[f'{x:.3f}' for x in entry['btfis']]}")