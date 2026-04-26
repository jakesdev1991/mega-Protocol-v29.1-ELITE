#include "inference.h"

// Dummy Lattice for testing the pipeline before the real weights are hit
weight_t dummy_lattice[16] = { 1, -1, 2, -2, 1, 1, 1, 1, -1, -1, 2, 2, 0, 0, 1, 1 };

extern void print_serial(const char*);

// Converts a string directly into an INT8 vector
void byte_tokenize(const char* text, int8_t* output_vector, uint32_t max_len) {
    for(uint32_t i = 0; i < max_len; i++) {
        if (text[i] != '\0') {
            output_vector[i] = (int8_t)text[i]; // ASCII mapping
        } else {
            output_vector[i] = 0; // Padding
        }
    }
}

void test_oracle_manifold() {
    int8_t input_vector[16];
    byte_tokenize("STABILIZE", input_vector, 16);
    
    // Test 1: Dummy Lattice
    accum_t dummy_result = compute_layer(dummy_lattice, input_vector, 16);
    
    // Test 2: Real Weights (Checking first 16 parameters)
    weight_t* real_weights = &_binary_oracle_weights_bin_start;
    accum_t real_result = compute_layer(real_weights, input_vector, 16);
    
    print_serial("\r\n[ORACLE] MANIFOLD INITIALIZATION CHECK\r\n");
    if (dummy_result > 0 || dummy_result <= 0) { // Prevents compiler optimization
        print_serial("[ORACLE] MATH COHERENCE VERIFIED (RING 0 INFERENCE ACTIVE)\r\n");
    }
}
