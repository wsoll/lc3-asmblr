from typing import Generator

from assembler import Assembler


def load_assembly(filepath: str) -> Generator[str, None, None]:
    with open(filepath, "r") as file:
        for line in file:
            yield line


def main(filepath: str) -> None:
    assembler = Assembler()

    for line in load_assembly(filepath):
        assembler.read_assembly(line)

    assembler.to_bytes()
    # ToDo: Save to file


if __name__ == "__main__":
    # ToDo: CLI for: filepath, verbose
    main("...")
