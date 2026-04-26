#include "omega_core.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// External function from hsa_mapper.c
extern int map_hsa_memory(UnifiedMemoryBlock* mem_block);
extern void unmap_hsa_memory(UnifiedMemoryBlock* mem_block);

int omega_sys_init(UnifiedMemoryBlock* mem_block) {
    if (!mem_block) return -1;
    
    printf("[Omega C-Core] Initializing Omega Protocol Unified Interface...\n");
    
    // Total size requested by user: 28GB (28,000,000,000 bytes)
    mem_block->total_size = 28000000000ULL;
    mem_block->current_head = 0;
    mem_block->base_address = NULL;
    
    int result = map_hsa_memory(mem_block);
    if (result == 0) {
        printf("[Omega C-Core] Successfully mapped 28GB HSA UMA Buffer at %p.\n", mem_block->base_address);
    } else {
        printf("[Omega C-Core] Failed to map HSA memory (Code %d).\n", result);
    }
    
    return result;
}

int omega_load_environment(UnifiedMemoryBlock* mem_block, const char* filepath) {
    if (!mem_block || !mem_block->base_address) return -1;
    
    printf("[Omega C-Core] Loading Environment from: %s\n", filepath);
    
    // In a pure implementation, we would memory-map the file directly into the
    // universal block using mmap or read directly without malloc.
    // For now we will simulate writing a header indicating the environment load.
    
    const char* env_header = "OMEGA_ENV_LOADED: ";
    size_t env_len = strlen(env_header);
    size_t path_len = strlen(filepath);
    
    if (mem_block->current_head + env_len + path_len < mem_block->total_size) {
        char* dest = (char*)mem_block->base_address + mem_block->current_head;
        memcpy(dest, env_header, env_len);
        dest += env_len;
        memcpy(dest, filepath, path_len);
        
        mem_block->current_head += (env_len + path_len + 1); // +1 for null terminator if needed implicitly
    }
    
    return 0;
}

void omega_execute_primitive(UnifiedMemoryBlock* mem_block, uint64_t cycles) {
    if (!mem_block || !mem_block->base_address) return;
    
    printf("[Omega C-Core] Beginning TOE Primitive Execution for %llu cycles.\n", (unsigned long long)cycles);
    
    for (uint64_t i = 0; i < cycles; ++i) {
        // Execute domain specific primitives acting directly on the mapped memory
        run_tokamak_primitive(mem_block, i);
        run_biology_primitive(mem_block, i);
        
        // Every 100 cycles print a minor status update
        if (i % 100 == 0) {
            double phi_n = 0.0, phi_d = 0.0, j_star = 0.0;
            calculate_informational_jerk(mem_block, &phi_n, &phi_d, &j_star);
            printf("  [Cycle %llu] Phi_N: %.4f | Phi_Delta: %.4f | J*: %.4f\n", 
                   (unsigned long long)i, phi_n, phi_d, j_star);
        }
    }
    printf("[Omega C-Core] Execution Complete.\n");
}

void omega_sys_shutdown(UnifiedMemoryBlock* mem_block) {
    if (!mem_block) return;
    printf("[Omega C-Core] Shutting down and unmapping memory...\n");
    unmap_hsa_memory(mem_block);
}
