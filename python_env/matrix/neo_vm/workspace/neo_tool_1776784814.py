# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import itertools
import pulp
import numpy as np

# ---------- Instance generation ----------
def generate_instance(n_orders=6, n_venues=2, seed=0):
    random.seed(seed)
    orders = []
    for i in range(n_orders):
        orders.append({
            'id': i,
            'value': random.uniform(1, 10),
            'deadline': random.randint(1, 5),   # discrete time steps
            'size': random.uniform(0.5, 2.0),   # resource units
            'venue_mask': [random.random() > 0.3 for _ in range(n_venues)]
        })
    venues = [{'capacity': random.uniform(5, 8)} for _ in range(n_venues)]
    return orders, venues

# ---------- True optimum (brute force for tiny instances) ----------
def true_optimum(orders, venues):
    best_val = 0
    best_set = []
    for r in range(len(orders)+1):
        for subset in itertools.combinations(orders, r):
            # check deadline and capacity feasibility
            time_cap = [v['capacity'] for v in venues]
            feasible = True
            total_val = 0
            for o in subset:
                # assign to first compatible venue with remaining capacity
                assigned = False
                for j, vm in enumerate(o['venue_mask']):
                    if vm and time_cap[j] >= o['size']:
                        time_cap[j] -= o['size']
                        assigned = True
                        break
                if not assigned:
                    feasible = False
                    break
                total_val += o['value']
            if feasible and total_val > best_val:
                best_val = total_val
                best_set = subset
    return best_val, best_set

# ---------- LP relaxation (upper bound) ----------
def lp_relaxation(orders, venues):
    prob = pulp.LpProblem('OrderMatching', pulp.LpMaximize)
    # variables: fractional assignment x_{i,j}
    x = pulp.LpVariable.dicts('x', ((i, j) for i in range(len(orders)) for j in range(len(venues))),
                                lowBound=0, upBound=1, cat='Continuous')
    # objective
    prob += pulp.lpSum(orders[i]['value'] * pulp.lpSum(x[(i,j)] for j in range(len(venues))) for i in range(len(orders))
    # capacity constraints
    for j, v in enumerate(venues):
        prob += pulp.lpSum(orders[i]['size'] * x[(i,j)] for i in range(len(orders))) <= v['capacity']
    # each order can be assigned at most once (fractionally)
    for i in range(len(orders)):
        prob += pulp.lpSum(x[(i,j)] for j in range(len(venues))) <= 1
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    lp_val = pulp.value(prob.objective)
    # extract duals for capacity constraints
    duals = [prob.constraints[f'C_{j}'].pi for j in range(len(venues))]
    return lp_val, duals

# ---------- Greedy SARound proxy (value density) ----------
def greedy_saround(orders, venues):
    # sort by value per size (density)
    sorted_orders = sorted(orders, key=lambda o: o['value']/o['size'], reverse=True)
    cap = [v['capacity'] for v in venues]
    total_val = 0
    for o in sorted_orders:
        # try to place in first compatible venue with capacity
        for j, vm in enumerate(o['venue_mask']):
            if vm and cap[j] >= o['size']:
                cap[j] -= o['size']
                total_val += o['value']
                break
    return total_val

# ---------- MEAI ----------
def compute_meai(opt_val, saround_val):
    # avoid division by zero
    if opt_val == 0:
        return 1.0
    return saround_val / opt_val

# ---------- Adversarial gaming: inject easy orders ----------
def game_instance(orders, venues):
    # add dummy orders that are tiny, high value, and compatible with all venues
    for i in range(3):
        orders.append({
            'id': f'dummy_{i}',
            'value': 10.0,          # high value
            'deadline': 10,
            'size': 0.1,            # tiny resource footprint
            'venue_mask': [True]*len(venues)
        })
    return orders, venues

# ---------- Simulation ----------
if __name__ == '__main__':
    # Normal scenario
    orders, venues = generate_instance(seed=42)
    opt_val, _ = true_optimum(orders, venues)
    lp_val, duals = lp_relaxation(orders, venues)
    saround_val = greedy_saround(orders, venues)
    meai_normal = compute_meai(opt_val, saround_val)

    print(f'--- Normal Scenario ---')
    print(f'True optimum: {opt_val:.2f}')
    print(f'LP upper bound: {lp_val:.2f}')
    print(f'Greedy SARound: {saround_val:.2f}')
    print(f'MEAI: {meai_normal:.3f}')
    print(f'Dual prices (capacity shadow costs): {duals}')

    # Gaming scenario: inject dummy orders
    orders_gamed, venues_gamed = generate_instance(seed=42)
    orders_gamed, venues_gamed = game_instance(orders_gamed, venues_gamed)
    opt_val_gamed, _ = true_optimum(orders_gamed, venues_gamed)
    lp_val_gamed, duals_gamed = lp_relaxation(orders_gamed, venues_gamed)
    saround_val_gamed = greedy_saround(orders_gamed, venues_gamed)
    meai_gamed = compute_meai(opt_val_gamed, saround_val_gamed)

    print(f'\n--- Gaming Scenario (injected easy orders) ---')
    print(f'True optimum: {opt_val_gamed:.2f}')
    print(f'LP upper bound: {lp_val_gamed:.2f}')
    print(f'Greedy SARound: {saround_val_gamed:.2f}')
    print(f'MEAI: {meai_gamed:.3f}')
    print(f'Dual prices: {duals_gamed}')

    # Show that duals remain low (no real stress) while MEAI is inflated
    print(f'\n--- Insight ---')
    print(f'MEAI increased by {meai_gamed/meai_normal:.1f}x due to gaming.')
    print(f'Dual prices changed by factor {np.mean(duals_gamed)/np.mean(duals):.1f}x (should be ~1 if robust).')

    # Simulate naive MPC-Ω that triggers on MEAI < 0.3
    threshold = 0.3
    # In gaming scenario, MEAI is high, so no intervention; but if we artificially drop MEAI by removing good orders:
    orders_stressed, venues_stressed = generate_instance(seed=42)
    # remove the highest-value orders to simulate stress
    orders_stressed = sorted(orders_stressed, key=lambda o: o['value'])[:3]
    opt_val_stressed, _ = true_optimum(orders_stressed, venues_stressed)
    lp_val_stressed, duals_stressed = lp_relaxation(orders_stressed, venues_stressed)
    saround_val_stressed = greedy_saround(orders_stressed, venues_stressed)
    meai_stressed = compute_meai(opt_val_stressed, saround_val_stressed)
    print(f'\n--- Stressed Scenario (few high-value orders) ---')
    print(f'MEAI: {meai_stressed:.3f}')
    print(f'Dual prices: {duals_stressed}')
    if meai_stressed < threshold:
        print('MPC-Ω triggers: circuit breaker!')
    else:
        print('MPC-Ω stays idle (MEAI above threshold).')
    # Note: duals_stressed will spike, showing real stress, while MEAI may still be above threshold, demonstrating MEAI lag.