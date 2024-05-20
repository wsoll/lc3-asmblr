from asmblr import link_labels_def_to_labels_usage
from gbl_const import Result
from run import produce_output
from assembler import Assembler


class TestPseudoOps:

    def test_orig(self):
        assembler = Assembler()
        words = ".ORIG x3000".split()
        result = assembler.step(words)
        assert result is Result.FOUND
        output = produce_output(
            assembler.swap, assembler.memory, assembler.pc, assembler.orig
        )
        assert output == b"\x30\x00"

    def test_fill_1(self):
        assembler = Assembler()
        words = ".FILL x5".split()
        result = assembler.step(words)
        assert result == Result.FOUND
        assert assembler.pc == 0x0001
        output = produce_output(
            assembler.swap, assembler.memory, assembler.pc, assembler.orig
        )
        assert output == b"\x00\x00\x00\x05"

    def test_fill_2_label(self):
        assembler = Assembler()
        words = "N .FILL #5".split()
        result = assembler.step(words)
        assert result == Result.FOUND
        assert assembler.pc == 0x0001
        assert assembler.labels_def_address["N"] == 0x0
        output = produce_output(
            assembler.swap, assembler.memory, assembler.pc, assembler.orig
        )
        assert output.hex() == "00000005"

    def test_fill_3_label_usage(self):
        assembler = Assembler()
        words_1 = "LD R1, N".split()
        words_2 = "AND R0, R0, #0".split()
        words_3 = "ADD R0, R0, R1".split()
        words_4 = "N .FILL x5".split()

        result = assembler.process_instr(words_1)
        assert result == Result.FOUND
        label_usage_address = assembler.labels_usage_address["N"][0][0]
        assert label_usage_address == 0x0000

        result = assembler.process_instr(words_2)
        assert result == Result.FOUND

        result = assembler.process_instr(words_3)
        assert result == Result.FOUND

        result = assembler.step(words_4)
        assert result == Result.FOUND
        label_def = assembler.memory[assembler.labels_def_address["N"]]
        assert label_def == 0x5

        link_labels_def_to_labels_usage(
            assembler.labels_usage_address,
            assembler.labels_def_address,
            assembler.memory,
        )
        output = produce_output(
            assembler.swap, assembler.memory, assembler.pc, assembler.orig
        )
        assert output.hex()[4:8] == "2202"

    def test_blkw_1(self):
        assembler = Assembler()
        words = ".BLKW #2".split()
        result = assembler.step(words)
        assert result == Result.FOUND

        output = produce_output(
            assembler.swap, assembler.memory, assembler.pc, assembler.orig
        )
        assert output.hex()[4:] == "00000000"

    def test_blkw_2_label(self):
        pass

    def test_stringz_1(self):
        assembler = Assembler()
        words = '.STRINGZ "Sunday"'.split()
        result = assembler.step(words)
        assert result == Result.FOUND
        output = produce_output(
            assembler.swap, assembler.memory, assembler.pc, assembler.orig
        )
        assert output.hex()[4:] == "00530075006e0064006100790000"

    def test_stringz_2_label(self):
        assembler = Assembler()
        words = 'N .STRINGZ "Sunday"'.split()
        result = assembler.step(words)
        assert result == Result.FOUND
        assert assembler.labels_def_address["N"] == 0x0000
        output = produce_output(
            assembler.swap, assembler.memory, assembler.pc, assembler.orig
        )
        assert output.hex()[4:] == "00530075006e0064006100790000"

    def test_stringz_3_label_usage(self):
        assembler = Assembler()
        words_1 = "LEA R3, N".split()
        words_2 = "HALT".split()
        words_3 = 'N .STRINGZ "Sunday"'.split()

        result = assembler.process_instr(words_1)
        assert result == Result.FOUND
        label_usage_address = assembler.labels_usage_address["N"][0][0]
        assert label_usage_address == 0x0000

        result = assembler.process_instr(words_2)
        assert result == Result.FOUND

        result = assembler.step(words_3)
        assert result == Result.FOUND

        link_labels_def_to_labels_usage(
            assembler.labels_usage_address,
            assembler.labels_def_address,
            assembler.memory,
        )

        output = produce_output(
            assembler.swap, assembler.memory, assembler.pc, assembler.orig
        )
        assert output.hex()[4:8] == "e601"

    def test_end(self):
        assembler = Assembler()
        words_1 = ".END"
        result = assembler.step(words_1)
        assert result == Result.BREAK
