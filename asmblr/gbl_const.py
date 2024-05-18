from enum import Enum

reg_pos = [9, 6, 0]
flags = {"n": 1 << 11, "z": 1 << 10, "p": 1 << 9}

instrs_bin = dict(
    [
        ("ADD", 0b1 << 12),
        ("AND", 0b0101 << 12),
        ("BR", 0b0),
        ("GETC", (0b1111 << 12) + 0x20),
        ("HALT", (0b1111 << 12) + 0x25),
        ("IN", (0b1111 << 12) + 0x23),
        ("JMP", 0b1100 << 12),
        ("JMPT", (0b1100000 << 9) + 1),
        ("JSR", 0b01001 << 11),
        ("JSRR", 0b010000 << 9),
        ("LD", 0b0010 << 12),
        ("LDI", 0b1010 << 12),
        ("LDR", 0b0110 << 12),
        ("LEA", 0b1110 << 12),
        ("NOT", (0b1001 << 12) + 0b111111),
        ("OUT", (0b1111 << 12) + 0x21),
        ("PUTS", (0b1111 << 12) + 0x22),
        ("PUTSP", (0b1111 << 12) + 0x24),
        ("RET", 0b1100000111000000),
        ("RTI", 0b1000 << 12),
        ("RTT", 0b1100000111000001),
        ("ST", 0b0011 << 12),
        ("STI", 0b1011 << 12),
        ("STR", 0b0111 << 12),
        ("TRAP", 0b1111 << 12),
    ]
)
instrs_keys = instrs_bin.keys()

imm_bit_range = dict(
    (
        ("ADD", 5),
        ("AND", 5),
        ("BR", 9),
        ("GETC", 0),
        ("HALT", 0),
        ("IN", 0),
        ("JMP", 0),
        ("JMPT", 0),
        ("JSR", 11),
        ("JSRR", 0),
        ("LD", 9),
        ("LDI", 9),
        ("LDR", 6),
        ("LEA", 9),
        ("NOT", 9),
        ("OUT", 0),
        ("PUTS", 0),
        ("PUTSP", 0),
        ("RET", 0),
        ("RTI", 0),
        ("RTT", 0),
        ("ST", 9),
        ("STI", 9),
        ("STR", 6),
        ("TRAP", 8),
        ("UNDEFINED", 0),
    )
)

imm_mask = dict()
for im in imm_bit_range:
    imm_mask[im] = (1 << imm_bit_range[im]) - 1


class Result(Enum):
    NOT_FOUND = 0
    FOUND = 1
    BREAK = 2
