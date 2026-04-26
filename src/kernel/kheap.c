#include "kheap.h"
#include <stdint.h>
#include <stddef.h>

struct header {
    size_t size;
    int is_free;
    struct header *next;
};

static struct header *free_list = (struct header *)KHEAP_START;
static uint32_t heap_end = KHEAP_START + KHEAP_SIZE;

void init_kheap() {
    free_list->size = KHEAP_SIZE - sizeof(struct header);
    free_list->is_free = 1;
    free_list->next = NULL;
}

void *kmalloc(size_t size) {
    // 1. Alignment Enforcement (8-byte alignment)
    size = (size + 7) & ~7;
    
    struct header *curr = free_list;
    
    while (curr) {
        // 2. Bounds Checking
        if ((uint32_t)curr < KHEAP_START || (uint32_t)curr >= heap_end) {
            // In a real kernel, we would panic here. 
            // For now, we'll return NULL to indicate corruption.
            return NULL;
        }

        if (curr->is_free && curr->size >= size) {
            // Split block if possible (must leave enough room for another header + alignment)
            if (curr->size > size + sizeof(struct header) + 8) {
                struct header *new_block = (struct header *)((uint32_t)curr + sizeof(struct header) + size);
                new_block->size = curr->size - size - sizeof(struct header);
                new_block->is_free = 1;
                new_block->next = curr->next;
                
                curr->size = size;
                curr->next = new_block;
            }
            
            curr->is_free = 0;
            return (void *)((uint32_t)curr + sizeof(struct header));
        }
        curr = curr->next;
    }
    
    return NULL; // Out of memory
}

void kfree(void *ptr) {
    if (!ptr) return;
    
    struct header *h = (struct header *)((uint32_t)ptr - sizeof(struct header));
    
    // Safety check
    if ((uint32_t)h < KHEAP_START || (uint32_t)h >= heap_end) return;
    
    h->is_free = 1;
    
    // 3. Coalescing (Forward only for now, prev requires a doubly linked list)
    if (h->next && h->next->is_free) {
        h->size += h->next->size + sizeof(struct header);
        h->next = h->next->next;
    }
}
