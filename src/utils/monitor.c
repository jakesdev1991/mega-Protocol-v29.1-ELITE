#include "../include/omega_core.h"
#include <math.h>

#define MAX_NODES 10
#define NODE_DIM 32
#define QUANTIZE_SCALE 20.0
#define TOL_BANDS 1

typedef struct {
    double alpha[MAX_NODES];
    double state[MAX_NODES];
    bool init[MAX_NODES];
    int rings[MAX_NODES][NODE_DIM];
    int head[MAX_NODES];
    int count[MAX_NODES];
    
    double prev_vel;
    double prev_accel;
} MonitorState;

// Provide a mock static state buffer mapped right onto the unified block 
// in this simplified structure.
static MonitorState* get_monitor_state(UnifiedMemoryBlock* mem_block) {
    if (!mem_block) return NULL;
    
    // We locate the monitor state at the very beginning of the unified block for demo routing
    MonitorState* ms = (MonitorState*)mem_block->base_address;
    
    static bool initialized = false;
    if (!initialized) {
        for (int i = 0; i < MAX_NODES; i++) {
            ms->alpha[i] = 1.0 - (i * 0.07);
            ms->state[i] = 0.0;
            ms->init[i] = false;
            ms->head[i] = 0;
            ms->count[i] = 0;
            for (int j = 0; j < NODE_DIM; j++) {
                ms->rings[i][j] = 0;
            }
        }
        ms->prev_vel = 0.0;
        ms->prev_accel = 0.0;
        initialized = true;
    }
    return ms;
}

static inline double get_jerk(MonitorState* ms, double new_vel) {
    double accel = new_vel - ms->prev_vel;
    ms->prev_vel = new_vel;
    
    double jerk = accel - ms->prev_accel;
    ms->prev_accel = accel;
    
    return jerk;
}

void calculate_informational_jerk(UnifiedMemoryBlock* mem_block, double* phi_n_out, double* phi_delta_out, double* j_star_out) {
    MonitorState* ms = get_monitor_state(mem_block);
    if (!ms) return;
    
    // For calculating max overlapping cohesive banded sequences
    int latest_vals[MAX_NODES] = {0};
    int node_active = 0;
    
    for (int i = 0; i < MAX_NODES; i++) {
        if (ms->count[i] > 0) {
            int idx_to_read = (ms->head[i] - 1 + NODE_DIM) % NODE_DIM;
            latest_vals[i] = ms->rings[i][idx_to_read];
            node_active++;
        }
    }
    
    // Sort array (Bubble sort for N=10 is fine)
    for (int i = 0; i < MAX_NODES - 1; i++) {
        for (int j = 0; j < MAX_NODES - i - 1; j++) {
            if (latest_vals[j] > latest_vals[j+1]) {
                int temp = latest_vals[j];
                latest_vals[j] = latest_vals[j+1];
                latest_vals[j+1] = temp;
            }
        }
    }
    
    int max_c = 1;
    for (int i = 0; i < MAX_NODES; i++) {
        int j = i;
        while (j + 1 < MAX_NODES && (latest_vals[j+1] - latest_vals[i]) <= TOL_BANDS) {
            j++;
        }
        if ((j - i + 1) > max_c) {
            max_c = (j - i + 1);
        }
    }
    
    // Mean state
    double mean_state = 0.0;
    double fast_mean = 0.0, slow_mean = 0.0;
    
    for (int i = 0; i < MAX_NODES; i++) {
        mean_state += ms->state[i];
        if (i < 3) fast_mean += ms->state[i];
        if (i >= 7) slow_mean += ms->state[i];
    }
    mean_state /= MAX_NODES;
    fast_mean /= 3.0;
    slow_mean /= 3.0; // Max nodes 10, indices 7,8,9 (3 nodes)
    
    double phi_plus = fmax(1e-6, fmin(1.0, (double)max_c / MAX_NODES));
    double phi_minus = fmax(1e-6, fmin(1.0, mean_state));
    
    double phi_n = sqrt(phi_plus * phi_minus);
    double phi_delta = 0.5 * fabs(log(phi_plus / phi_minus));
    if (phi_delta > 1.0) phi_delta = 1.0;
    
    double vel = fast_mean - slow_mean;
    double jerk = get_jerk(ms, vel);
    
    double j_star = fabs(jerk) / (pow(phi_n, 2) + 1e-6);
    
    if (j_star > 1.5) {
        // Boost Phi_Delta
        phi_delta *= 1.25;
        if (phi_delta > 1.0) phi_delta = 1.0;
    }
    
    if (phi_n_out) *phi_n_out = phi_n;
    if (phi_delta_out) *phi_delta_out = phi_delta;
    if (j_star_out) *j_star_out = j_star;
}

// Simulates stepping raw sensor values into the monitoring ring buffer
void _monitor_step(MonitorState* ms, double raw_value) {
    for (int i = 0; i < MAX_NODES; i++) {
        if (!ms->init[i]) {
            ms->state[i] = raw_value;
            ms->init[i] = true;
        } else {
            ms->state[i] = ms->alpha[i] * raw_value + (1.0 - ms->alpha[i]) * ms->state[i];
        }
        
        int q_val = (int)round(ms->state[i] * QUANTIZE_SCALE);
        ms->rings[i][ms->head[i]] = q_val;
        
        ms->head[i] = (ms->head[i] + 1) % NODE_DIM;
        if (ms->count[i] < NODE_DIM) ms->count[i]++;
    }
}
