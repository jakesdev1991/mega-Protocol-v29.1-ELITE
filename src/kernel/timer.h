#ifndef TIMER_H
#define TIMER_H

#include <stdint.h>
#include "idt.h"

void init_timer(uint32_t frequency);
void timer_handler(struct regs *r);

#endif
