from enum import Enum


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


class OperandType(Enum):
    REGISTER = 1
    NUMERAL = 2
    REGISTER_XOR_NUMERAL = 3


class Encoding:
    """To compose 16 bit words.

    Attributes:
        REGISTER_OPERANDS_POSITION: first bit position in word for 3 bits register id.
            Operations could have from 0 to 3 registers operands defined in a word
            following the declaration pattern - first on 11,10,9 bit, second on
            8,7,6 bit, third 2,1,0.
        CONDITION_FLAGS: To indicate the sign of the previous calculation.
        DIRECTIVE_CODES: Set of assembler 'pseudo operations' which generate a piece of
            code or data (like macros).
        OPERATION: Encoding for tasks representation that the CPU knows how to process.
    """

    REGISTER_OPERANDS_POSITION = [9, 6, 0]
    BASE_REGISTER_POSITION = 6
    CONDITION_FLAGS = {"n": 1 << 11, "z": 1 << 10, "p": 1 << 9}
    DIRECTIVE_CODES = (
        PseudoOpCode.ORIG,
        PseudoOpCode.FILL,
        PseudoOpCode.BLKW,
        PseudoOpCode.STRINGZ,
        PseudoOpCode.END,
    )
    REGISTERS = {
        f"R{r}": r for r in range(8)
    }  # literals R0-R7 with encodings from 0b000 to 0b111
    OPERATION = {
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
