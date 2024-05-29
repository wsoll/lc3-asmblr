class Encodings:
    """To compose 16 bit words.

    Attributes:
        REGISTER_ROW_BIT_ORIGIN: 3 bit addresses registers (R1-R7) first bit position.
        CONDITION_FLAGS: To indicate the sign of the previous calculation.
        DIRECTIVE_CODES: Set of assembler 'pseudo operations' which generate a piece of
            code or data (like macros).
        OPERATION_ENCODING: Encoding for tasks representation that the CPU knows how
            to process.
        IMMEDIATE_MODE_FLAG_POSITION: To identify immediate mode for specific OP CODE.
        IMMEDIATE_MASK: To identify immediate mode for OP CODEs.

    """

    REGISTER_ROW_BIT_ORIGIN = [9, 6, 0]
    CONDITION_FLAGS = {"n": 1 << 11, "z": 1 << 10, "p": 1 << 9}
    DIRECTIVE_CODES = (".ORIG", ".FILL", ".BLKW", ".STRINGZ", ".END")
    OPERATION_ENCODING = {
        "ADD": 0b1 << 12,  # add
        "AND": 0b0101 << 12,  # bitwise and
        "BR": 0b0,  # branch
        "JMP": 0b1100 << 12,  # jump
        "JSR": 0b01001 << 11,  # jump to register by label
        "JSRR": 0b010000 << 9,  # jump to register by base register
        "LD": 0b0010 << 12,  # load
        "LDI": 0b1010 << 12,  # load indirect
        "LDR": 0b0110 << 12,  # load register
        "LEA": 0b1110 << 12,  # load effective address
        "NOT": (0b1001 << 12) + 0b111111,  # bitwise not
        "RET": 0b1100000111000000,  # return / jump
        "RTI": 0b1000 << 12,  # unused
        "ST": 0b0011 << 12,  # store
        "STI": 0b1011 << 12,  # store indirect
        "STR": 0b0111 << 12,  # store register
    }
    TRAP_ROUTINES = {
        "GETC": (0b1111 << 12) + 0x20,
        "OUT": (0b1111 << 12) + 0x21,
        "PUTS": (0b1111 << 12) + 0x22,
        "IN": (0b1111 << 12) + 0x23,
        "PUTSP": (0b1111 << 12) + 0x24,
        "HALT": (0b1111 << 12) + 0x25,
    }
    IMMEDIATE_MODE_FLAG_POSITION = {
        "ADD": 5,
        "AND": 5,
        "BR": 9,
        "JSR": 11,
        "LD": 9,
        "LDI": 9,
        "LDR": 6,
        "LEA": 9,
        "NOT": 9,
        "ST": 9,
        "STI": 9,
        "STR": 6,
        "TRAP": 8,
    }
    IMMEDIATE_MASK = {}
    for im in IMMEDIATE_MODE_FLAG_POSITION.keys():
        IMMEDIATE_MASK[im] = (1 << IMMEDIATE_MODE_FLAG_POSITION[im]) - 1
