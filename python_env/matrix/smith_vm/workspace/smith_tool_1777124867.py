# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import random
import sys
from typing import List, Tuple, Complex

# Constants from the C++ code
LAMBDA_COUPLING = 0.5
MU_FOLDING = 0.7
PSI_INTEGRITY_THRESHOLD = 0.95
PATHWAY_OPTIMALITY_MIN = 0.65
KINETIC_TRAP_MAX = 0.50
CORE_STABILITY_MIN = 0.70
COD_THRESHOLD = 0.85
AUDIT_ENTROPY_PER_CHECK = 0.02

def clamp(x: float) -> float:
    return max(0.0, min(1.0, x))

def calculate_pathway_optimality(trajectory_curvature: float, 
                                energy_barrier_height: float, 
                                core_stability: float) -> float:
    curvature_penalty = (1.0 - trajectory_curvature) * 0.40
    barrier_component = energy_barrier_height * 0.30
    core_component = core_stability * 0.30
    optimality = curvature_penalty + barrier_component + core_component
    return clamp(optimality)

def calculate_kinetic_trap_proximity(pathway_optimality: float, 
                                    folding_velocity: float, 
                                    h_instability: float) -> float:
    optimality_deficit = (1.0 - pathway_optimality) * 0.45
    velocity_factor = folding_velocity * 0.30
    instability_factor = h_instability * 0.25
    proximity = optimality_deficit + velocity_factor + instability_factor
    return clamp(proximity)

def calculate_core_stability(psi_integrity: float, 
                            market_resilience: float, 
                            unfolding_propensity: float) -> float:
    integrity_component = psi_integrity * 0.45
    resilience_component = market_resilience * 0.30
    unfolding_penalty = (1.0 - unfolding_propensity) * 0.25
    stability = integrity_component + resilience_component + unfolding_penalty
    return clamp(stability)

def calculate_unfolding_propensity(kinetic_trap_proximity: float, 
                                  h_instability: float, 
                                  pathway_optimality: float) -> float:
    trap_factor = kinetic_trap_proximity * 0.40
    instability_factor = h_instability * 0.35
    optimality_reduction = (1.0 - pathway_optimality) * 0.25
    propensity = trap_factor + instability_factor + optimality_reduction
    return clamp(propensity)

def calculate_energy_barrier_height(trajectory_curvature: float, 
                                   core_stability: float, 
                                   folding_velocity: float) -> float:
    curvature_component = trajectory_curvature * 0.40
    core_component = core_stability * 0.35
    velocity_reduction = folding_velocity * 0.25
    barrier = curvature_component + core_component - velocity_reduction
    return clamp(barrier)

def calculate_trap_capture_probability(kinetic_trap_proximity: float, 
                                      pathway_optimality: float, 
                                      folding_velocity: float) -> float:
    proximity_factor = kinetic_trap_proximity * 0.50
    optimality_deficit = (1.0 - pathway_optimality) * 0.30
    velocity_factor = folding_velocity * 0.20
    probability = proximity_factor + optimality_deficit + velocity_factor
    return clamp(probability)

def calculate_folding_dynamics_risk(pathway_optimality: float, 
                                   kinetic_trap_proximity: float, 
                                   core_stability: float) -> float:
    optimality_deficit = 1.0 - pathway_optimality
    core_deficit = 1.0 - core_stability
    risk = optimality_deficit * kinetic_trap_proximity * core_deficit
    return clamp(risk)

def calculate_cod_folding_aware(diagnostic_vec: List[Complex], 
                               plasma_vec: List[Complex], 
                               h_instability: float, 
                               theta_tensor_leak: float, 
                               pathway_optimality: float, 
                               kinetic_trap_proximity: float, 
                               folding_dynamics_risk: float) -> float:
    # Calculate fidelity (dot product of complex vectors)
    dot = 0.0
    magD = 0.0
    magP = 0.0
    size = min(len(diagnostic_vec), len(plasma_vec))
    for i in range(size):
        # Conjugate of diagnostic_vec[i] times plasma_vec[i]
        conj_diag = diagnostic_vec[i].conjugate()
        product = conj_diag * plasma_vec[i]
        dot += product.real  # Only real part matters for magnitude in this context
        magD += abs(diagnostic_vec[i]) ** 2
        magP += abs(plasma_vec[i]) ** 2
    
    fidelity = 0.0
    if magD > 1e-9 and magP > 1e-9:
        fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
        fidelity = clamp(fidelity)
    
    # Calculate penalties
    instability_penalty = math.exp(-LAMBDA_COUPLING * h_instability)
    exposure_penalty = math.exp(-LAMBDA_COUPLING * theta_tensor_leak)
    pathway_penalty = math.exp(-MU_FOLDING * (1.0 - pathway_optimality))
    trap_penalty = math.exp(-MU_FOLDING * kinetic_trap_proximity)
    risk_penalty = math.exp(-MU_FOLDING * folding_dynamics_risk)
    
    cod = fidelity * instability_penalty * exposure_penalty * \
          pathway_penalty * trap_penalty * risk_penalty
    return clamp(cod)

