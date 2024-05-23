from assembler import Assembler


def load_assembly(filepath):
    with open(filepath, "r") as file:
        for line in file:
            yield line


def main(filepath):
    assembler = Assembler()

    for line in load_assembly("..."):
        assembler.read(line)

    assembler.to_bytes()
    # ToDo: Save to file


if __name__ == "__main__":
    # ToDo: CLI for: filepath, verbose
    main("...")
