from asmblr import (
    process_pseudo_ops,
    process_instr,
    link_labels_def_to_labels_usage,
    process_label,
)
from gbl_const import Result
from state import State
from run import produce_output


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
        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output == b"\x00\x00\x00\x05"

    def test_fill_2_label(self):
        state = State()
        words = "N .FILL #5".split()
        result = process_pseudo_ops(words, state)
        assert result == Result.FOUND
        assert state.pc == 0x0001
        assert state.labels_def_address["N"] == 0x0
        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
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
        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:8] == "2202"

    def test_blkw_1(self):
        state = State()
        words = ".BLKW #2".split()
        result = process_pseudo_ops(words, state)
        assert result == Result.FOUND

        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:] == "00000000"

    def test_blkw_2_label(self):
        pass

    def test_stringz_1(self):
        state = State()
        words = '.STRINGZ "Sunday"'.split()
        result = process_pseudo_ops(words, state)
        assert result == Result.FOUND
        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:] == "00530075006e0064006100790000"

    def test_stringz_2_label(self):
        state = State()
        words = 'N .STRINGZ "Sunday"'.split()
        result = process_pseudo_ops(words, state)
        assert result == Result.FOUND
        assert state.labels_def_address["N"] == 0x0000
        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
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

        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:8] == "e601"

    def test_end(self):
        state = State()
        words_1 = ".END"
        result = process_pseudo_ops(words_1, state)
        assert result == Result.BREAK


class TestInstructions:
    def work_with_label(self, words_1, hex_output_result):
        state = State()
        words_2 = "HALT".split()
        words_3 = "FOO .FILL xFF".split()

        result = process_instr(words_1, state)
        assert (result, Result.FOUND)

        result = process_instr(words_2, state)
        assert (result, Result.FOUND)

        result = process_pseudo_ops(words_3, state)
        assert (result, Result.FOUND)

        link_labels_def_to_labels_usage(
            state.labels_usage_address,
            state.labels_def_address,
            state.memory,
        )

        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert (output.hex()[4:8], hex_output_result)
        assert (output.hex()[8:12], "f025")
        assert (output.hex()[12:16], "00ff")

    def test_add_1(self):
        state = State()
        words = "ADD R0, R1, R2".split()
        result = process_instr(words, state)
        assert result == Result.FOUND
        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:8] == "1042"

    def test_add_2(self):
        state = State()
        words = "ADD R0, R1, x5".split()
        result = process_instr(words, state)
        assert (result, Result.FOUND)
        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:8] == "1065"

    def test_and_1(self):
        state = State()
        words = "AND R3, R0, R2".split()
        result = process_instr(words, state)
        assert (result, Result.FOUND)
        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:8] == "5602"

    def test_and_2(self):
        state = State()
        words = "AND R3, R0, #14".split()
        result = process_instr(words, state)
        assert result == Result.FOUND
        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:8] == "562e"

    def test_br_and_ret(self):
        state = State()
        words_1 = "BRnp FOO".split()
        words_2 = "HALT".split()
        words_3 = "FOO AND R3, R0, #14".split()
        words_4 = "RET".split()

        result = process_instr(words_1, state)
        assert result == Result.FOUND

        result = process_instr(words_2, state)
        assert result == Result.FOUND

        result = process_label(words_3, state)
        assert result == Result.FOUND

        result = process_instr(words_4, state)
        assert result == Result.FOUND

        link_labels_def_to_labels_usage(
            state.labels_usage_address,
            state.labels_def_address,
            state.memory,
        )

        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:8] == "0a01"
        assert output.hex()[8:12] == "f025"
        assert output.hex()[12:16] == "562e"
        assert output.hex()[16:20] == "c1c0"

    def test_jmp_1(self):
        state = State()
        words_1 = "JMP R2".split()

        result = process_instr(words_1, state)
        assert result == Result.FOUND

        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:8] == "c400"

    def test_jsr_and_ldr(self):
        state = State()
        words_1 = "JSR FOO".split()
        words_2 = "HALT".split()
        words_3 = "HALT".split()
        words_4 = "FOO LDR R4, R2, x5".split()

        result = process_instr(words_1, state)
        assert result == Result.FOUND

        result = process_instr(words_2, state)
        assert result == Result.FOUND

        result = process_instr(words_3, state)
        assert result == Result.FOUND

        result = process_label(words_4, state)
        assert result == Result.FOUND

        link_labels_def_to_labels_usage(
            state.labels_usage_address,
            state.labels_def_address,
            state.memory,
        )
        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )

        assert output.hex()[4:8] == "4802"
        assert output.hex()[8:12] == output.hex()[12:16] == "f025"
        assert output.hex()[16:20] == "6885"

    def test_jsrr(self):
        state = State()
        words_1 = "JSRR R2".split()

        result = process_instr(words_1, state)
        assert result == Result.FOUND

        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:8] == "2080"

    def test_ld(self):
        words_1 = "LD R1, FOO".split()
        self.work_with_label(words_1, "2201")

    def test_ldi(self):
        words_1 = "LDI R1, FOO".split()
        self.work_with_label(words_1, "a201")

    def test_ldr(self):
        state = State()
        words_1 = "LDR R2, R1, #5".split()

        result = process_instr(words_1, state)
        assert result == Result.FOUND

        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:8] == "6445"

    def test_lea(self):
        words_1 = "LEA R1, FOO".split()
        self.work_with_label(words_1, "e201")

    def test_not(self):
        state = State()
        words_1 = "NOT R2, R1".split()

        result = process_instr(words_1, state)
        assert result == Result.FOUND

        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:8] == "947f"

    def test_st(self):
        words_1 = "ST R1, FOO".split()
        self.work_with_label(words_1, "3201")

    def test_sti(self):
        words_1 = "STI R1, FOO".split()
        self.work_with_label(words_1, "b201")

    def test_str(self):
        state = State()
        words_1 = "STR R2, R1, #5".split()

        result = process_instr(words_1, state)
        assert result == Result.FOUND

        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:8] == "7445"

    def test_getc(self):
        state = State()
        words_1 = "GETC".split()

        result = process_instr(words_1, state)
        assert result == Result.FOUND

        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:8] == "f020"

    def test_out(self):
        state = State()
        words_1 = "OUT".split()

        result = process_instr(words_1, state)
        assert result == Result.FOUND

        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:8] == "f021"

    def test_puts(self):
        state = State()
        words_1 = "PUTS".split()

        result = process_instr(words_1, state)
        assert result == Result.FOUND

        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:8] == "f022"

    def test_in(self):
        state = State()
        words_1 = "IN".split()

        result = process_instr(words_1, state)
        assert result == Result.FOUND

        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:8] == "f023"

    def test_putsp(self):
        state = State()
        words_1 = "PUTSP".split()

        result = process_instr(words_1, state)
        assert result == Result.FOUND

        output = produce_output(
            state.swap, state.memory, state.pc, state.orig
        )
        assert output.hex()[4:8] == "f024"

    def test_rti(self):
        pass
