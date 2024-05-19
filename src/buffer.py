from array import array

from gbl_const import reg_pos, imm_mask, imm_bit_range


class Buffer:

    def __init__(self):
        self.pc = 0
        self.memory = array("H", [0] * (1 << 16))
        self.labels_usage_address = dict()

    @staticmethod
    def valid_label(word):
        return all(c.isalpha() or c.isdigit() or c == "_" for c in word)

    @staticmethod
    def get_mem_str(loc, memory):
        return "x{0:04X}: {1:016b}".format(loc, memory[loc])

    def write_to_memory(self, value):
        if value < 0:
            value = (1 << 16) + value
        self.memory[self.pc] = value

    def set_label_usage_address(self, word, imm_mask=0xFFFF, imm_bit_range=16):
        if word in self.labels_usage_address:
            self.labels_usage_address[word].append([self.pc, imm_mask, imm_bit_range])
        else:
            self.labels_usage_address[word] = [[self.pc, imm_mask, imm_bit_range]]

    def set_imm_mode(self, instruction):
        instruction |= 1 << 5
        return instruction

    def get_immediate_value(self, word, mask=0xFFFF):
        if word.startswith("x"):
            return int("0" + word, 0) & mask
        elif word.startswith("#"):
            return int(word.strip("#"), 0) & mask

    def set_instr_args(self, words, regs, found_instr):
        r = rc = 0
        rc += found_instr == "JSRR"
        for raw_arg in words[1:]:
            arg = raw_arg.strip(",")
            if arg in regs:
                tmp = regs[arg] << reg_pos[rc]
                r |= tmp
                rc += 1
            elif arg.startswith("x") or arg.startswith("#"):
                imm_value = self.get_immediate_value(arg, imm_mask[found_instr])
                r |= imm_value
                if found_instr == "AND" or found_instr == "ADD":
                    r = self.set_imm_mode(r)
            elif self.valid_label(arg):
                self.set_label_usage_address(
                    arg, imm_mask[found_instr], imm_bit_range[found_instr]
                )
            else:
                raise ValueError("Invalid label: %r" % (arg))
        return r
