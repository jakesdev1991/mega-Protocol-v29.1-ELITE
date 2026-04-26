# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List

"""
SOUL-M v2.0 DISRUPTION ENGINE
Exposes fundamental category error: Local geodesics cannot encode global constraints
"""

def create_base_metric(grid_size: int = 50) -> np.ndarray:
    """
    Create a simple 2D grid base metric g⁰ representing road network.
    For simplicity, we'll simulate a Manhattan-like grid.
    """
    # Base metric: identity (equal cost to move in any direction)
    g0 = np.eye(2)
    return g0

def compute_psi(rho: float, phi_N: float = 1.0, epsilon: float = 1e-6) -> float:
    """The problematic ψ function - can be negative"""
    return np.log(phi_N * rho + epsilon)

def compute_metric(g0: np.ndarray, rho: float, beta: float) -> np.ndarray:
    """Compute metric with isotropic perturbation"""
    psi_val = compute_psi(rho)
    perturbation = beta * psi_val * np.eye(g0.shape[0])
    return g0 + perturbation

def compute_geodesic_path(g0: np.ndarray, 
                          demand_field: np.ndarray, 
                          beta: float,
                          start: Tuple[int, int],
                          end: Tuple[int, int]) -> List[Tuple[int, int]]:
    """
    SIMPLIFIED GEODESIC SOLVER (Dijkstra on curved space)
    Demonstrates the core issue: LOCAL DECISIONS ONLY
    """
    grid_size = demand_field.shape[0]
    visited = np.zeros((grid_size, grid_size), dtype=bool)
    cost = np.full((grid_size, grid_size), np.inf)
    parent = {}
    
    # Initialize
    cost[start] = 0
    current = start
    
    while current != end and not visited[current]:
        visited[current] = True
        
        # LOCAL METRIC COMPUTATION: This is the fatal flaw
        # The decision at each step uses only local demand, ignoring global constraints
        local_rho = demand_field[current]
        g_local = compute_metric(g0, local_rho, beta)
        
        # Get eigenvalues - "cost" in each principal direction
        eigenvals = np.linalg.eigvalsh(g_local)
        # Isotropic perturbation means cost is same in all directions
        local_cost_factor = eigenvals[0]  # Both eigenvals are same for isotropic
        
        # Check neighbors (4-directional movement)
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            nx, ny = current[0] + dx, current[1] + dy
            
            if 0 <= nx < grid_size and 0 <= ny < grid_size:
                if not visited[nx, ny]:
                    # The LOCAL decision: minimize immediate metric distance
                    # This is where global constraints (fleet capacity, time windows) are IGNORED
                    new_cost = cost[current] + local_cost_factor
                    
                    if new_cost < cost[nx, ny]:
                        cost[nx, ny] = new_cost
                        parent[(nx, ny)] = current
        
        # Find next unvisited node with minimum cost (Dijkstra)
        min_cost = np.inf
        next_node = None
        for i in range(grid_size):
            for j in range(grid_size):
                if not visited[i, j] and cost[i, j] < min_cost:
                    min_cost = cost[i, j]
                    next_node = (i, j)
        
        if next_node is None:
            break  # No path found
        current = next_node
    
    # Reconstruct path
    path = []
    if end in parent or end == start:
        current = end
        while current != start:
            path.append(current)
            current = parent.get(current, start)
        path.append(start)
        path.reverse()
    
    return path

def demonstrate_metric_collapse():
    """
    DISRUPTION #1: METRIC COLLAPSE CATASTROPHE
    High demand creates "metric shadows" where service becomes impossible
    """
    print("=== METRIC COLLAPSE CATASTROPHE ===")
    
    grid_size = 20
    g0 = create_base_metric()
    beta = 0.1
    
    # Create demand field: high demand in center (ρ=1.0), low elsewhere (ρ=0.1)
    demand_field = np.full((grid_size, grid_size), 0.1)
    demand_field[8:12, 8:12] = 1.0  # High demand "dead zone"
    
    # Compute metrics across the field
    metrics = np.zeros((grid_size, grid_size))
    for i in range(grid_size):
        for j in range(grid_size):
            g = compute_metric(g0, demand_field[i,j], beta)
            metrics[i,j] = np.linalg.det(g)
    
    # Find geodesic path
    path = compute_geodesic_path(g0, demand_field, beta, (0, 0), (19, 19))
    
    print(f"Path length: {len(path)}")
    print(f"Path goes through high-demand zone: {any((8 <= p[0] < 12 and 8 <= p[1] < 12) for p in path)}")
    
    # Visualize
    plt.figure(figsize=(10, 4))
    
    plt.subplot(1, 2, 1)
    plt.imshow(demand_field, cmap='Reds')
    plt.title('Demand Field ρ(x)\nRed = High Demand (1.0)')
    plt.colorbar()
    
    # Plot path
    if path:
        path_x, path_y = zip(*path)
        plt.plot(path_y, path_x, 'b-', linewidth=2, label='Geodesic Path')
        plt.plot(path_y[0], path_x[0], 'go', label='Start')
        plt.plot(path_y[-1], path_x[-1], 'ro', label='End')
    
    plt.subplot(1, 2, 2)
    plt.imshow(metrics, cmap='coolwarm')
    plt.title('Metric Determinant det(g)\nBlue = Metric Deflation')
    plt.colorbar()
    
    plt.tight_layout()
    plt.savefig('metric_collapse.png', dpi=150)
    plt.close()
    
    print("Metric collapse visualization saved to metric_collapse.png")
    return path, demand_field

