#include <stdint.h>
#include "multiboot.h"
#include "pmm.h"
#include "vmm.h"
#include "kheap.h"
#include "task.h"

extern void init_gdt();
extern void init_idt();
extern void init_timer(uint32_t);
extern void init_serial();
extern void init_afds();
extern void init_manifold_bridge();
extern void print_serial(const char*);
extern void test_oracle_manifold();

void print_hex(uint32_t n) {
    const char *hex = "0123456789ABCDEF";
    char *vidptr = (char*)0xb8000;
    static int line = 5;
    int offset = line * 160;
    
    for (int i = 7; i >= 0; i--) {
        vidptr[offset + i * 2] = hex[n & 0xF];
        vidptr[offset + i * 2 + 1] = 0x0E; // Yellow
        n >>= 4;
    }
    line++;
}

void task_a() {
    while (1) {
        print_serial("[TASK-A] MANIFOLD COHERENCE STABLE\r\n");
        asm volatile("hlt"); // CPU sleeps until next 50Hz tick
    }
}

void task_b() {
    while (1) {
        print_serial("[TASK-B] RCOD FLUX MONITORING ACTIVE\r\n");
        asm volatile("hlt"); // CPU sleeps until next 50Hz tick
    }
}

void kmain(uint32_t magic, multiboot_info_t *info) {
    init_gdt();
    init_idt();
    init_serial();
    init_timer(50); // 50 Hz heartbeat (20ms quantum)
    init_afds();
    init_manifold_bridge();
    
    print_serial("\r\n[OMEGA-OS] MANIFOLD HANDSHAKE COMPLETE - SERIAL DEBUG ACTIVE\r\n");

    if (magic == MULTIBOOT_MAGIC) {
        init_pmm(info);
        init_paging();
        init_kheap();
        print_serial("[OMEGA-OS] HEAP & VIRTUAL MEMORY INITIALIZED - MANIFOLD STABILIZED\r\n");
        
        // Boot the Oracle
        test_oracle_manifold();
        
        init_tasking();
        create_task(task_a);
        create_task(task_b);
        print_serial("[OMEGA-OS] PREEMPTIVE MULTITASKING INITIALIZED - PERSISTENCE ENABLED\r\n");
    }

    asm volatile("sti"); // ENABLE INTERRUPTS

    const char *str = "OMEGA OS: MANIFOLD ACTIVE - PREEMPTION RUNNING";
    char *vidptr = (char*)0xb8000;
    unsigned int i = 0;
    unsigned int j = 0;

    /* clear screen */
    while(j < 80 * 25 * 2) {
        vidptr[j] = ' ';
        vidptr[j+1] = 0x07;
        j = j + 2;
    }

    j = 0;
    while(str[i] != '\0') {
        vidptr[j] = str[i];
        vidptr[j+1] = 0x0F; 
        i++;
        j = j + 2;
    }

    // Idle Loop
    while(1) {
        asm volatile("hlt");
    }
}
