import os

from asmblr import *
from state import State
from gbl_const import Result

def load_file():
    fn = "none"
    while(fn and not os.path.exists(fn)):
        print('\n'.join(fn for fn in os.listdir(os.curdir)
                            if fn.endswith('.asm')))
        fn = input("Give name of .asm file: ")
    with open(fn) as codefile:
        asm_code = codefile.read()
    return asm_code


def save_to_file(output):
    #ToDo: ask for output filename
    with open('out.obj', 'wb') as f:
        f.write(output)

def produce_output(swap, memory, pc, orig):
    output = ""
    memory[pc] = orig
    if swap:
        memory.byteswap()
    output = memory[pc:pc+1].tobytes()
    output += memory[orig:pc].tobytes()
    return output


if __name__ == '__main__':
    asm_code = load_file()
    state = State()
    state.verbose = input('Verbose Y/n? ').lower() != 'n'

    for line in asm_code.splitlines():
        orig_line, line = line, line.split(";")[0]
        if state.verbose:
           print(line.replace('\t', ''))
        words = line.split()
        if not words:
            continue
        result = process_pseudo_ops(words, state)
        if result == Result.FOUND:
            continue
        elif result == Result.BREAK:
            break
        result = process_instr(words, state)
        if result == Result.FOUND:
            continue
        elif result == Result.NOT_FOUND:
            process_label(words, state)
    link_labels_def_to_labels_usage(state.labels_usage_address,
                             state.labels_def_address, state.memory)
    output = produce_output(state.swap, state.memory, state.pc, state.orig)
    save_to_file(output)


#    for m in range(state.orig, state.pc):
#        print('x{0:04X}: {1:016b}'.format(m, state.memory[m]))
