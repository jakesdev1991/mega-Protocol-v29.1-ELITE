ENTRY(_start)

PHDRS
{
    text PT_LOAD FLAGS(5);    /* Read + Execute */
    data PT_LOAD FLAGS(6);    /* Read + Write */
}

SECTIONS
{
    . = 0x100000;

    .text : {
        *(.text)
    } :text

    .rodata : {
        *(.rodata*)
    } :text

    .data : {
        *(.data)
    } :data

    .bss : {
        *(.bss)
        *(COMMON)
    } :data
}
