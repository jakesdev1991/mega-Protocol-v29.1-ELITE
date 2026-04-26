global idt_load
global isr0
global isr14
global irq0
global irq1
global isr128
global isr_common
extern idtp
extern isr_handler
extern irq_handler
extern schedule
extern current_task_esp_ptr
extern next_task_esp

idt_load:
    lidt [idtp]
    ret

; ISR 0: Divide-by-Zero
isr0:
    cli
    push dword 0
    push dword 0
    jmp isr_common

; ISR 14: Page Fault
isr14:
    cli
    ; Page fault pushes an error code automatically
    push dword 14
    jmp isr_common

; IRQ 0: Timer
irq0:
    cli
    push dword 0
    push dword 32
    jmp irq_common

; IRQ 1: Keyboard
irq1:
    cli
    push dword 0
    push dword 33
    jmp irq_common

; ISR 128: System Call (int 0x80)
isr128:
    cli
    push dword 0
    push dword 128
    jmp isr_common

isr_common:
    pusha
    mov ax, ds
    push eax
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    push esp
    call isr_handler
    add esp, 4
    pop eax
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    popa
    add esp, 8
    sti
    iret

irq_common:
    pusha
    mov ax, ds
    push eax
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    
    push esp
    call irq_handler
    add esp, 4
    
    ; PREEMPTIVE SCHEDULING HANDOVER
    call schedule
    
    ; Check if we need to switch stacks
    mov eax, [current_task_esp_ptr]
    cmp eax, 0
    je .no_switch
    
    ; Perform the switch
    mov [eax], esp        ; Save current stack pointer into prev task
    mov esp, [next_task_esp] ; Load next task's stack pointer
    
    ; Reset the switch pointer to prevent re-switching
    mov dword [current_task_esp_ptr], 0

.no_switch:
    pop eax
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    popa
    add esp, 8
    sti
    iret

section .note.GNU-stack noalloc noexec nowrite progbits
