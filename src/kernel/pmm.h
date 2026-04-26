#ifndef PMM_H
#define PMM_H

#include <stdint.h>
#include "multiboot.h"

#define PAGE_SIZE 4096

void init_pmm(multiboot_info_t *info);
void *pmm_alloc_page();
void pmm_free_page(void *page);

#endif
