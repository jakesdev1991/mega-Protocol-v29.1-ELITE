#ifndef NPU_DISPATCH_H
#define NPU_DISPATCH_H

#include <stdint.h>

// OMEGA OS: Asynchronous NPU Dispatch Protocol (XDNA 2)
// This header interfaces the kernel with the Ryzen AI 9 NPU for AI offloading.

typedef struct {
    uint32_t payload_addr;
    uint32_t payload_size;
    uint32_t context_ptr; // Pointer to 6-message history
} npu_task_t;

void init_npu_dispatch();
void dispatch_to_sarai(const char* message, uint32_t context_id);

// NPU Status Invariants
#define NPU_MIN_TOPS 50
#define NPU_POWER_THRESHOLD 15 // Watts

#endif
