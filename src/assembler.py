from array import array

from encoding import Encodings
from logger import Logger


class Assembler(Encodings, Logger):
    def __init__(self, verbose=False):
        super().__init__(verbose)
        self.origin = 0
        self.swap = True
        self.line_counter = -1

        self.program_counter = 0
        self.memory = array("H", [0] * (1 << 16))
        self.labels_usage_address = dict()
        self.labels_def_address = dict()
        self.registers = dict(("R%1i" % r, r) for r in range(8))

        self.__directives_mapping = {}

    def read(self, line: str):
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

    def to_bytes(self) -> bytes:
        self.memory[self.program_counter] = self.origin
        if self.swap:
            self.memory.byteswap()
        output = self.memory[self.program_counter : self.program_counter + 1].tobytes()
        output += self.memory[self.origin : self.program_counter].tobytes()
        return output
