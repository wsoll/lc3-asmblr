import pytest

from assembler import Assembler


class TestOrigin:

    @pytest.mark.parametrize("value", ["x3000", "12288"])
    def test_origin_with_proper_values(self, value):
        assembler = Assembler()
        words = f".ORIG {value}"
        assembler.read(words)

        assert assembler.to_bytes() == b"\x30\x00"

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

    @pytest.mark.parametrize("value", ["abcd"])
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
