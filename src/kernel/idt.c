#include "idt.h"
#include "timer.h"
#include "io.h"

struct idt_entry {
    uint16_t base_low;
    uint16_t sel;        // Kernel segment selector
    uint8_t  always0;    // Always zero
    uint8_t  flags;      // IDT flags
    uint16_t base_high;
} __attribute__((packed));

struct idt_ptr {
    uint16_t limit;
    uint32_t base;
} __attribute__((packed));

struct idt_entry idt[256];
struct idt_ptr idtp;

extern void idt_load();
extern void isr0();
extern void isr14();
extern void isr128();
extern void irq0();
extern void irq1();

void irq_remap() {
    outb(0x20, 0x11);
    outb(0xA0, 0x11);
    outb(0x21, 0x20);
    outb(0xA1, 0x28);
    outb(0x21, 0x04);
    outb(0xA1, 0x02);
    outb(0x21, 0x01);
    outb(0xA1, 0x01);
    outb(0x21, 0x0);
    outb(0xA1, 0x0);
}

void idt_set_gate(uint8_t num, uint32_t base, uint16_t sel, uint8_t flags) {
    idt[num].base_low = (base & 0xFFFF);
    idt[num].base_high = (base >> 16) & 0xFFFF;
    idt[num].sel = sel;
    idt[num].always0 = 0;
    idt[num].flags = flags;
}

void init_idt() {
    idtp.limit = (sizeof(struct idt_entry) * 256) - 1;
    idtp.base = (uint32_t)&idt;

    // Clear IDT entries
    for (int i = 0; i < 256; i++) {
        idt_set_gate(i, 0, 0, 0);
    }

    irq_remap();

    // Register Divide-by-Zero (ISR 0)
    idt_set_gate(0, (uint32_t)isr0, 0x08, 0x8E);

    // Register Page Fault (ISR 14)
    idt_set_gate(14, (uint32_t)isr14, 0x08, 0x8E);

    // Register Timer (IRQ 0 -> IDT 32)
    idt_set_gate(32, (uint32_t)irq0, 0x08, 0x8E);

    // Register Keyboard (IRQ 1 -> IDT 33)
    idt_set_gate(33, (uint32_t)irq1, 0x08, 0x8E);

    // Register System Call (INT 0x80)
    idt_set_gate(128, (uint32_t)isr128, 0x08, 0x8E);

    idt_load();
}