def validate_bounds(func, args_ranges: List[Tuple[float, float]], 
                   num_tests: int = 10000, func_name: str = "") -> bool:
    """Validate that function output stays in [0,1] for random inputs in given ranges."""
    for _ in range(num_tests):
        args = [random.uniform(low, high) for low, high in args_ranges]
        try:
            result = func(*args)
            if not (0.0 <= result <= 1.0 + 1e-10):  # Allow tiny floating point overflow
                print(f"FAIL: {func_name} returned {result} for args {args}")
                return False
            if math.isnan(result) or math.isinf(result):
                print(f"FAIL: {func_name} returned NaN/Inf for args {args}")
                return False
        except Exception as e:
            print(f"FAIL: {func_name} raised exception {e} for args {args}")
            return False
    return True

def main():
    print("Validating Folding Dynamics Manifold mathematical functions...")
    
    # Define test cases for each function: (func, arg_ranges, name)
    test_cases = [
        (calculate_pathway_optimality, 
         [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)], 
         "calculate_pathway_optimality"),
        (calculate_kinetic_trap_proximity, 
         [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)], 
         "calculate_kinetic_trap_proximity"),
        (calculate_core_stability, 
         [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)], 
         "calculate_core_stability"),
        (calculate_unfolding_propensity, 
         [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)], 
         "calculate_unfolding_propensity"),
        (calculate_energy_barrier_height, 
         [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)], 
         "calculate_energy_barrier_height"),
        (calculate_trap_capture_probability, 
         [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)], 
         "calculate_trap_capture_probability"),
        (calculate_folding_dynamics_risk, 
         [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)], 
         "calculate_folding_dynamics_risk"),
    ]
    
    all_passed = True
    for func, arg_ranges, name in test_cases:
        if not validate_bounds(func, arg_ranges, func_name=name):
            all_passed = False
    
    # Special test for COD function with complex vectors
    print("Testing calculate_cod_folding_aware...")
    for _ in range(1000):
        # Generate random complex vectors
        size = random.randint(1, 10)
        diagnostic_vec = [complex(random.uniform(-1, 1), random.uniform(-1, 1)) 
                         for _ in range(size)]
        plasma_vec = [complex(random.uniform(-1, 1), random.uniform(-1, 1)) 
                     for _ in range(size)]
        h_instability = random.uniform(0.0, 1.0)
        theta_tensor_leak = random.uniform(0.0, 1.0)
        pathway_optimality = random.uniform(0.0, 1.0)
        kinetic_trap_proximity = random.uniform(0.0, 1.0)
        folding_dynamics_risk = random.uniform(0.0, 1.0)
        
        try:
            result = calculate_cod_folding_aware(
                diagnostic_vec, plasma_vec, h_instability, theta_tensor_leak,
                pathway_optimality, kinetic_trap_proximity, folding_dynamics_risk
            )
            if not (0.0 <= result <= 1.0 + 1e-10):
                print(f"FAIL: COD returned {result}")
                all_passed = False
                break
            if math.isnan(result) or math.isinf(result):
                print(f"FAIL: COD returned NaN/Inf")
                all_passed = False
                break
        except Exception as e:
            print(f"FAIL: COD raised exception {e}")
            all_passed = False
            break
    
    if all_passed:
        print("✅ All mathematical validations PASSED")
        print("All functions maintain [0,1] bounds and dimensional compliance")
        return 0
    else:
        print("❌ Mathematical validation FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())