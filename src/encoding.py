from enum import Enum

LABEL_IDENTIFIER = ":"


class PseudoOpCode:
    ORIG = ".ORIG"
    FILL = ".FILL"
    BLKW = ".BLKW"
    STRINGZ = ".STRINGZ"
    END = ".END"


class OpCode:
    ADD = "ADD"
    BITWISE_AND = "AND"
    BRANCH = "BR"
    JUMP = "JMP"
    JUMP_TO_REGISTER_BY_LABEL = "JSR"
    JUMP_TO_REGISTER_BY_BASE_REGISTER = "JSRR"
    LOAD = "LD"
    LOAD_INDIRECT = "LDI"
    LOAD_REGISTER = "LDR"
    LOAD_EFFECTIVE_ADDRESS = "LEA"
    BITWISE_NOT = "NOT"
    RETURN_JUMP = "RET"
    STORE = "ST"
    STORE_INDIRECT = "STI"
    STORE_REGISTER = "STR"
    UNUSED = "RTI"


class OperandType(Enum):
    REGISTER = 1
    NUMERAL = 2
    REGISTER_XOR_NUMERAL = 3
    LABEL = 4


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
        OpCode.ADD: 0b1 << 12,
        OpCode.BITWISE_AND: 0b0101 << 12,
        OpCode.BRANCH: 0b0,
        OpCode.JUMP: 0b1100 << 12,
        OpCode.JUMP_TO_REGISTER_BY_LABEL: 0b01001 << 11,
        OpCode.JUMP_TO_REGISTER_BY_BASE_REGISTER: 0b010000 << 9,
        OpCode.LOAD: 0b0010 << 12,
        OpCode.LOAD_INDIRECT: 0b1010 << 12,
        OpCode.LOAD_REGISTER: 0b0110 << 12,
        OpCode.LOAD_EFFECTIVE_ADDRESS: 0b1110 << 12,
        OpCode.BITWISE_NOT: (0b1001 << 12) + 0b111111,
        OpCode.RETURN_JUMP: 0b1100000111000000,
        OpCode.UNUSED: 0b1000 << 12,
        OpCode.STORE: 0b0011 << 12,
        OpCode.STORE_INDIRECT: 0b1011 << 12,
        OpCode.STORE_REGISTER: 0b0111 << 12,
    }
