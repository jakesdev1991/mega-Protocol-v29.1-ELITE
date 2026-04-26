[bits 32]
section .text
        align 4
        dd 0x1BADB002              ; multiboot magic
        dd 0x03                    ; flags: align modules + mem info
        dd - (0x1BADB002 + 0x03)   ; checksum

global _start
global idt_load
global gdt_flush
global loadPageDirectory
global enablePaging
global switch_to
extern idtp
extern kmain
extern isr_common

loadPageDirectory:
    push ebp
    mov ebp, esp
    mov eax, [ebp+8]          ; Fix: Use EBP for arguments
    mov cr3, eax
    mov esp, ebp
    pop ebp
    ret

enablePaging:
    push ebp
    mov ebp, esp
    mov eax, cr0
    or eax, 0x80000000        ; Fix: Only touch PG (bit 31)
    mov cr0, eax
    mov esp, ebp
    pop ebp
    ret

switch_to:
    push ebp
    push ebx
    push esi
    push edi

    mov eax, [esp+20]         ; address of old_esp
    mov [eax], esp            ; save current ESP

    mov esp, [esp+24]         ; load new ESP

    pop edi
    pop esi
    pop ebx
    pop ebp
    ret

gdt_flush:
    mov eax, [esp+4]
    lgdt [eax]
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    jmp 0x08:.flush
.flush:
    ret

_start:
        cli                        ; disable interrupts
        mov esp, stack_space       ; set up stack
        and esp, -16               ; align stack to 16 bytes
        
        push ebx                   ; Push Multiboot info structure pointer
        push eax                   ; Push Multiboot magic number
        
        call kmain
        
.halt:
        hlt                        ; halt the CPU
        jmp .halt                  ; loop if NMI triggers

section .bss
align 16
resb 8192                          ; 8KB for stack
stack_space:

section .note.GNU-stack noalloc noexec nowrite progbits ; Fix executable stack warning
