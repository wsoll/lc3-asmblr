import pytest

from assembler import Assembler


class TestDirective:
    @pytest.mark.parametrize(
        "word",
        [
            "x3001 .ORIG",
            "#50 .FILL",
            ".FILL #50 FOO",
            "#50 .BLKW",
            ".BLKW #50 FOO",
            ".END x3000",
            "FOO .END",
            '"Hello, World!" .STRINGZ',
        ],
    )
    def test_wrong_order_raises(self, word):
        assembler = Assembler()
        with pytest.raises(SyntaxError):
            assembler.read_assembly(word)

    @pytest.mark.parametrize("directive_key", [".FILL", ".BLKW"])
    def test_invalid_label_raises(self, directive_key):
        assembler = Assembler()
        with pytest.raises(TypeError):
            word = f"#50 {directive_key} FOO"
            assembler.read_assembly(word)


class TestOrigin:
    @pytest.mark.parametrize("value", ["x3001"])
    def test_origin_with_proper_values(self, value):
        assembler = Assembler()
        words = f".ORIG {value}"
        assembler.read_assembly(words)

        assert assembler.to_bytes().hex() == b"\x30\x01".hex()

    def test_origin_not_before_main_program_raises(self):
        assembler = Assembler()
        assembler.line_counter += 1
        line_2 = ".ORIG x3000"
        with pytest.raises(SyntaxError):
            assembler.read_assembly(line_2)

    @pytest.mark.parametrize("value", ["abcd", "#1234", "1234", "b01011"])
    def test_origin_inappropriate_value_raises(self, value):
        assembler = Assembler()
        words = f".ORIG {value}"
        with pytest.raises(ValueError):
            assembler.read_assembly(words)

    @pytest.mark.parametrize("value", ["", "x3000 x5000"])
    def test_origin_not_one_argument_raises(self, value):
        assembler = Assembler()
        words = f".ORIG {value}"
        with pytest.raises(ValueError):
            assembler.read_assembly(words)


class TestFill:
    @pytest.mark.parametrize("value", ["x0030", "b110000", "#48"])
    def test_fill_with_value(self, value):
        assembler = Assembler()
        line = f".FILL {value}"
        assembler.read_assembly(line)
        assert assembler.to_bytes().hex()[4:] == b"\x00\x30".hex()


class TestBlockOfWords:
    @pytest.mark.parametrize("n", ["#1", "#3", "#15"])
    def test_blkw_with_value(self, n):
        assembler = Assembler()
        line = f".BLKW {n}"
        empty_words_count = int(n[1:]) * 2  # every word has 2 bytes
        origin_and_empty_words = bytearray(empty_words_count)

        assembler.read_assembly(line)

        assert assembler.to_bytes().hex()[4:] == origin_and_empty_words.hex()


class TestStringWithZero:
    def test_stringz_with_string(self):
        assembler = Assembler()
        line = '.STRINGZ "Hello, World!"'
        assembler.read_assembly(line)

        # Encode the content in UTF-16 big endian without BOM + default ORIG
        expected = "Hello, World!".encode("utf-16-be") + b"\x00\x00"
        assert assembler.to_bytes().hex()[4:] == expected.hex()

    @pytest.mark.skip(reason="Improve regex")
    @pytest.mark.parametrize("arg", ["#4000", 'Hello!"', '"Hello!', '"Hello!""'])
    def test_stringz_invalid_argument_raises(self, arg):
        assembler = Assembler()
        line_1 = f".STRINGZ {arg}"
        with pytest.raises(SyntaxError):
            assembler.read_assembly(line_1)


class TestEnd:
    def test_instructions_after_end_raises(self):
        assembler = Assembler()
        line_1 = ".END"
        line_2 = "SOME INSTRUCTION"
        assembler.read_assembly(line_1)

        with pytest.raises(IndexError):
            assembler.read_assembly(line_2)
