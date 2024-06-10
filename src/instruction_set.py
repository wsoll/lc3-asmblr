from encoding import OpCode, Encoding, OperandType
from syntax import is_numeral_base_prefixed, cast_to_numeral


class InstructionSet:

    def process_operands(self, operation_code: str, operands: list[str]) -> int:
        match operation_code:
            case OpCode.ADD | OpCode.AND:
                return self.get_5_bit_flag_option_register_xor_numeral_encoding(
                    operands
                )
            case OpCode.BR:
                ...
            case OpCode.JMP | OpCode.JSRR:
                return self.get_base_register_only_operand_encoding(operands)
            case OpCode.JSR:
                ...
            case OpCode.LD | OpCode.LDI | OpCode.LEA | OpCode.ST | OpCode.STI:
                ...
            case OpCode.LDR | OpCode.STR:
                return self.get_6_bit_signed_offset_encoding(operands)
            case OpCode.NOT:
                return self.get_not_operand_encoding(operands)
            case OpCode.RET:
                if len(operands) != 0:
                    raise IndexError("Return instruction doesn't accept operands.")
                return 0
            case OpCode.RTI:
                ...
        raise RuntimeError("Processing operands for unknown instruction.")

    def validate_operands(
        self, operands: list[str], types_criteria: list[OperandType]
    ) -> None:
        """Validates syntax of operands for defined types criteria."""
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

    def get_5_bit_flag_option_register_xor_numeral_encoding(
        self, operands: list[str]
    ) -> int:
        """For common instructions that allow either register or numeral third operand.

        ADD, AND: 3-bit Destination Register, 3-Bit Source Register,
            (register option): 1-bit False flag, 2-bits fixed, 3-bit Source Register
            (numeral option): 1-bit True flag, 5-bit Immediate Value
        """
        self.validate_operands(
            operands,
            [
                OperandType.REGISTER,
                OperandType.REGISTER,
                OperandType.REGISTER_XOR_NUMERAL,
            ],
        )

        first_register_operand_encoding = (
            Encoding.REGISTERS[operands[0]] << Encoding.REGISTER_OPERANDS_POSITION[0]
        )
        second_register_operand_encoding = (
            Encoding.REGISTERS[operands[1]] << Encoding.REGISTER_OPERANDS_POSITION[1]
        )
        if operands[2] in Encoding.REGISTERS.keys():
            third_operand_encoding = (
                Encoding.REGISTERS[operands[2]]
                << Encoding.REGISTER_OPERANDS_POSITION[2]
            )
        elif is_numeral_base_prefixed(operands[2]):
            immediate_value_flag_position = 5
            third_operand_encoding = cast_to_numeral(operands[2]) | (
                1 << immediate_value_flag_position
            )
        else:
            raise TypeError(
                f"Unknown third operand type: {operands[2]}. "
                f"Register or immediate value are accepted only."
            )

        return (
            first_register_operand_encoding
            | second_register_operand_encoding
            | third_operand_encoding
        )

    def get_base_register_only_operand_encoding(self, operands: list[str]) -> int:
        """For common instructions that contain Base Register on 8-to-6 position.

        JMP, JSRR: 3-bits fixed, 3-bit Base Register, 6-bits fixed
        """
        self.validate_operands(operands, [OperandType.REGISTER])

        base_operand_encoding = (
            Encoding.REGISTERS[operands[0]] << Encoding.BASE_REGISTER_POSITION
        )
        return base_operand_encoding

    def get_not_operand_encoding(self, operands: list[str]) -> int:
        """For specific 'NOT' instruction.

        NOT: 3-bit Destination Register, 3-bit Source Register, 6-bit fixed.
        """
        self.validate_operands(operands, [OperandType.REGISTER, OperandType.REGISTER])

        first_operand_encoding = (
            Encoding.REGISTERS[operands[0]] << Encoding.REGISTER_OPERANDS_POSITION[0]
        )
        second_operand_encoding = (
            Encoding.REGISTERS[operands[1]] << Encoding.REGISTER_OPERANDS_POSITION[1]
        )
        return first_operand_encoding | second_operand_encoding

    def get_6_bit_signed_offset_encoding(self, operands: list[str]) -> int:
        """For common instructions that contain 6-bit singed offset.

        LDR: 3-bit Destination Register, 3-bit Base Register, 6-bit offset
        STR: 3-bit Source Register, 3-bit Base Register, 6-bit offset
        """
        self.validate_operands(
            operands, [OperandType.REGISTER, OperandType.REGISTER, OperandType.NUMERAL]
        )
        first_register_operand_encoding = (
            Encoding.REGISTERS[operands[0]] << Encoding.REGISTER_OPERANDS_POSITION[0]
        )
        second_register_operand_encoding = (
            Encoding.REGISTERS[operands[1]] << Encoding.REGISTER_OPERANDS_POSITION[1]
        )
        _6_bit_signed_offset_encoding = cast_to_numeral(operands[2])
        return (
            first_register_operand_encoding
            | second_register_operand_encoding
            | _6_bit_signed_offset_encoding
        )

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
            if type_criteria == OperandType.REGISTER_XOR_NUMERAL
            and (
                not is_numeral_base_prefixed(operand)
                and operand not in Encoding.REGISTERS
            )
            else False
        )
