#include <stdint.h>
#include "timer.h"
#include "idt.h"
#include "io.h"

uint32_t timer_ticks = 0;

void timer_handler(struct regs *r) {
    timer_ticks++;
    
    // Optional: Write a simple ticker to the VGA buffer to prove it works
    if (timer_ticks % 18 == 0) { // Approx once per second (18.22 Hz is default, but we'll set it)
        char *vidptr = (char*)0xb8000;
        static int toggle = 0;
        vidptr[158] = toggle ? '*' : ' ';
        vidptr[159] = 0x0F; // White on Black
        toggle = !toggle;
    }
}

void init_timer(uint32_t frequency) {
    // The value we send to the PIT is the value to divide its input clock
    // (1193180 Hz) by, to get our desired frequency
    uint32_t divisor = 1193180 / frequency;

    // Send the command byte
    outb(0x43, 0x36);

    // Divisor has to be sent byte-wise, so split here into upper/lower bytes
    uint8_t l = (uint8_t)(divisor & 0xFF);
    uint8_t h = (uint8_t)((divisor >> 8) & 0xFF);

    // Send the frequency divisor
    outb(0x40, l);
    outb(0x40, h);
}
