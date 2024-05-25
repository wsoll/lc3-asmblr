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


class TestFill:
    @pytest.mark.parametrize("value", ["x0030", "b110000", "#48"])
    def test_fill_with_value(self, value):
        assembler = Assembler()
        line = f".FILL {value}"
        assembler.read(line)
        assert assembler.to_bytes().hex() == b"\x30\x00\x00\x30".hex()


class TestBlockOfWords:

    @pytest.mark.parametrize("n", ["#1", "#3", "#15"])
    def test_blkw_with_value(self, n):
        assembler = Assembler()
        line = f".BLKW {n}"
        empty_words_count = int(n[1:]) * 2  # every word has 2 bytes
        origin_and_empty_words = bytearray(2 + empty_words_count)
        origin_and_empty_words[0] = 0x30

        assembler.read(line)

        assert assembler.to_bytes().hex() == origin_and_empty_words.hex()


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
