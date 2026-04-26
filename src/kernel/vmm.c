#include "vmm.h"
#include <stdint.h>

uint32_t page_directory[1024] __attribute__((aligned(4096)));
// Support mapping 16MB (4 page tables)
uint32_t page_tables[4][1024] __attribute__((aligned(4096)));

extern void loadPageDirectory(uint32_t*);
extern void enablePaging();

void init_paging() {
    // Identity map the first 16MB
    for(int t = 0; t < 4; t++) {
        for(int i = 0; i < 1024; i++) {
            uint32_t addr = (t * 1024 + i) * 4096;
            // Attributes: supervisor level, read/write, present
            page_tables[t][i] = addr | 3;
        }
        // Put page tables into page directory
        page_directory[t] = ((uint32_t)page_tables[t]) | 3;
    }

    // Fill the rest of the page directory as not present
    for(int i = 4; i < 1024; i++) {
        page_directory[i] = 0 | 2; 
    }

    loadPageDirectory(page_directory);
    enablePaging();
}
