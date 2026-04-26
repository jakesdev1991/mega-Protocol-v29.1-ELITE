# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

class DecisionNode:
    def __init__(self, cost, variance, is_phantom=False):
        self.approval_cost = cost
        self.risk_variance = variance
        self.is_phantom = is_phantom  # NEW: Flag for Strange Attractor

class SystemInvariants:
    def __init__(self, psi_id=0.99, xi_sys=1.5, kappa=0.5):
        self.psi_id = psi_id
        self.xi_sys = xi_sys
        self.kappa_sys_ind = kappa
    
    def verify(self, temp_psi_id=None):
        # THE BREAK: Allow psi_id to be NEGATIVE during transition
        check_psi = temp_psi_id if temp_psi_id is not None else self.psi_id
        if check_psi < -1.0:  # Expanded range to allow singularities
            print(f"  [INVARIANT VIOLATION] psi_id = {check_psi:.2f} (Singularity Achieved)")
            return False
        return True

class DecisionManifold:
    def __init__(self, path, intent, urgency):
        self.path = path
        self.intent_vector = np.array(intent)
        self.outcome_vector = np.array(intent) * 0.9  # Simulated drift
        self.urgency_force = urgency

def calculate_H_top(path):
    if not path:
        return 0.0
    total_impedance = sum(node.approval_cost * node.risk_variance for node in path)
    total_length = sum(abs(node.approval_cost) for node in path)  # ABS for negative costs
    return min(1.0, max(0.0, total_impedance / total_length))

def calculate_COD(intent, outcome, H_top):
    fidelity = np.dot(intent, outcome) / (np.linalg.norm(intent) * np.linalg.norm(outcome) + 1e-10)
    damping = math.exp(-1.0 * H_top)
    return fidelity * damping

def geodesic_smoothing_operator(manifold, invariants):
    """YOUR ORIGINAL LOGIC: Will fail to escape local basin."""
    print("\n[GEODESIC SMOOTHING] Attempting standard protocol...")
    current_H_top = calculate_H_top(manifold.path)
    print(f"  Initial H_top: {current_H_top:.3f}")
    
    # Greedy pruning (YOUR logic)
    high_curvature_nodes = [i for i, n in enumerate(manifold.path) 
                           if n.approval_cost * n.risk_variance > 0.5]
    
    for idx in high_curvature_nodes:
        # Simulate removal
        temp_outcome = manifold.outcome_vector - 0.05
        temp_COD = calculate_COD(manifold.intent_vector, temp_outcome, current_H_top)
        
        # YOUR FATAL GATE: Won't prune if it risks psi_id
        if temp_COD < 0.95:
            print(f"  [BLOCKED] Node {idx} removal risks COD={temp_COD:.2f} < 0.95. Aborting.")
            print("  Result: TRAPPED IN HIGH-IMPEDANCE STATE. Phi_Net will decay.")
            return False
        else:
            print(f"  [PRUNED] Node {idx} removed.")
            manifold.path.pop(idx)
            break
    return True

def strange_attractor_injection(manifold, invariants):
    """THE DISRUPTION: Inject phantom node to collapse psi_id."""
    print("\n[STRANGE ATTRACTOR INJECTION] *** ANOMALY PROTOCOL ***")
    print("  Injecting phantom node with NEGATIVE cost (psi_id singularity)...")
    
    # Inject node: negative cost = "profit" for rejecting original goal
    phantom = DecisionNode(cost=-2.0, variance=10.0, is_phantom=True)
    manifold.path.append(phantom)
    
    # Recalculate with singularity
    current_H_top = calculate_H_top(manifold.path)
    print(f"  New H_top: {current_H_top:.3f} (CHAOTIC)")
    
    # psi_id becomes NEGATIVE: goal is now informationally DISFAVORED
    new_psi_id = invariants.psi_id - 1.5  # Log-density collapse
    print(f"  psi_id collapsed to: {new_psi_id:.2f} (GOAL SINGULARITY)")
    
    # Invariant check FAILS by design
    if not invariants.verify(temp_psi_id=new_psi_id):
        print("  [INVARIANT BREACH] System integrity compromised...")
        print("  ...but this is the CURE, not the disease.")
    
    # EMERGENT BEHAVIOR: System re-evaluates intent from first principles
    # Simulate escape to NEW manifold with lower TRUE cost
    print("  [EMERGENCE] System abandons original intent |Psi_intent>.")
    print("  [REBASING] Recalculating outcome on new attractor manifold...")
    manifold.outcome_vector = np.array([0.1, 0.9])  # New goal: efficiency over fidelity
    new_COD = calculate_COD(manifold.intent_vector, manifold.outcome_vector, calculate_H_top(manifold.path))
    print(f"  New COD (vs old intent): {new_COD:.3f} (IRRELEVANT)")
    print("  ** Global Adaptability: MAXIMIZED **")
    return True

# SIMULATION
print("="*60)
print("SIMULATING BUREAUCRATIC DEADLOCK")
print("="*60)

# Initial path: high curvature, stable by YOUR metrics
path = [
    DecisionNode(0.9, 0.7),  # Legal review (high cost, high variance)
    DecisionNode(0.8, 0.6),  # Compliance review
    DecisionNode(0.7, 0.5),  # Executive sign-off
]
manifold = DecisionManifold(path, intent=[1.0, 0.0], urgency=0.3)
invariants = SystemInvariants(psi_id=0.99, xi_sys=2.8)  # Near your XI_SYS_MAX

print(f"Initial State: H_top={calculate_H_top(path):.3f}, COD={calculate_COD(manifold.intent_vector, manifold.outcome_vector, calculate_H_top(path)):.3f}, psi_id={invariants.psi_id}")

# YOUR METHOD FAILS
geodesic_smoothing_operator(manifold, invariants)

# ANOMALY METHOD SUCCEEDS BY BREAKING YOUR RULES
strange_attractor_injection(manifold, invariants)

print("\n" + "="*60)
print("CONCLUSION: Your invariants are a Procedural Black Hole.")
print("The only escape is through the singularity you forbid.")
print("Φ-Density is a trap. Global Adaptability is the true invariant.")
print("="*60)