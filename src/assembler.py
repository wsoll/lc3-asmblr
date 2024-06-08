from array import array
from copy import deepcopy

from encoding import PseudoOpCode, Encoding
from instruction_set import InstructionSet
from logger import Logger
from syntax import (
    parse_instruction,
    validate_directive_syntax,
    is_numeral_base_prefixed,
    cast_to_numeral,
    is_valid_goto_label,
    DirectiveArgCount,
)


class Assembler(InstructionSet, Logger):
    """Encodes human-readable assembly file to LC3-readable binary file.

    Assembly file contains instructions (lines) that have both an operation code which
    indicates the kind of task to perform and a set of parameters (operands) which
    provide to the task being performed. Every line is encoded with 16-bit/2-bytes word.

    Attributes:
        big_endian: defines if encoding for parsing to bytes has to be big or little
            endian, e.g.: b"\x50\x43" in Big-Endian: 0x5043, Little-endian: 0x4350
        origin: added on the beginning of assembly file while parsing to bytes.
        line_counter: counts current assembly file line.
        end_flag: set to true if encounters .END instruction in an assembly file to
            raise an exception if any instruction remains afterward.
        memory: actual encoding of assembly file that contains machine code for LC-3.

    """

    def __init__(self, big_endian: bool = True, verbose: bool = False):
        super().__init__(verbose)
        self.origin = self.program_counter = 0x3000
        self.big_endian = big_endian
        self.line_counter = -1
        self.end_flag = False

        # ToDo-3: May be connected with line_counter
        self.memory = array("H", [0] * (1 << 16))

    def read_assembly(self, line: str) -> None:
        if self.end_flag:
            raise IndexError("Main program is finished after '.END' directive.")
        self.line_counter += 1

        # ToDo: Check if code exists in line, parse separately for directive and opcode
        instruction = parse_instruction(line)

        if not instruction:
            self._logger.debug(f"Line[{self.line_counter}]: empty.")
            return

        for directive_code in Encoding.DIRECTIVE_CODES:
            if directive_code in instruction:
                self.process_directive(instruction, directive_code)
                return

        for operation_key in Encoding.OPERATION.keys():
            if operation_key in instruction:
                self.process_instruction(instruction, operation_key)
                return

    def process_directive(self, instruction: list[str], code: str) -> None:
        match code:
            case PseudoOpCode.ORIG:
                self.process_origin(instruction)
            case PseudoOpCode.FILL:
                self.process_fill(instruction)
            case PseudoOpCode.BLKW:
                self.process_block_of_words(instruction)
            case PseudoOpCode.STRINGZ:
                self.process_string_with_zero(instruction)
            case PseudoOpCode.END:
                if len(instruction) != 1:
                    raise SyntaxError("Directive '.END' does not accept operands.")
                self.end_flag = True

    def process_instruction(self, instruction: list[str], operation_code: str) -> None:
        # ToDo: process BR/BRANCH firsts.
        # ToDo: With or Without label.
        binary_representation = 0x0000
        binary_representation |= Encoding.OPERATION[operation_code]

        operands_with_separator = instruction[1:]
        operands = [operand.strip(",") for operand in operands_with_separator]
        binary_representation |= self.process_operands(operation_code, operands)

        self.write_to_memory(binary_representation)
        self.program_counter += 1

    def write_to_memory(self, value: int) -> None:
        if value < 0:
            value = (1 << 16) + value
        self.memory[self.program_counter] = value

    def process_origin(self, instruction: list[str]) -> None:
        """Define starting address of program. If not setup default 0x3000

        syntax: .ORIG address
            .ORIG: The directive keyword.
            address: a 16-bit memory address where the program or data block will start.
        """
        if self.line_counter != 0:
            raise SyntaxError(".ORIG has to be placed before a main program.")

        if instruction[0] != ".ORIG":
            raise SyntaxError("'.ORIG' has to be first argument in the instruction.")

        if len(instruction) != DirectiveArgCount.WITHOUT_GOTO_LABEL.value:
            raise ValueError("Instruction with '.ORIG' cannot work with label.")

        value = cast_to_numeral(
            operand=instruction[1], allow_decimal=False, allow_binary=False
        )
        self.origin = self.program_counter = value

    def process_fill(self, instruction: list[str]) -> None:
        """Allocate one word, initialize with word.

        syntax: label .FILL value
            label: (Optional) A symbolic name for the memory location being defined.
            .FILL: The directive keyword.
            value: A 16-bit value to store in the allocated memory location. This
                can be a literal number (in decimal, hexadecimal, or binary format)
                or a symbolic constant.
        """
        arg_count = validate_directive_syntax(instruction, ".FILL")

        # ToDo-1: remove duplication if pattern
        operand = instruction[arg_count.value - 1]
        if is_numeral_base_prefixed(operand):
            value = cast_to_numeral(operand)
            self.write_to_memory(value)
        elif is_valid_goto_label(operand):
            raise NotImplementedError()
        else:
            msg = "Invalid '.FILL' operand."
            self._logger.error(msg)
            raise SyntaxError(msg)

        self.program_counter += 1

    def process_block_of_words(self, instruction: list[str]) -> None:
        """Allocate multiple words of storage, value unspecified.

        syntax: label .BLKW n
            label: (Optional) A symbolic name for the memory location being defined.
            .BLKW : The directive keyword.
            n: number of words to allocate.
        """

        arg_count = validate_directive_syntax(instruction, ".BLKW")

        operand = instruction[arg_count.value - 1]  # ToDo: (ToDo-1 reference)
        if is_numeral_base_prefixed(operand):
            words_to_allocate = cast_to_numeral(
                operand, allow_hexadecimal=False, allow_binary=False
            )
            self.program_counter += words_to_allocate
        elif is_valid_goto_label(operand):
            raise NotImplementedError()
        else:
            msg = "Invalid '.BLKW' operand."
            self._logger.error(msg)
            raise SyntaxError(msg)

    def process_string_with_zero(self, instruction: list[str]) -> None:
        """Allocate n+1 locations, initialize with characters and null terminator.

        syntax: label .STRINGZ "string"
            label: (Optional) A symbolic name for the memory location being defined.
            .STRINGZ: The directive keyword.
            "string": The actual string to be stored in memory. Null character added on
                its end.
        """
        arg_count = validate_directive_syntax(instruction, ".STRINGZ")

        arg = instruction[arg_count.value - 1]
        if arg.startswith('"') and arg.endswith('"'):
            string = arg[1:-1]

            for char in string:
                self.write_to_memory(ord(char))
                self.program_counter += 1

            self.write_to_memory(0)
            self.program_counter += 1
        else:
            msg = "Invalid '.STRINGZ' operand. It has to be between double quotes."
            self._logger.error(msg)
            raise SyntaxError(msg)

    def to_bytes(self) -> bytes:
        memory_deepcopy = deepcopy(self.memory)
        memory_deepcopy[self.program_counter] = self.origin
        if self.big_endian:
            memory_deepcopy.byteswap()
        output = memory_deepcopy[
            self.program_counter : self.program_counter + 1
        ].tobytes()
        output += memory_deepcopy[self.origin : self.program_counter].tobytes()
        return output
