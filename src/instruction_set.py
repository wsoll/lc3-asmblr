from encoding import OpCode, Encoding, OperandType
from syntax import is_numeral_base_prefixed, cast_to_numeral


class InstructionSet:

    def process_operands(self, operation_code: str, operands: list[str]) -> int:
        match operation_code:
            case OpCode.ADD | OpCode.AND:
                return self.get_add_or_and_operands_encoding(operands)
            case OpCode.BR:
                ...
            case OpCode.JMP | OpCode.JSRR:
                return self.get_jump_or_jump_to_subroutine_register_operand_encoding(
                    operands
                )
            case OpCode.JSR:
                ...
            case OpCode.LD | OpCode.LDI | OpCode.LEA:
                ...
            case OpCode.LDR | OpCode.STR:
                return self.get_store_or_load_base_encoding(operands)
            case OpCode.NOT:
                return self.get_not_operand_encoding(operands)
            case OpCode.RET:
                if len(operands) != 0:
                    raise IndexError("Return instruction doesn't accept operands.")
                return 0
            case OpCode.RTI:
                ...
            case OpCode.ST | OpCode.STI:
                ...
        raise RuntimeError("Processing operands for unknown instruction.")

    def validate_operands(
        self, operands: list[str], types_criteria: list[OperandType]
    ) -> None:
        operands_count = len(operands)
        expected_operands_count = len(types_criteria)

        if operands_count != expected_operands_count:
            raise IndexError(
                f"Invalid operands number - expected: {expected_operands_count}, "
                f"actual {operands_count}"
            )

        for index, (operand, type_criteria) in enumerate(zip(operands, types_criteria)):
            if self.must_be_register_and_is_not(operand, type_criteria):
                raise TypeError(f"Operand ({index+1}) isn't a register.")
            elif self.must_be_numeral_and_is_not(operand, type_criteria):
                raise TypeError(f"Operand ({index+1}) isn't a numeral.")
            elif self.must_be_either_register_or_numeral_and_is_not(
                operand, type_criteria
            ):
                raise TypeError(f"Operand ({index+1}) isn't a register nor a numeral.")

    def get_add_or_and_operands_encoding(self, operands: list[str]) -> int:
        self.validate_operands(
            operands,
            [OperandType.REGISTER, OperandType.REGISTER, OperandType.EITHER_OR],
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

    def get_jump_or_jump_to_subroutine_register_operand_encoding(
        self, operands: list[str]
    ) -> int:
        self.validate_operands(operands, [OperandType.REGISTER])

        base_operand_encoding = (
            Encoding.REGISTERS[operands[0]] << Encoding.BASE_REGISTER_POSITION
        )
        return base_operand_encoding

    def get_not_operand_encoding(self, operands: list[str]) -> int:
        self.validate_operands(operands, [OperandType.REGISTER, OperandType.REGISTER])

        first_operand_encoding = (
            Encoding.REGISTERS[operands[0]] << Encoding.REGISTER_OPERANDS_POSITION[0]
        )
        second_operand_encoding = (
            Encoding.REGISTERS[operands[1]] << Encoding.REGISTER_OPERANDS_POSITION[1]
        )
        return first_operand_encoding | second_operand_encoding

    def get_store_or_load_base_encoding(self, operands: list[str]) -> int:
        self.validate_operands(
            operands, [OperandType.REGISTER, OperandType.REGISTER, OperandType.NUMERAL]
        )
        first_operand_encoding = (
            Encoding.REGISTERS[operands[0]] << Encoding.REGISTER_OPERANDS_POSITION[0]
        )
        second_operand_encoding = (
            Encoding.REGISTERS[operands[1]] << Encoding.REGISTER_OPERANDS_POSITION[1]
        )
        third_operand_encoding = cast_to_numeral(operands[2])
        return first_operand_encoding | second_operand_encoding | third_operand_encoding

    @staticmethod
    def must_be_register_and_is_not(operand: str, type_criteria: OperandType) -> bool:
        return (
            True
            if type_criteria == OperandType.REGISTER
            and operand not in Encoding.REGISTERS
            else False
        )

    @staticmethod
    def must_be_numeral_and_is_not(operand: str, type_criteria: OperandType) -> bool:
        return (
            True
            if type_criteria == OperandType.NUMERAL
            and not is_numeral_base_prefixed(operand)
            else False
        )

    @staticmethod
    def must_be_either_register_or_numeral_and_is_not(
        operand: str, type_criteria: OperandType
    ) -> bool:
        return (
            True
            if type_criteria == OperandType.EITHER_OR
            and (
                not is_numeral_base_prefixed(operand)
                and operand not in Encoding.REGISTERS
            )
            else False
        )
