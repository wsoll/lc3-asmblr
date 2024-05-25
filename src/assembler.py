from array import array
from copy import deepcopy

import syntax
from encoding import Encodings
from logger import Logger


class Assembler(Encodings, Logger):
    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
        self.origin = self.program_counter = 0x3000
        self.swap = True
        self.line_counter = -1
        self.end_flag = False

        self.memory = array("H", [0] * (1 << 16))
        self.labels_usage_addresses: dict[str, int] = {}
        self.labels_definition_addresses: dict[str, int] = {}
        self.registers = {("R%1i" % r, r) for r in range(8)}

        self.__directives_mapping = {
            ".ORIG": self.process_origin,
            ".FILL": self.process_fill,
            ".BLKW": self.process_block_of_words,
            ".END": self.process_end,
        }

    def read(self, line: str) -> None:
        if self.end_flag:
            raise IndexError("Main program is finished after '.END' directive.")
        self.line_counter += 1

        line_keywords = syntax.parse_assembly(line)

        if not line_keywords:
            self._logger.debug(f"Line[{self.line_counter}]: empty.")
            return

        for key, method in self.__directives_mapping.items():
            if key in line_keywords:
                method(line_keywords)
                break

    def write_to_memory(self, value: int) -> None:
        if value < 0:
            value = (1 << 16) + value
        self.memory[self.program_counter] = value

    def process_origin(self, line: list[str]) -> None:
        if self.line_counter != 0:
            raise SyntaxError(".ORIG has to be placed before a main program.")

        if line[0] != ".ORIG":
            raise SyntaxError("Directive '.ORIG' has to be first argument in the line.")

        if len(line) != 2:
            raise ValueError("Line with '.ORIG' has only one argument.")

        value = syntax.cast_value_argument(
            arg=line[1], allow_decimal=False, allow_binary=False
        )
        self.origin = self.program_counter = value

    def process_end(self, line: list[str]) -> None:
        if len(line) != 1:
            raise SyntaxError("Directive '.END' does not accept arguments.")
        self.end_flag = True

    def process_directive(
        self, line: list[str], directive_key: syntax.Directive
    ) -> int:
        try:
            words_count = syntax.validate_directive(line, directive_key)
        except (ValueError, SyntaxError) as e:
            self._logger.error(e)
            raise e

        if words_count == 3:
            raise NotImplementedError("Processing label is not yet implemented.")

        return words_count

    def process_fill(self, line: list[str]) -> None:
        """Allocate one word, initialize with word.

        syntax: label .FILL value
            label: (Optional) A symbolic name for the memory location being defined.
            .FILL: The directive keyword.
            value: A 16-bit value to store in the allocated memory location. This
                can be a literal number (in decimal, hexadecimal, or binary format)
                or a symbolic constant.
        """
        words_count = self.process_directive(line, ".FILL")

        arg = line[words_count - 1]  # ToDo-1: remove duplication if pattern
        if syntax.is_value(arg):
            value = syntax.cast_value_argument(arg)
            self.write_to_memory(value)
        elif syntax.is_valid_label(arg):
            raise NotImplementedError()
        else:
            msg = "Invalid '.FILL' argument."
            self._logger.error(msg)
            raise SyntaxError(msg)

        self.program_counter += 1

    def process_block_of_words(self, line: list[str]) -> None:
        """Allocate multiple words of storage, value unspecified.

        syntax: label .BLKW n
            label: (Optional) A symbolic name for the memory location being defined.
            .BLKW : The directive keyword.
            n: number of words to allocate.
        """

        words_count = self.process_directive(line, ".BLKW")

        arg = line[words_count - 1]  # ToDo: (ToDo-1 reference)
        if syntax.is_value(arg):
            words_to_allocate = syntax.cast_value_argument(
                arg, allow_hexadecimal=False, allow_binary=False
            )
            self.program_counter += words_to_allocate
        elif syntax.is_valid_label(arg):
            raise NotImplementedError()
        else:
            msg = "Invalid '.BLKW' argument."
            self._logger.error(msg)
            raise SyntaxError(msg)

    def to_bytes(self) -> bytes:
        memory_deepcopy = deepcopy(self.memory)
        memory_deepcopy[self.program_counter] = self.origin
        if self.swap:
            memory_deepcopy.byteswap()
        output = memory_deepcopy[
            self.program_counter : self.program_counter + 1
        ].tobytes()
        output += memory_deepcopy[self.origin : self.program_counter].tobytes()
        return output
