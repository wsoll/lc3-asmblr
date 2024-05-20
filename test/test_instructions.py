from asmblr import (
    link_labels_def_to_labels_usage,
    process_label,
)
from gbl_const import Result
from run import produce_output
from assembler import Assembler


class TestInstructions:
    def work_with_label(self, words_1, hex_output_result):
        assembler = Assembler()
        words_2 = "HALT".split()
        words_3 = "FOO .FILL xFF".split()

        result = assembler.process_instr(words_1)
        assert result == Result.FOUND

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
        assert output.hex()[4:8] == hex_output_result
        assert output.hex()[8:12] == "f025"
        assert output.hex()[12:16] == "00ff"

    def test_add_1(self):
        assembler = Assembler()
        words = "ADD R0, R1, R2".split()
        result = assembler.process_instr(words)
        assert result == Result.FOUND
        output = produce_output(assembler.swap, assembler.memory, assembler.pc, assembler.orig)
        assert output.hex()[4:8] == "1042"

    def test_add_2(self):
        assembler = Assembler()
        words = "ADD R0, R1, x5".split()
        result = assembler.process_instr(words)
        assert result == Result.FOUND
        output = produce_output(assembler.swap, assembler.memory, assembler.pc, assembler.orig)
        assert output.hex()[4:8] == "1065"

    def test_and_1(self):
        assembler = Assembler()
        words = "AND R3, R0, R2".split()
        result = assembler.process_instr(words)
        assert result == Result.FOUND
        output = produce_output(assembler.swap, assembler.memory, assembler.pc, assembler.orig)
        assert output.hex()[4:8] == "5602"

    def test_and_2(self):
        assembler = Assembler()
        words = "AND R3, R0, #14".split()
        result = assembler.process_instr(words)
        assert result == Result.FOUND
        output = produce_output(assembler.swap, assembler.memory, assembler.pc, assembler.orig)
        assert output.hex()[4:8] == "562e"

    def test_br_and_ret(self):
        assembler = Assembler()
        words_1 = "BRnp FOO".split()
        words_2 = "HALT".split()
        words_3 = "FOO AND R3, R0, #14".split()
        words_4 = "RET".split()

        result = assembler.process_instr(words_1)
        assert result == Result.FOUND

        result = assembler.process_instr(words_2)
        assert result == Result.FOUND

        result = process_label(words_3, assembler)
        assert result == Result.FOUND

        result = assembler.process_instr(words_4)
        assert result == Result.FOUND

        link_labels_def_to_labels_usage(
            assembler.labels_usage_address,
            assembler.labels_def_address,
            assembler.memory,
        )

        output = produce_output(assembler.swap, assembler.memory, assembler.pc, assembler.orig)
        assert output.hex()[4:8] == "0a01"
        assert output.hex()[8:12] == "f025"
        assert output.hex()[12:16] == "562e"
        assert output.hex()[16:20] == "c1c0"

    def test_jmp_1(self):
        assembler = Assembler()
        words_1 = "JMP R2".split()

        result = assembler.process_instr(words_1)
        assert result == Result.FOUND

        output = produce_output(assembler.swap, assembler.memory, assembler.pc, assembler.orig)
        assert output.hex()[4:8] == "c400"

    def test_jsr_and_ldr(self):
        assembler = Assembler()
        words_1 = "JSR FOO".split()
        words_2 = "HALT".split()
        words_3 = "HALT".split()
        words_4 = "FOO LDR R4, R2, x5".split()

        result = assembler.process_instr(words_1)
        assert result == Result.FOUND

        result = assembler.process_instr(words_2)
        assert result == Result.FOUND

        result = assembler.process_instr(words_3)
        assert result == Result.FOUND

        result = process_label(words_4, assembler)
        assert result == Result.FOUND

        link_labels_def_to_labels_usage(
            assembler.labels_usage_address,
            assembler.labels_def_address,
            assembler.memory,
        )
        output = produce_output(assembler.swap, assembler.memory, assembler.pc, assembler.orig)

        assert output.hex()[4:8] == "4802"
        assert output.hex()[8:12] == output.hex()[12:16] == "f025"
        assert output.hex()[16:20] == "6885"

    def test_jsrr(self):
        assembler = Assembler()
        words_1 = "JSRR R2".split()

        result = assembler.process_instr(words_1)
        assert result == Result.FOUND

        output = produce_output(assembler.swap, assembler.memory, assembler.pc, assembler.orig)
        assert output.hex()[4:8] == "2080"

    def test_ld(self):
        words_1 = "LD R1, FOO".split()
        self.work_with_label(words_1, "2201")

    def test_ldi(self):
        words_1 = "LDI R1, FOO".split()
        self.work_with_label(words_1, "a201")

    def test_ldr(self):
        assembler = Assembler()
        words_1 = "LDR R2, R1, #5".split()

        result = assembler.process_instr(words_1)
        assert result == Result.FOUND

        output = produce_output(assembler.swap, assembler.memory, assembler.pc, assembler.orig)
        assert output.hex()[4:8] == "6445"

    def test_lea(self):
        words_1 = "LEA R1, FOO".split()
        self.work_with_label(words_1, "e201")

    def test_not(self):
        assembler = Assembler()
        words_1 = "NOT R2, R1".split()

        result = assembler.process_instr(words_1)
        assert result == Result.FOUND

        output = produce_output(assembler.swap, assembler.memory, assembler.pc, assembler.orig)
        assert output.hex()[4:8] == "947f"

    def test_st(self):
        words_1 = "ST R1, FOO".split()
        self.work_with_label(words_1, "3201")

    def test_sti(self):
        words_1 = "STI R1, FOO".split()
        self.work_with_label(words_1, "b201")

    def test_str(self):
        assembler = Assembler()
        words_1 = "STR R2, R1, #5".split()

        result = assembler.process_instr(words_1)
        assert result == Result.FOUND

        output = produce_output(assembler.swap, assembler.memory, assembler.pc, assembler.orig)
        assert output.hex()[4:8] == "7445"

    def test_getc(self):
        assembler = Assembler()
        words_1 = "GETC".split()

        result = assembler.process_instr(words_1)
        assert result == Result.FOUND

        output = produce_output(assembler.swap, assembler.memory, assembler.pc, assembler.orig)
        assert output.hex()[4:8] == "f020"

    def test_out(self):
        assembler = Assembler()
        words_1 = "OUT".split()

        result = assembler.process_instr(words_1)
        assert result == Result.FOUND

        output = produce_output(assembler.swap, assembler.memory, assembler.pc, assembler.orig)
        assert output.hex()[4:8] == "f021"

    def test_puts(self):
        assembler = Assembler()
        words_1 = "PUTS".split()

        result = assembler.process_instr(words_1)
        assert result == Result.FOUND

        output = produce_output(assembler.swap, assembler.memory, assembler.pc, assembler.orig)
        assert output.hex()[4:8] == "f022"

    def test_in(self):
        assembler = Assembler()
        words_1 = "IN".split()

        result = assembler.process_instr(words_1)
        assert result == Result.FOUND

        output = produce_output(assembler.swap, assembler.memory, assembler.pc, assembler.orig)
        assert output.hex()[4:8] == "f023"

    def test_putsp(self):
        assembler = Assembler()
        words_1 = "PUTSP".split()

        result = assembler.process_instr(words_1)
        assert result == Result.FOUND

        output = produce_output(assembler.swap, assembler.memory, assembler.pc, assembler.orig)
        assert output.hex()[4:8] == "f024"

    def test_rti(self):
        pass
