from encoding import OpCode, Encoding
from syntax import is_numeral_base_prefixed, is_valid_goto_label, cast_to_numeral


class InstructionSet:

    def process_operands(self, operation_code: str, operands: list[str]) -> int:
        operands_binary_repr = 0x000
        match operation_code:
            case OpCode.ADD:
                operands_binary_repr |= self.get_operands_encoding(operands)
            case OpCode.AND:
                operands_binary_repr |= self.get_operands_encoding(operands)
            case OpCode.BR:
                ...
            case OpCode.JMP:
                operands_binary_repr |= self.get_operands_encoding(operands)
            case OpCode.JSR:
                ...
            case OpCode.JSRR:
                ...
            case OpCode.LD:
                ...
            case OpCode.LDI:
                ...
            case OpCode.LDR:
                ...
            case OpCode.LEA:
                ...
            case OpCode.NOT:
                operands_binary_repr |= self.get_operands_encoding(operands)
            case OpCode.RET:
                ...
            case OpCode.RTI:
                ...
            case OpCode.ST:
                ...
            case OpCode.STI:
                ...
            case OpCode.STR:
                ...
        return operands_binary_repr

    def get_operands_encoding(self, operands: list[str]) -> int:
        operands_encoding = 0
        register_operand_counter = 0

        for operand in operands:
            if operand in Encoding.REGISTERS.keys():
                operands_encoding |= (
                    Encoding.REGISTERS[operand]
                    << Encoding.REGISTER_OPERANDS_POSITION[register_operand_counter]
                )
                register_operand_counter += 1
            elif is_numeral_base_prefixed(operand):
                ...
            elif is_valid_goto_label(operand):
                raise NotImplementedError()

        return operands_encoding
