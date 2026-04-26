#ifndef TASK_H
#define TASK_H

#include <stdint.h>

struct task {
    uint32_t id;
    uint32_t esp;               // Current stack pointer (saved state)
    struct task *next;          // Linked list of tasks
    uint32_t state;             // 0=Ready, 1=Running
};

void init_tasking();
void create_task(void (*entry)());
void schedule(); // The preemptive scheduler

#endif
