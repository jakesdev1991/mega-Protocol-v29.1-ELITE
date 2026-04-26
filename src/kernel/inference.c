#include "inference.h"

// Safe INT8 Dot-Product (No FPU required)
accum_t compute_layer(weight_t* weights, int8_t* inputs, uint32_t length) {
    accum_t sum = 0;
    for (uint32_t i = 0; i < length; i++) {
        sum += (accum_t)weights[i] * (accum_t)inputs[i];
    }
    // Simple ReLU Activation
    return (sum > 0) ? sum : 0;
}
