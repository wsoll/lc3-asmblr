from array import array
from enum import Enum

from encoding import Encodings


class Assembler(Encodings):
    def __init__(self):
        super().__init__()
        self.origin = 0
        self.verbose = True
        self.swap = True

        self.program_counter = 0
        self.memory = array("H", [0] * (1 << 16))
        self.labels_usage_address = dict()
        self.labels_def_address = dict()
        self.registers = dict(("R%1i" % r, r) for r in range(8))

        self.__directives_mapping = {
            ".ORIG": self.process_origin,
            ".FILL": self.process_fill,
            ".BLKW": self.process_blkw,
            ".STRINGZ": self.process_stringz,
            ".END": lambda x: Result.BREAK,
        }

    def step(self, line_keywords):
        for key, method in self.__directives_mapping.items():
            if key in line_keywords:
                return method(line_keywords)
        return Result.NOT_FOUND

    def prepare_keywords(self, line):
        line = line.split(";")[0]
        if self.verbose:
            print(line.replace("\t", ""))
        return line.split()

    def process_origin(self, line):
        self.origin = self.program_counter = int(
            "0" + line[1] if line[1].startswith("x") else line[1], 0
        )
        return Result.FOUND

    def process_br_instr(self, words):
        fl = 0
        if all(c in self.CONDITION_FLAGS for c in words[0][2:].lower()):
            fl = 0
            if words[0] == "BR":
                words[0] = "BRnzp"
            for f in words[0][2:].lower():
                fl |= self.CONDITION_FLAGS[f]
        return fl

    def process_instruction(self, words):
        instr_bin = 0
        if words[0].startswith("BR"):
            flags = self.process_br_instr(words)
            instr_bin |= flags
            words[0] = "BR"
        if words[0] in self.ALL_INSTRUCTIONS.keys():
            instruction = words[0]
            instr_bin |= self.ALL_INSTRUCTIONS[instruction]
            args_bin = self.set_instr_args(words, instruction)
            instr_bin |= args_bin
            self.write_to_memory(instr_bin)
            self.program_counter += 1
            return Result.FOUND
        else:
            return Result.NOT_FOUND

    def process_label(self, words):
        label = words[0]
        # instr = words[1]
        if self.valid_label(label):
            self.labels_def_address[label] = self.program_counter
            # set_label_usage_address(label, state.labels_usage_address,
            #                   state.pc, imm_mask[instr], imm_bit_range[instr])
            words.pop(0)
            return self.process_instruction(words)
        else:
            raise ValueError(f"Invalid label: {label}")

    def link_labels_def_to_labels_usage(self):
        for label, usages in self.labels_usage_address.items():
            for ref, mask, bit in usages:
                current = self.labels_def_address[label] - ref - 1
                self.memory[ref] |= mask & current

    def process_fill(self, line):
        word = line[line.index(".FILL") + 1]
        # TODO: handle exceptions
        if word.startswith("x") or word.startswith("#"):
            imm_value = self.get_immediate_value(word)
            self.write_to_memory(imm_value)
        # TODO: To check if needed (also for .STRINGZ, .BLKW)
        elif self.valid_label(word):
            self.set_label_usage_address(
                word, self.labels_usage_address, self.program_counter
            )
        else:
            raise ValueError(f"Invalid label: {word}")
        if line[0] != ".FILL":
            self.labels_def_address[line[0]] = self.program_counter
        self.program_counter += 1
        return Result.FOUND

    def process_blkw(self, line):
        if line[0] != ".BLKW":
            self.labels_def_address[line[0]] = self.program_counter
        word = line[line.index(".BLKW") + 1]
        if word.startswith("x") or word.startswith("#"):
            imm_value = self.get_immediate_value(word)
            self.program_counter += imm_value
        else:
            raise ValueError(f"Invalid label: {word}")
        return Result.FOUND

    def process_stringz(self, line):
        if line[0] != ".STRINGZ":
            self.labels_def_address[line[0]] = self.program_counter
        # TODO: handle exceptions (first and last ")
        self.labels_def_address[line[0]] = self.program_counter

        line = " ".join(line)
        tmp = line.split('"')
        string = tmp[1]

        for char in string:
            ascii_code = ord(char)
            self.write_to_memory(ascii_code)
            self.program_counter += 1
        self.write_to_memory(0)
        self.program_counter += 1
        return Result.FOUND

    @staticmethod
    def valid_label(word):
        return all(c.isalpha() or c.isdigit() or c == "_" for c in word)

    @staticmethod
    def get_mem_str(loc, memory):
        return "x{0:04X}: {1:016b}".format(loc, memory[loc])

    def write_to_memory(self, value):
        if value < 0:
            value = (1 << 16) + value
        self.memory[self.program_counter] = value

    def set_label_usage_address(self, word, imm_mask=0xFFFF, imm_bit_range=16):
        if word in self.labels_usage_address:
            self.labels_usage_address[word].append(
                [self.program_counter, imm_mask, imm_bit_range]
            )
        else:
            self.labels_usage_address[word] = [
                [self.program_counter, imm_mask, imm_bit_range]
            ]

    def set_imm_mode(self, instruction):
        instruction |= 1 << 5
        return instruction

    def get_immediate_value(self, word, mask=0xFFFF):
        if word.startswith("x"):
            return int("0" + word, 0) & mask
        elif word.startswith("#"):
            return int(word.strip("#"), 0) & mask

    def set_instr_args(self, words, found_instr):
        r = rc = 0
        rc += found_instr == "JSRR"
        for raw_arg in words[1:]:
            arg = raw_arg.strip(",")
            if arg in self.registers:
                tmp = self.registers[arg] << self.REGISTER_ROW_BIT_ORIGIN[rc]
                r |= tmp
                rc += 1
            elif arg.startswith("x") or arg.startswith("#"):
                imm_value = self.get_immediate_value(
                    arg, self.IMMEDIATE_MASK[found_instr]
                )
                r |= imm_value
                if found_instr == "AND" or found_instr == "ADD":
                    r = self.set_imm_mode(r)
            elif self.valid_label(arg):
                self.set_label_usage_address(
                    arg,
                    self.IMMEDIATE_MASK[found_instr],
                    self.IMMEDIATE_MODE_FLAG_POSITION[found_instr],
                )
            else:
                raise ValueError("Invalid label: %r" % (arg))
        return r


class Result(Enum):
    NOT_FOUND = 0
    FOUND = 1
    BREAK = 2
