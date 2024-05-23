from array import array

from encoding import Encodings
from logger import Logger


class Assembler(Encodings, Logger):
    def __init__(self, verbose=False):
        super().__init__(verbose)
        self.origin = 0
        self.swap = True
        self.line_counter = -1
        self.end_flag = False

        self.program_counter = 0
        self.memory = array("H", [0] * (1 << 16))
        self.labels_usage_address = dict()
        self.labels_def_address = dict()
        self.registers = dict(("R%1i" % r, r) for r in range(8))

        self.__directives_mapping = {
            ".ORIG": self.process_origin,
            ".END": self.process_end,
        }

    def read(self, line: str):
        if self.end_flag:
            raise IndexError("Main program is finished after '.END' directive.")
        self.line_counter += 1

        line_keywords = self.prepare_keywords(line)

        if not line_keywords:
            self._logger.debug(f"Line[{self.line_counter}]: empty.")
            return True

        for key, method in self.__directives_mapping.items():
            if key in line_keywords:
                method(line_keywords)
                break

    def prepare_keywords(self, line: str) -> list[str]:
        line_without_comment = line.split(";")[0]
        line_without_tabs = line_without_comment.replace("\t", "")
        self._logger.debug(line_without_tabs)

        return line_without_tabs.split()

    def cast_value_argument(
        self, arg: str, allow_decimal: bool = True, allow_binary: bool = True
    ) -> int:
        if arg.startswith("x"):
            base = 16
        elif allow_decimal and arg.startswith("#"):
            base = 10
        elif allow_binary and arg.startswith("b"):
            base = 2
        else:
            raise ValueError(
                "Every value argument has to be prefixed with 'x' for hexadecimal, '#' "
                "for decimal and 'b' for binary values."
            )

        try:
            value = int(arg[1:], base)
            self._logger.debug(f"'{arg}' casted to: {value}")
            return value
        except ValueError as e:
            raise ValueError(f"Inappropriate value: {arg} for base {base}.") from e

    def process_origin(self, line: list[str]) -> None:
        if self.line_counter != 0:
            raise SyntaxError(".ORIG has to be placed before a main program.")

        if line[0] != ".ORIG":
            raise SyntaxError("Directive '.ORIG' has to be first argument in the line.")

        if len(line) != 2:
            raise ValueError("Line with '.ORIG' has only one argument.")

        value = self.cast_value_argument(
            arg=line[1], allow_decimal=False, allow_binary=False
        )
        self.origin = self.program_counter = value

    def process_end(self, line: list[str]):
        if len(line) != 1:
            raise SyntaxError("Directive '.END' does not accept arguments.")
        self.end_flag = True

    def to_bytes(self) -> bytes:
        self.memory[self.program_counter] = self.origin
        if self.swap:
            self.memory.byteswap()
        output = self.memory[self.program_counter : self.program_counter + 1].tobytes()
        output += self.memory[self.origin : self.program_counter].tobytes()
        return output
