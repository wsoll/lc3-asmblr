#in this file passing pc by object is not needed (read only)

from gbl_const import reg_pos, imm_mask, imm_bit_range

def valid_label(word):
    return all(c.isalpha() or c.isdigit() or c == '_' for c in word)

def get_mem_str(loc, memory):
    return 'x{0:04X}: {1:016b}'.format(loc, memory[loc])

def write_to_memory(value, memory, pc, verbose, end = ''):
    if value < 0: value = (1<<16) + value
    memory[pc] = value
    #if verbose:
    #    print(get_mem_str(pc, memory), end=end)

def set_label_usage_address(word, labels_usage_address,
                       pc, imm_mask = 0xFFFF, imm_bit_range = 16):
    if word in labels_usage_address:
        labels_usage_address[word].append([pc, imm_mask, imm_bit_range])
    else:
        labels_usage_address[word] = [[pc, imm_mask, imm_bit_range]]


def set_imm_mode(instruction):
    instruction |= 1 << 5
    return instruction


def get_immediate_value(word, mask=0xFFFF):
    if word.startswith('x'):
        return int('0' + word, 0) & mask
    elif word.startswith('#'):
        return int(word.strip('#'), 0) & mask


def set_instr_args(words, regs, labels_usage_address, pc, found_instr):
    r = rc = 0
    rc += found_instr == 'JSRR'
    for raw_arg in words[1:]:
        arg = raw_arg.strip(',')
        if arg in regs:
            tmp = regs[arg] << reg_pos[rc]
            r |= tmp
            rc += 1
        elif arg.startswith('x') or arg.startswith('#'):
            imm_value = get_immediate_value(arg, imm_mask[found_instr])
            r |= imm_value
            if found_instr == 'AND' or found_instr == 'ADD':
                r = set_imm_mode(r)
        elif valid_label(arg):
            set_label_usage_address(arg, labels_usage_address, pc,
                                    imm_mask[found_instr],
                                    imm_bit_range[found_instr])
        else:
            raise ValueError('Invalid label: %r' % (arg))
    return r



