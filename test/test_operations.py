import pytest

from assembler import Assembler


@pytest.mark.skip
class TestOperations:

    @pytest.mark.parametrize(
        "instruction, binary_encoding",
        [
            ("ADD R0, R1, R2", 0x1042),
            ("ADD R0, R1, x5", 0x1065),
            ("AND R3, R0, R2", 0x5602),
            ("AND R3, R0, x14", 0x562E),
            ("JMP R2", 0xC400),
            ("JSRR R2", 0x2080),
            ("LDR R2, R1, #5", 0x6445),
            ("NOT R2, R1", 0x947F),
            ("STR R2, R1, #5", 0x7445),
        ],
    )
    def test_binary_encoding(self, instruction, binary_encoding):
        assembler = Assembler()
        assembler.read_assembly(instruction)
        assert assembler.to_bytes().hex()[4:] == binary_encoding
