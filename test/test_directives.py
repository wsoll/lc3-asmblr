import pytest

from assembler import Assembler


class TestOrigin:
    @pytest.mark.parametrize("value", ["x3001"])
    def test_origin_with_proper_values(self, value):
        assembler = Assembler()
        words = f".ORIG {value}"
        assembler.read(words)

        assert assembler.to_bytes().hex() == b"\x30\x01".hex()

    def test_origin_not_before_main_program_raises(self):
        assembler = Assembler()
        assembler.line_counter += 1
        line_2 = ".ORIG x3000"
        with pytest.raises(SyntaxError):
            assembler.read(line_2)

    def test_origin_not_first_argument_raises(self):
        assembler = Assembler()
        line = "x3000 .ORIG"
        with pytest.raises(SyntaxError):
            assembler.read(line)

    @pytest.mark.parametrize("value", ["abcd", "#1234", "1234", "b01011"])
    def test_origin_inappropriate_value_raises(self, value):
        assembler = Assembler()
        words = f".ORIG {value}"
        with pytest.raises(ValueError):
            assembler.read(words)

    @pytest.mark.parametrize("value", ["", "x3000 x5000"])
    def test_origin_not_one_argument_raises(self, value):
        assembler = Assembler()
        words = f".ORIG {value}"
        with pytest.raises(ValueError):
            assembler.read(words)


class TestEnd:
    @pytest.mark.parametrize("line", [".END x3000", "FOO .END"])
    def test_inappropriate_end_syntax_raises(self, line):
        assembler = Assembler()

        with pytest.raises(SyntaxError):
            assembler.read(line)

    def test_instructions_after_end_raises(self):
        assembler = Assembler()
        line_1 = ".END"
        line_2 = "SOME INSTRUCTION"
        assembler.read(line_1)

        with pytest.raises(IndexError):
            assembler.read(line_2)
