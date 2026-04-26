#include "pmm.h"
#include <stdint.h>
#include <stddef.h>

#define MAX_PAGES (1024 * 1024 / 8) // Supporting up to 4GB of memory
uint32_t pmm_bitmap[MAX_PAGES];
uint32_t total_pages = 0;

void pmm_set_page(uint32_t page) {
    pmm_bitmap[page / 32] |= (1 << (page % 32));
}

void pmm_clear_page(uint32_t page) {
    pmm_bitmap[page / 32] &= ~(1 << (page % 32));
}

int pmm_test_page(uint32_t page) {
    return pmm_bitmap[page / 32] & (1 << (page % 32));
}

void init_pmm(multiboot_info_t *info) {
    uint32_t mem_kb = info->mem_lower + info->mem_upper;
    total_pages = (mem_kb * 1024) / PAGE_SIZE;

    // Initially mark all pages as used
    for (uint32_t i = 0; i < MAX_PAGES; i++) {
        pmm_bitmap[i] = 0xFFFFFFFF;
    }

    // Free memory regions based on multiboot map
    multiboot_memory_map_t *mmap = (multiboot_memory_map_t*)info->mmap_addr;
    while ((uint32_t)mmap < info->mmap_addr + info->mmap_length) {
        if (mmap->type == 1) { // Available
            uint32_t start_page = mmap->addr / PAGE_SIZE;
            uint32_t end_page = (mmap->addr + mmap->len) / PAGE_SIZE;
            for (uint32_t i = start_page; i < end_page; i++) {
                pmm_clear_page(i);
            }
        }
        mmap = (multiboot_memory_map_t*)((uint32_t)mmap + mmap->size + sizeof(mmap->size));
    }

    // Reserve first 1MB (Kernel + BIOS)
    for (uint32_t i = 0; i < 256; i++) {
        pmm_set_page(i);
    }
}

void *pmm_alloc_page() {
    for (uint32_t i = 0; i < total_pages; i++) {
        if (!pmm_test_page(i)) {
            pmm_set_page(i);
            return (void*)(i * PAGE_SIZE);
        }
    }
    return NULL;
}

void pmm_free_page(void *page) {
    uint32_t p = (uint32_t)page / PAGE_SIZE;
    pmm_clear_page(p);
}
