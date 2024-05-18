from asmblr import process_pseudo_ops, process_instr, link_labels_def_to_labels_usage
from gbl_const import Result
from run import produce_output
from state import State


class TestPseudoOps:

    def test_orig(self):
        state = State()
        words = ".ORIG x3000".split()
        result = process_pseudo_ops(words, state)
        assert result is Result.FOUND
        output = produce_output(state.swap, state.memory, state.pc, state.orig)
        assert output == b"\x30\x00"

    def test_fill_1(self):
        state = State()
        words = ".FILL x5".split()
        result = process_pseudo_ops(words, state)
        assert result == Result.FOUND
        assert state.pc == 0x0001
        output = produce_output(state.swap, state.memory, state.pc, state.orig)
        assert output == b"\x00\x00\x00\x05"

    def test_fill_2_label(self):
        state = State()
        words = "N .FILL #5".split()
        result = process_pseudo_ops(words, state)
        assert result == Result.FOUND
        assert state.pc == 0x0001
        assert state.labels_def_address["N"] == 0x0
        output = produce_output(state.swap, state.memory, state.pc, state.orig)
        assert output.hex() == "00000005"

    def test_fill_3_label_usage(self):
        state = State()
        words_1 = "LD R1, N".split()
        words_2 = "AND R0, R0, #0".split()
        words_3 = "ADD R0, R0, R1".split()
        words_4 = "N .FILL x5".split()

        result = process_instr(words_1, state)
        assert result == Result.FOUND
        label_usage_address = state.labels_usage_address["N"][0][0]
        assert label_usage_address == 0x0000

        result = process_instr(words_2, state)
        assert result == Result.FOUND

        result = process_instr(words_3, state)
        assert result == Result.FOUND

        result = process_pseudo_ops(words_4, state)
        assert result == Result.FOUND
        label_def = state.memory[state.labels_def_address["N"]]
        assert label_def == 0x5

        link_labels_def_to_labels_usage(
            state.labels_usage_address,
            state.labels_def_address,
            state.memory,
        )
        output = produce_output(state.swap, state.memory, state.pc, state.orig)
        assert output.hex()[4:8] == "2202"

    def test_blkw_1(self):
        state = State()
        words = ".BLKW #2".split()
        result = process_pseudo_ops(words, state)
        assert result == Result.FOUND

        output = produce_output(state.swap, state.memory, state.pc, state.orig)
        assert output.hex()[4:] == "00000000"

    def test_blkw_2_label(self):
        pass

    def test_stringz_1(self):
        state = State()
        words = '.STRINGZ "Sunday"'.split()
        result = process_pseudo_ops(words, state)
        assert result == Result.FOUND
        output = produce_output(state.swap, state.memory, state.pc, state.orig)
        assert output.hex()[4:] == "00530075006e0064006100790000"

    def test_stringz_2_label(self):
        state = State()
        words = 'N .STRINGZ "Sunday"'.split()
        result = process_pseudo_ops(words, state)
        assert result == Result.FOUND
        assert state.labels_def_address["N"] == 0x0000
        output = produce_output(state.swap, state.memory, state.pc, state.orig)
        assert output.hex()[4:] == "00530075006e0064006100790000"

    def test_stringz_3_label_usage(self):
        state = State()
        words_1 = "LEA R3, N".split()
        words_2 = "HALT".split()
        words_3 = 'N .STRINGZ "Sunday"'.split()

        result = process_instr(words_1, state)
        assert result == Result.FOUND
        label_usage_address = state.labels_usage_address["N"][0][0]
        assert label_usage_address == 0x0000

        result = process_instr(words_2, state)
        assert result == Result.FOUND

        result = process_pseudo_ops(words_3, state)
        assert result == Result.FOUND

        link_labels_def_to_labels_usage(
            state.labels_usage_address,
            state.labels_def_address,
            state.memory,
        )

        output = produce_output(state.swap, state.memory, state.pc, state.orig)
        assert output.hex()[4:8] == "e601"

    def test_end(self):
        state = State()
        words_1 = ".END"
        result = process_pseudo_ops(words_1, state)
        assert result == Result.BREAK
