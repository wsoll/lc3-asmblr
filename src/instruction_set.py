from encoding import OpCode, Encoding
from syntax import is_numeral_base_prefixed, is_valid_goto_label, cast_to_numeral


class InstructionSet:

    def process_operands(self, operation_code: str, operands: list[str]) -> int:
        operands_binary_repr = 0x000
        match operation_code:
            case OpCode.ADD:
                operands_binary_repr |= self.get_add_and_operands_encoding(operands)
            case OpCode.AND:
                operands_binary_repr |= self.get_add_and_operands_encoding(operands)
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

    @staticmethod
    def get_add_and_operands_encoding(operands: list[str]) -> int:
        is_three_operands = True if len(operands) == 3 else False
        is_first_operand_destination_register = (
            True if operands[0] in Encoding.REGISTERS.keys() else False
        )
        is_second_operand_source_register = (
            True if operands[1] in Encoding.REGISTERS.keys() else False
        )
        if (
            not is_three_operands
            or not is_first_operand_destination_register
            or not is_second_operand_source_register
        ):
            raise SyntaxError(
                f"Operands validation failure - Three operands: {is_three_operands}, "
                f"First operand is destination register: "
                f"{is_first_operand_destination_register}, Second operand is source "
                f"register: {is_second_operand_source_register}"
            )

        first_operand_encoding = (
            Encoding.REGISTERS[operands[0]] << Encoding.REGISTER_OPERANDS_POSITION[0]
        )
        second_operand_encoding = (
            Encoding.REGISTERS[operands[1]] << Encoding.REGISTER_OPERANDS_POSITION[1]
        )
        if operands[2] in Encoding.REGISTERS.keys():
            third_operand_encoding = (
                Encoding.REGISTERS[operands[2]]
                << Encoding.REGISTER_OPERANDS_POSITION[2]
            )
        elif is_numeral_base_prefixed(operands[2]):
            third_operand_encoding = cast_to_numeral(operands[2]) | (
                1 << Encoding.OPERATION_IMMEDIATE_VALUE_FLAG_POSITION[OpCode.ADD]
            )
        else:
            raise TypeError(
                f"Unknown third operand type: {operands[2]}. "
                f"Register or immediate value are accepted only."
            )

        return first_operand_encoding | second_operand_encoding | third_operand_encoding
