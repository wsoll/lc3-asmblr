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
            ("LDR R2, R1, #5", b"\x64\x45"),
            ("NOT R2, R1", b"\x94\x7F"),
            ("STR R2, R1, #5", b"\x74\x45"),
        ],
    )
    def test_binary_encoding(self, instruction, binary_encoding):
        assembler = Assembler()
        assembler.read_assembly(instruction)
        assert assembler.to_bytes().hex()[4:] == binary_encoding.hex()

    @pytest.mark.parametrize(
        "instruction",
        [
            "ADD #14, R1, R2",
            "AND R0, #14, R2",
            "AND R0, #14, R2",
            "JMP #5",
            "AND R0, R1, 155",
            'ADD R0, R3, "Hello, world!"',
            "NOT #14, R3",
            "NOT R1, x19",
            "STR R2, R1, R4",
            "STR R2, x4, R4",
            "STR x4, R2, R4",
            "LDR R2, R1, R4",
            "LDR R2, x4, R4",
            "LDR x4, R2, R4",
        ],
    )
    def test_invalid_operands_type_raises(self, instruction):
        assembler = Assembler()
        with pytest.raises(TypeError):
            assembler.read_assembly(instruction)

    @pytest.mark.parametrize(
        "instruction",
        [
            "ADD",
            "AND R1",
            "ADD R0, R1",
            "ADD R0, R1, R2, R3",
            "RET R0",
            "JMP R0, R1",
            "JMP",
            "NOT R1, R2, R2",
            "NOT",
            "STR R1, R2",
            "STR R1",
            "STR R1, R2, #4, R4",
            "STR",
        ],
    )
    def test_invalid_number_of_operands_raises(self, instruction):
        assembler = Assembler()
        with pytest.raises(IndexError):
            assembler.read_assembly(instruction)
