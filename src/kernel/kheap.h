#ifndef KHEAP_H
#define KHEAP_H

#include <stdint.h>
#include <stddef.h>

#define KHEAP_START 0x400000    // 4MB
#define KHEAP_SIZE  0x100000    // 1MB initial heap

void init_kheap();
void *kmalloc(size_t size);
void kfree(void *ptr);

#endif
