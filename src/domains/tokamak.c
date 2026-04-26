#include "../include/omega_core.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// Extern declaration for monitor functions
extern void _monitor_step(void* ms, double raw_value);
extern void calculate_informational_jerk(UnifiedMemoryBlock* mem_block, double* phi_n_out, double* phi_delta_out, double* j_star_out);

// Random generator roughly matching normal distribution just for simulation
static double get_random_normal() {
    double u1 = (double)rand() / RAND_MAX;
    double u2 = (double)rand() / RAND_MAX;
    return sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2) * 0.1;
}

void run_tokamak_primitive(UnifiedMemoryBlock* mem_block, uint64_t current_cycle) {
    if (!mem_block) return;
    
    // Simulate sensor sweep
    double raw_sensor = get_random_normal();
    
    // MS is mapped at base address.
    _monitor_step(mem_block->base_address, raw_sensor);
    
    if (current_cycle % 500 == 0) {
        double j_star = 0.0;
        calculate_informational_jerk(mem_block, NULL, NULL, &j_star);
        
        printf("[Tokamak Node] Simulation Output: J* = %.4f | Risk: %s \n", 
               j_star, j_star < 1.5 ? "LOW" : "HIGH");
        
        if (j_star >= 1.5) {
            printf(">>> Disruption (TQ) \\equiv Manifold Shredding Detected!\n");
        }
    }
}
