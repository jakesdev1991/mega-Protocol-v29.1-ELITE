AS = nasm
CC = gcc
LD = ld

ASFLAGS = -f elf32
CFLAGS = -m32 -c -ffreestanding -fno-stack-protector -fno-builtin -nostdlib -nodefaultlibs -I.
LDFLAGS = -m elf_i386 -T link.ld

OBJS = boot.o gdt.o idt.o interrupt.o isr.o timer.o pmm.o vmm.o kheap.o task.o serial.o keyboard.o afds.o npu_dispatch.o manifold_bridge.o kernel.o \
       inference.o oracle_test.o oracle_weights.o

all: kernel-v8.1

boot.o: boot.asm
	$(AS) $(ASFLAGS) boot.asm -o boot.o

interrupt.o: interrupt.asm
	$(AS) $(ASFLAGS) interrupt.asm -o interrupt.o

gdt.o: gdt.c
	$(CC) $(CFLAGS) gdt.c -o gdt.o

idt.o: idt.c
	$(CC) $(CFLAGS) idt.c -o idt.o

isr.o: isr.c
	$(CC) $(CFLAGS) isr.c -o isr.o

timer.o: timer.c
	$(CC) $(CFLAGS) timer.c -o timer.o

pmm.o: pmm.c
	$(CC) $(CFLAGS) pmm.c -o pmm.o

vmm.o: vmm.c
	$(CC) $(CFLAGS) vmm.c -o vmm.o

kheap.o: kheap.c
	$(CC) $(CFLAGS) kheap.c -o kheap.o

task.o: task.c
	$(CC) $(CFLAGS) task.c -o task.o

serial.o: serial.c
	$(CC) $(CFLAGS) serial.c -o serial.o

keyboard.o: keyboard.c
	$(CC) $(CFLAGS) keyboard.c -o keyboard.o

afds.o: afds.c
	$(CC) $(CFLAGS) afds.c -o afds.o

npu_dispatch.o: npu_dispatch.c
	$(CC) $(CFLAGS) npu_dispatch.c -o npu_dispatch.o

manifold_bridge.o: manifold_bridge.c
	$(CC) $(CFLAGS) manifold_bridge.c -o manifold_bridge.o

inference.o: inference.c
	$(CC) $(CFLAGS) inference.c -o inference.o

oracle_test.o: oracle_test.c
	$(CC) $(CFLAGS) oracle_test.c -o oracle_test.o

oracle_weights.o: oracle_weights.bin
	objcopy -I binary -O elf32-i386 -B i386 \
	--rename-section .data=.oracle_weights,alloc,load,readonly,data,contents \
	oracle_weights.bin oracle_weights.o

kernel.o: kernel.c
	$(CC) $(CFLAGS) kernel.c -o kernel.o

kernel-v8.1: $(OBJS)
	$(LD) $(LDFLAGS) $(OBJS) -o kernel-v8.1

clean:
	rm -f *.o kernel-v*
