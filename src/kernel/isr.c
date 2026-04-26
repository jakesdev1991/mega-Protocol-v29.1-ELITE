#include <stdint.h>
#include "idt.h"
#include "timer.h"
#include "io.h"
extern void afds_log_syscall(uint32_t);
extern void dispatch_to_sarai(const char*, uint32_t);
extern void keyboard_handler();

void isr_handler(struct regs *r) {
    char *vidptr = (char*)0xb8000;

    if (r->int_no == 128) {
        // System Call Dispatcher
        afds_log_syscall(r->eax);

        switch (r->eax) {
            case 1: // print_serial
                print_serial((const char*)r->ebx);
                break;
            case 2: // dispatch_to_sarai
                dispatch_to_sarai((const char*)r->ebx, r->ecx);
                break;
            default:
                print_serial("[SYSCALL] UNKNOWN SYSTEM CALL\r\n");
                break;
        }
        return;
    }

    if (r->int_no == 14) {
...
        uint32_t fault_addr;
        asm volatile("mov %%cr2, %0" : "=r" (fault_addr));
        
        print_serial("\r\n[OMEGA-OS] !!! PAGE FAULT !!!\r\n");
        
        const char *msg = "PAGE FAULT - MANIFOLD BREACH DETECTED";
        int j = 160 * 3; 
        for(int i=0; msg[i] != '\0'; i++) {
            vidptr[j] = msg[i];
            vidptr[j+1] = 0x4F;
            j += 2;
        }
    } else {
        const char *msg = "CPU EXCEPTION DETECTED - SINGULARITY PROTECTED";
        int j = 160 * 2; 
        for(int i=0; msg[i] != '\0'; i++) {
            vidptr[j] = msg[i];
            vidptr[j+1] = 0x4F; 
            j += 2;
        }
    }
    for(;;); 
}

void irq_handler(struct regs *r) {
    // 1. Send EOI to PIC (End of Interrupt)
    if (r->int_no >= 40) {
        outb(0xA0, 0x20); // Slave PIC
    }
    outb(0x20, 0x20); // Master PIC

    // 2. Dispatch to specific handler
    if (r->int_no == 32) {
        timer_handler(r);
    } else if (r->int_no == 33) {
        keyboard_handler();
    }
}
