#include "../include/omega_core.h"
#include <stdio.h>
#include <unistd.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <errno.h>

// Translates to MAP_ANONYMOUS | MAP_SHARED with NO_RESERVE if available,
// representing the 28GB Peladn HO5 memory block mapping under Linux.
// Under proper HSA Linux setup, the AMD drivers will manage MAP_SHARED 
// gracefully without physical OOM unless touched simultaneously.
#ifndef MAP_NORESERVE
#define MAP_NORESERVE 0x4000
#endif

int map_hsa_memory(UnifiedMemoryBlock* mem_block) {
    if (!mem_block) return -1;
    
    printf("[HSA Mapper] Requesting Linux kernel to map %zu bytes (%.2f GB) of UMA memory...\n", 
           mem_block->total_size, (double)mem_block->total_size / (1024ULL * 1024ULL * 1024ULL));

    // For a real heterogeneous architecture like Peladn HO5 running Gentoo, 
    // memory mapped MAP_SHARED|MAP_ANONYMOUS (or via a special dri/hsa node) 
    // routes purely to the unified system physical RAM.
    int flags = MAP_SHARED | MAP_ANONYMOUS | MAP_NORESERVE;
    
    // MAP_POPULATE could enforce immediate allocation, but we want a fluid block
    void* ptr = mmap(NULL, mem_block->total_size, PROT_READ | PROT_WRITE, flags, -1, 0);

    if (ptr == MAP_FAILED) {
        perror("[HSA Mapper] mmap failed");
        return errno;
    }

    mem_block->base_address = ptr;
    return 0;
}

void unmap_hsa_memory(UnifiedMemoryBlock* mem_block) {
    if (!mem_block || !mem_block->base_address) return;
    
    if (munmap(mem_block->base_address, mem_block->total_size) != 0) {
        perror("[HSA Mapper] munmap failed");
    } else {
        printf("[HSA Mapper] Successfully unmapped %.2f GB UMA block.\n", 
               (double)mem_block->total_size / (1024ULL * 1024ULL * 1024ULL));
    }
    
    mem_block->base_address = NULL;
    mem_block->current_head = 0;
}
