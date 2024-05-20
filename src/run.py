import os

from asmblr import link_labels_def_to_labels_usage

from assembler import Assembler
from gbl_const import Result


def load_file():
    fn = "none"
    while fn and not os.path.exists(fn):
        print("\n".join(fn for fn in os.listdir(os.curdir) if fn.endswith(".asm")))
        fn = input("Give name of .asm file: ")
    with open(fn) as codefile:
        asm_code = codefile.read()
    return asm_code


def save_to_file(output):
    # ToDo: ask for output filename
    with open("out.obj", "wb") as f:
        f.write(output)


def produce_output(swap, memory, pc, orig):
    output = ""
    memory[pc] = orig
    if swap:
        memory.byteswap()
    output = memory[pc : pc + 1].tobytes()
    output += memory[orig:pc].tobytes()
    return output


if __name__ == "__main__":
    asm_code = load_file()
    assembler = Assembler()
    assembler.verbose = input("Verbose Y/n? ").lower() != "n"

    for line in asm_code.splitlines():
        words = assembler.prepare_keywords(line)
        if not words:
            continue

        result = assembler.step(words)
        if result == Result.FOUND:
            continue
        elif result == Result.BREAK:
            break
        result = assembler.process_instr(words)
        if result == Result.FOUND:
            continue
        elif result == Result.NOT_FOUND:
            assembler.process_label(words)
    link_labels_def_to_labels_usage(
        assembler.labels_usage_address, assembler.labels_def_address, assembler.memory
    )
    output = produce_output(assembler.swap, assembler.memory, assembler.pc, assembler.orig)
    save_to_file(output)


#    for m in range(state.orig, state.pc):
#        print('x{0:04X}: {1:016b}'.format(m, state.memory[m]))
