class PseudoOpCode:
    ORIG = ".ORIG"
    FILL = ".FILL"
    BLKW = ".BLKW"
    STRINGZ = ".STRINGZ"
    END = ".END"


class OpCode:
    ADD = "ADD"
    AND = "AND"
    BR = "BR"
    JMP = "JMP"
    JSR = "JSR"
    JSRR = "JSRR"
    LD = "LD"
    LDI = "LDI"
    LDR = "LDR"
    LEA = "LEA"
    NOT = "NOT"
    RET = "RET"
    RTI = "RTI"
    ST = "ST"
    STI = "STI"
    STR = "STR"


class Encodings:
    """To compose 16 bit words.

    Attributes:
        REGISTER_OPERANDS_POSITION: first bit position in word for 3 bits register id.
            Operations could have from 0 to 3 registers operands defined in a word
            following the declaration pattern - first on 11,10,9 bit, second on
            8,7,6 bit, third 2,1,0.
        CONDITION_FLAGS: To indicate the sign of the previous calculation.
        DIRECTIVE_CODES: Set of assembler 'pseudo operations' which generate a piece of
            code or data (like macros).
        OPERATION_ENCODING: Encoding for tasks representation that the CPU knows how
            to process.
        OPERATION_IMMEDIATE_VALUE_FLAG_POSITION: Flag position defining mode in word for
            operations having immediate value operand option.
        IMMEDIATE_MASK: To identify immediate mode for OP CODEs.

    """

    REGISTER_OPERANDS_POSITION = [9, 6, 0]
    CONDITION_FLAGS = {"n": 1 << 11, "z": 1 << 10, "p": 1 << 9}
    DIRECTIVE_CODES = (
        PseudoOpCode.ORIG,
        PseudoOpCode.FILL,
        PseudoOpCode.BLKW,
        PseudoOpCode.STRINGZ,
        PseudoOpCode.END,
    )
    REGISTERS_ENCODING = {
        f"R{r}": r for r in range(8)
    }  # literals R0-R7 with encodings from 0b000 to 0b111
    OPERATION_ENCODING = {
        OpCode.ADD: 0b1 << 12,  # add
        OpCode.AND: 0b0101 << 12,  # bitwise and
        OpCode.BR: 0b0,  # branch
        OpCode.JMP: 0b1100 << 12,  # jump
        OpCode.JSR: 0b01001 << 11,  # jump to register by label
        OpCode.JSRR: 0b010000 << 9,  # jump to register by base register
        OpCode.LD: 0b0010 << 12,  # load
        OpCode.LDI: 0b1010 << 12,  # load indirect
        OpCode.LDR: 0b0110 << 12,  # load register
        OpCode.LEA: 0b1110 << 12,  # load effective address
        OpCode.NOT: (0b1001 << 12) + 0b111111,  # bitwise not
        OpCode.RET: 0b1100000111000000,  # return / jump
        OpCode.RTI: 0b1000 << 12,  # unused
        OpCode.ST: 0b0011 << 12,  # store
        OpCode.STI: 0b1011 << 12,  # store indirect
        OpCode.STR: 0b0111 << 12,  # store register
    }
    TRAP_ROUTINES = {
        "GETC": (0b1111 << 12) + 0x20,
        "OUT": (0b1111 << 12) + 0x21,
        "PUTS": (0b1111 << 12) + 0x22,
        "IN": (0b1111 << 12) + 0x23,
        "PUTSP": (0b1111 << 12) + 0x24,
        "HALT": (0b1111 << 12) + 0x25,
    }
    OPERATION_IMMEDIATE_VALUE_FLAG_POSITION = {
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
    for im in OPERATION_IMMEDIATE_VALUE_FLAG_POSITION.keys():
        IMMEDIATE_MASK[im] = (1 << OPERATION_IMMEDIATE_VALUE_FLAG_POSITION[im]) - 1
