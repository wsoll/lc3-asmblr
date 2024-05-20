import os

from assembler import Assembler, Result


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
    memory[pc] = orig
    if swap:
        memory.byteswap()
    output = memory[pc : pc + 1].tobytes()
    output += memory[orig:pc].tobytes()
    return output


if __name__ == "__main__":
    asm_code = load_file()
    assembler = Assembler()

    for line in asm_code.splitlines():
        words = assembler.prepare_keywords(line)
        if not words:
            continue

        result = assembler.step(words)
        if result == Result.FOUND:
            continue
        elif result == Result.BREAK:
            break
        result = assembler.process_instruction(words)
        if result == Result.FOUND:
            continue
        elif result == Result.NOT_FOUND:
            assembler.process_label(words)
    assembler.link_labels_def_to_labels_usage()
    output = produce_output(
        assembler.swap, assembler.memory, assembler.program_counter, assembler.origin
    )
    save_to_file(output)
