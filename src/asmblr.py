from asmblr_tools import (
    write_to_memory,
    valid_label,
    set_instr_args,
)
from gbl_const import (
    instrs_keys,
    instrs_bin,
    Result,
    flags,
)


def process_stringz_pseudo_op(words, state):
    line = " ".join(words)
    tmp = line.split('"')
    string = tmp[1]

    for char in string:
        ascii_code = ord(char)
        write_to_memory(ascii_code, state.memory, state.pc, state.verbose, "\n")
        state.pc += 1
    write_to_memory(0, state.memory, state.pc, state.verbose)
    state.pc += 1


# TODO: Handle exckceptions
def process_br_instr(words, state):
    fl = 0
    if all(c in flags for c in words[0][2:].lower()):
        fl = 0
        if words[0] == "BR":
            words[0] = "BRnzp"
        for f in words[0][2:].lower():
            fl |= flags[f]
    return fl


def process_instr(words, state):
    instr_bin = 0
    if words[0].startswith("BR"):
        flags = process_br_instr(words, state)
        instr_bin |= flags
        words[0] = "BR"
    if words[0] in instrs_keys:
        found_instr = words[0]
        instr_bin |= instrs_bin[found_instr]
        args_bin = set_instr_args(
            words, state.regs, state.labels_usage_address, state.pc, found_instr
        )
        instr_bin |= args_bin
        write_to_memory(instr_bin, state.memory, state.pc, state.verbose, "\n")
        state.pc += 1
        return Result.FOUND
    else:
        return Result.NOT_FOUND


def process_label(words, state):
    label = words[0]
    # instr = words[1]
    if valid_label(label):
        state.labels_def_address[label] = state.pc
        # set_label_usage_address(label, state.labels_usage_address,
        #                   state.pc, imm_mask[instr], imm_bit_range[instr])
        words.pop(0)
        return process_instr(words, state)
    else:
        raise ValueError(f"Invalid label: {label}")


def link_labels_def_to_labels_usage(labels_usage_address, labels_def_address, memory):
    for label, usages in labels_usage_address.items():
        for ref, mask, bit in usages:
            current = labels_def_address[label] - ref - 1
            memory[ref] |= mask & current
