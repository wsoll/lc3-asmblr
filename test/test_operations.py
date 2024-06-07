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
            ("JMP R2", b"\xC0\x80"),
            ("RET", b"\xC1\xC0"),
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

    @pytest.mark.parametrize(
        "instruction, error_type",
        [
            ("ADD #14, R1, R2", TypeError),
            ("AND R0, #14, R2", TypeError),
            ("AND R0, #14, R2", TypeError),
            ("JMP #5", TypeError),
            ("AND R0, R1, 155", TypeError),
            ('ADD R0, R3, "Hello, world!"', TypeError),
            ("NOT #14, R3", TypeError),
            ("NOT R1, x19", TypeError),
        ],
    )
    def test_invalid_operands_type_raises(self, instruction, error_type):
        assembler = Assembler()
        with pytest.raises(TypeError):
            assembler.read_assembly(instruction)

    @pytest.mark.parametrize(
        "instruction, error_type",
        [
            ("ADD", IndexError),
            ("AND R1", IndexError),
            ("ADD R0, R1", IndexError),
            ("ADD R0, R1, R2, R3", IndexError),
            ("RET R0", IndexError),
            ("JMP R0, R1", IndexError),
            ("JMP", IndexError),
            ("NOT R1, R2, R2", IndexError),
            ("NOT", IndexError),
        ],
    )
    def test_invalid_number_of_operands_raises(self, instruction, error_type):
        assembler = Assembler()
        with pytest.raises(IndexError):
            assembler.read_assembly(instruction)
