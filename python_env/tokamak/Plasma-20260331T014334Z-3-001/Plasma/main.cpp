#include "Omega_System_Executive.hpp"
#include <iostream>

int main() {
    // 1. Instantiate Executive
    OmegaSystem tokamak_safety;
    
    // 2. Mock Data Loop (Safe Initialization)
    std::array<double, 8> raw_inputs; raw_inputs.fill(50.0);
    ReactorVitals vitals = {1.5, 0.5, true}; // Simulated Steady State Vitals
    
    // 3. Execute Control Cycle
    auto result = tokamak_safety.run_cycle(raw_inputs, vitals, true);
    
    // 4. Output Logic
    if (result.global_trip_actuated) {
        std::cout << "[CRITICAL] TRIP ACTUATED. MASK: " << result.trip_bitmask << std::endl;
    } else {
        std::cout << "[NOMINAL] SYSTEM SAFE - ACTIVE PHASE: " << (int)tokamak_safety.get_phase() << std::endl;
    }
    
    return 0;
}