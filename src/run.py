import os

from assembler import Assembler


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


def main(assembly):
    assembler = Assembler()

    for line in assembly.splitlines():
        result = assembler.step(line)
        if not result:
            break

    assembler.link_labels_def_to_labels_usage()
    return produce_output(
        assembler.swap, assembler.memory, assembler.program_counter, assembler.origin
    )


if __name__ == "__main__":
    assembly = load_file()
    result = main(assembly)
    save_to_file(result)
