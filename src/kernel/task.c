#include "task.h"
#include "kheap.h"
#include "idt.h"
#include <stddef.h>

static struct task *current_task = NULL;
static struct task *task_list = NULL;
static uint32_t next_pid = 1;

void init_tasking() {
    // Current execution becomes the first task
    current_task = (struct task*)kmalloc(sizeof(struct task));
    current_task->id = next_pid++;
    current_task->state = 1; 
    current_task->next = current_task;
    task_list = current_task;
}

void create_task(void (*entry)()) {
    struct task *new_task = (struct task*)kmalloc(sizeof(struct task));
    new_task->id = next_pid++;
    new_task->state = 0;
    
    uint32_t stack_base = (uint32_t)kmalloc(4096);
    uint32_t *stack_ptr = (uint32_t*)(stack_base + 4096);
    
    // 1. Initial Stack Frame for iret (Ring 0 -> Ring 0)
    *(--stack_ptr) = 0x0202;        // EFLAGS (Interrupts enabled)
    *(--stack_ptr) = 0x08;          // CS (Kernel Code)
    *(--stack_ptr) = (uint32_t)entry; // EIP
    
    // 2. Dummy Error code and Interrupt Number
    *(--stack_ptr) = 0;             // err
    *(--stack_ptr) = 32;            // int_no
    
    // 3. pusha state
    *(--stack_ptr) = 0;             // eax
    *(--stack_ptr) = 0;             // ecx
    *(--stack_ptr) = 0;             // edx
    *(--stack_ptr) = 0;             // ebx
    *(--stack_ptr) = 0;             // esp (ignored by popa)
    *(--stack_ptr) = 0;             // ebp
    *(--stack_ptr) = 0;             // esi
    *(--stack_ptr) = 0;             // edi
    
    // 4. Data Segment
    *(--stack_ptr) = 0x10;          // ds
    
    new_task->esp = (uint32_t)stack_ptr;
    
    // Insert into circular linked list
    new_task->next = task_list->next;
    task_list->next = new_task;
}

// Global pointers for the assembly context switch
uint32_t current_task_esp_ptr = 0;
uint32_t next_task_esp = 0;

void schedule() {
    if (!current_task) return;
    
    struct task *prev = current_task;
    current_task = current_task->next;
    
    // Only set the pointers if we're actually switching
    if (prev != current_task) {
        current_task_esp_ptr = (uint32_t)&(prev->esp);
        next_task_esp = current_task->esp;
    }
}
