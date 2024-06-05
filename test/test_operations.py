import pytest

from assembler import Assembler


class TestOperations:

    @pytest.mark.parametrize(
        "instruction, binary_encoding",
        [
            ("ADD R0, R1, R2", b"\x10\x42"),
            ("ADD R0, R1, x5", b"\x10\x65"),
            ("AND R3, R0, R2", b"\x56\x02"),
            ("AND R3, R0, #14", b"\x56\x2E"),
            ("JMP R2", b"\xC4\x00"),
            # ("JSRR R2", b"\x20\x80"),
            # ("LDR R2, R1, #5", b"\x64\x45"),
            ("NOT R2, R1", b"\x94\x7F"),
            # ("STR R2, R1, #5", b"\x74\x45"),
        ],
    )
    def test_binary_encoding(self, instruction, binary_encoding):
        assembler = Assembler()
        assembler.read_assembly(instruction)
        assert assembler.to_bytes().hex()[4:] == binary_encoding.hex()