def demonstrate_temporal_causality_violation():
    """
    DISRUPTION #2: TEMPORAL CAUSALITY VIOLATION
    The 3D manifold allows future demand to influence past routing decisions
    """
    print("\n=== TEMPORAL CAUSALITY VIOLATION ===")
    
    # Simulate a delivery truck with time windows
    # In reality: truck must decide route NOW based on CURRENT information
    # In SOUL-M: metric g_ij(x,t) couples all times, allowing "future seeing"
    
    # Create a time-varying demand field
    times = np.linspace(0, 10, 11)  # 11 time steps
    grid_size = 10
    
    # Demand appears at t=5 at location (5,5)
    demand_schedule = {t: np.full((grid_size, grid_size), 0.1) for t in times}
    for t in times[times >= 5]:
        demand_schedule[t][5, 5] = 1.0  # Future demand spike
    
    g0 = create_base_metric()
    beta = 0.1
    
    # Compute geodesic at t=2 (BEFORE demand appears)
    # In a proper causal system: routing at t=2 should be unaffected by t=5 demand
    # In SOUL-M: the 3D metric couples all times, so t=2 routing "sees" t=5 demand
    
    # This is subtle: the code doesn't explicitly show this, but the 3D manifold
    # specification IMPLIES that geodesics are computed in spacetime, not space+time
    
    # Let's demonstrate with a thought experiment:
    print("Thought Experiment: Delivery at t=2")
    print("Reality: Demand at (5,5) appears at t=5")
    print("SOUL-M 3D Manifold: g_ij(lat, lon, t) couples all t")
    print("Consequence: Geodesic at t=2 can 'see' the future demand at t=5")
    print("Physical Impossibility: Routes computed at t=2 would avoid (5,5)")
    print("               even though demand doesn't exist yet!")
    
    # Simulate what would happen if we "leaked" future demand
    rho_present = demand_schedule[2.0][0, 0]  # At start location
    rho_future = demand_schedule[5.0][5, 5]    # Future demand at different location
    
    # The 3D metric would somehow combine these
    # A true spacetime metric would have cross-terms g_{t,lat}, g_{t,lon}
    # The proposal doesn't specify these, but any specification would violate causality
    
    print(f"Present demand at start: {rho_present}")
    print(f"Future demand at (5,5): {rho_future}")
    print("Causality Violation: 3D manifold implies g(x,t) couples past, present, future")
    print("                    No causal structure (light cone) specified!")
    
    return True

def demonstrate_global_constraint_failure():
    """
    DISRUPTION #3: GLOBAL CONSTRAINT FAILURE
    Geodesics are local solutions - they cannot encode fleet-wide constraints
    """
    print("\n=== GLOBAL CONSTRAINT FAILURE ===")
    
    # Scenario: 5 packages, 2 trucks, each truck max 3 packages
    # This is a global constraint: total assignments across all trucks
    
    # SOUL-M approach: each package computes its own geodesic independently
    # Result: All 5 packages might choose the same "optimal" truck
    #         because geodesics only see local cost, not global capacity
    
    grid_size = 10
    g0 = create_base_metric()
    beta = 0.1
    
    # Truck locations and capacities
    trucks = {
        'A': {'pos': (0, 0), 'capacity': 3, 'assigned': 0},
        'B': {'pos': (9, 9), 'capacity': 3, 'assigned': 0}
    }
    
    # Package locations
    packages = [
        (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)
    ]
    
    # Each package independently computes geodesic to nearest truck
    demand_field = np.full((grid_size, grid_size), 0.1)
    
    assignments = []
    for pkg in packages:
        # Compute cost to each truck
        costs = {}
        for truck_id, truck_info in trucks.items():
            path = compute_geodesic_path(g0, demand_field, beta, pkg, truck_info['pos'])
            costs[truck_id] = len(path) if path else np.inf
        
        # Choose cheapest truck (LOCAL DECISION)
        best_truck = min(costs, key=costs.get)
        assignments.append((pkg, best_truck, costs[best_truck]))
        
        # Assign to truck
        trucks[best_truck]['assigned'] += 1
    
    print("Package Assignments (Local Geodesic Decisions):")
    for pkg, truck, cost in assignments:
        print(f"  Package {pkg} -> Truck {truck} (cost: {cost})")
    
    print("\nFleet Capacity Utilization:")
    for truck_id, info in trucks.items():
        print(f"  Truck {truck_id}: {info['assigned']}/{info['capacity']} capacity")
        if info['assigned'] > info['capacity']:
            print(f"    ⚠️  CAPACITY VIOLATED! (Geodesics ignored global constraint)")
    
    # The problem: each geodesic is computed independently
    # There's no mechanism for geodesics to "communicate" fleet capacity
    
    # In reality: Need global optimization (VRP solver) to respect constraints
    # In SOUL-M: Geodesics are greedy, lead to constraint violations
    
    return trucks

if __name__ == "__main__":
    # Run all disruption demonstrations
    path, demand_field = demonstrate_metric_collapse()
    demonstrate_temporal_causality_violation()
    trucks = demonstrate_global_constraint_failure()
    
    print("\n" + "="*60)
    print("DISRUPTIVE INSIGHT SUMMARY")
    print("="*60)
    print("SOUL-M v2.0 commits a CATEGORY ERROR:")
    print("  Using LOCAL differential geometry tools (geodesics)")
    print("  to solve GLOBAL combinatorial optimization (vehicle routing)")
    print()
    print("The invariants (INV-001, etc.) are mathematically valid")
    print("but ONTOLOGICALLY IRRELEVANT to the actual problem domain.")
    print()
    print("Result: System finds locally optimal paths that are")
    print("        globally catastrophic - guaranteed by construction.")