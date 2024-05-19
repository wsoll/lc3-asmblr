from buffer import Buffer


class Assembler(Buffer):
    def __init__(self):
        super().__init__()
        self.orig = 0
        self.verbose = True
        self.swap = True

        self.labels_def_address = dict()
        self.regs = dict(("R%1i" % r, r) for r in range(8))

        self.__pseudo_ops_mapping = {
            ".ORIG": self._process_orig,
            ".FILL": self._process_fill,
            ".BLKW": self._process_blkw,
            ".STRINGZ": self._process_stringz,
            ".END": self._process_end,
        }

    def step(self, line):
        line_keywords = self.prepare_keywords(line)
        for key, method in self.__pseudo_ops_mapping.items():
            if key in line_keywords:
                method(line_keywords)

    def prepare_keywords(self, line):
        line = line.split(";")[0]
        if self.verbose:
            print(line.replace("\t", ""))
        return line.split()

    def _process_orig(self, line):
        self.orig = self.pc = int(
            "0" + line[1] if line[1].startswith("x") else line[1], 0
        )

    def _process_fill(self, line):
        word = line[line.index(".FILL") + 1]
        # TODO: handle exceptions
        if word.startswith("x") or word.startswith("#"):
            imm_value = self.get_immediate_value(word)
            self.write_to_memory(imm_value)
        # TODO: To check if needed (also for .STRINGZ, .BLKW)
        elif self.valid_label(word):
            self.set_label_usage_address(word, self.labels_usage_address, self.pc)
        else:
            raise ValueError(f"Invalid label: {word}")
        if line[0] != ".FILL":
            self.labels_def_address[line[0]] = self.pc
        self.pc += 1

    def _process_blkw(self, line):
        if line[0] != ".BLKW":
            self.labels_def_address[line[0]] = self.pc
        word = line[line.index(".BLKW") + 1]
        if word.startswith("x") or word.startswith("#"):
            imm_value = self.get_immediate_value(word)
            self.pc += imm_value
        else:
            raise ValueError(f"Invalid label: {word}")

    def _process_stringz(self, line):
        if line[0] != ".STRINGZ":
            self.labels_def_address[line[0]] = self.pc
        # TODO: handle exceptions (first and last ")
        self.labels_def_address[line[0]] = self.pc

        line = " ".join(line)
        tmp = line.split('"')
        string = tmp[1]

        for char in string:
            ascii_code = ord(char)
            self.write_to_memory(ascii_code)
            self.pc += 1
        self.write_to_memory(0)
        self.pc += 1

    def _process_end(self, line): ...
