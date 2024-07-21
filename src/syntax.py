import re
from enum import Enum
from typing import Literal

OperandsDirective = Literal[".STRINGZ", ".FILL", ".BLKW"]


class DirectiveArgCount(Enum):
    WITHOUT_GOTO_LABEL = 2
    WITH_GOTO_LABEL = 3


# ToDo[2]: works only for inline code
def parse_instruction(line: str) -> list[str]:
    line_without_comment = line.split(";")[0]
    line_without_tabs = line_without_comment.replace("\t", "")

    whitespace_split_exclude_double_quoted = r'\s+(?=(?:[^"]*"[^"]*")*[^"]*$)'
    return re.split(whitespace_split_exclude_double_quoted, line_without_tabs)


def cast_to_numeral(
    operand: str,
    allow_hexadecimal: bool = True,
    allow_decimal: bool = True,
    allow_binary: bool = True,
) -> int:
    if allow_hexadecimal and operand.startswith("x"):
        base = 16
    elif allow_decimal and operand.startswith("#"):
        base = 10
    elif allow_binary and operand.startswith("b"):
        base = 2
    else:
        raise ValueError(
            "Every value argument has to be prefixed with 'x' for hexadecimal, '#' "
            "for decimal and 'b' for binary values."
        )

    try:
        numeral = int(operand[1:], base)
        return numeral
    except ValueError as e:
        raise ValueError(f"Inappropriate value: {operand} for base {base}.") from e


def is_valid_goto_label(label: str) -> bool:
    return all(c.isalpha() or c.isdigit() or c == "_" for c in label)


def is_numeral_base_prefixed(operand: str) -> bool:
    return (
        True
        if operand.startswith("x") or operand.startswith("#") or operand.startswith("b")
        else False
    )


def validate_directive_syntax(
    instruction: list[str], directive_code: OperandsDirective
) -> DirectiveArgCount:
    if len(instruction) == DirectiveArgCount.WITHOUT_GOTO_LABEL.value:
        if instruction[0] != directive_code:
            raise SyntaxError(
                f"'{directive_code}' has to be first argument in the instruction."
            )
        result = DirectiveArgCount.WITHOUT_GOTO_LABEL
    elif len(instruction) == DirectiveArgCount.WITH_GOTO_LABEL.value:
        if instruction[1] != directive_code:
            raise SyntaxError(
                f"'{directive_code}' has to be second argument in the instruction."
            )
        if not is_valid_goto_label(instruction[0]):
            raise TypeError(
                f"Invalid label for {directive_code} directive: {instruction[0]}"
            )
        raise NotImplementedError("Processing label is not yet implemented.")
    else:
        raise SyntaxError(
            f"{directive_code} has only one argument and label optionally"
        )

    return result
