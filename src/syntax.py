import re
from typing import Literal

Directive = Literal[".FILL", ".BLKW", ".STRINGZ"]


def parse_assembly(line: str) -> list[str]:
    line_without_comment = line.split(";")[0]
    line_without_tabs = line_without_comment.replace("\t", "")

    whitespace_split_exclude_double_quoted = r'\s+(?=(?:[^"]*"[^"]*")*[^"]*$)'
    return re.split(whitespace_split_exclude_double_quoted, line_without_tabs)


def cast_value_argument(
    arg: str,
    allow_hexadecimal: bool = True,
    allow_decimal: bool = True,
    allow_binary: bool = True,
) -> int:
    if allow_hexadecimal and arg.startswith("x"):
        base = 16
    elif allow_decimal and arg.startswith("#"):
        base = 10
    elif allow_binary and arg.startswith("b"):
        base = 2
    else:
        raise ValueError(
            "Every value argument has to be prefixed with 'x' for hexadecimal, '#' "
            "for decimal and 'b' for binary values."
        )

    try:
        value = int(arg[1:], base)
        return value
    except ValueError as e:
        raise ValueError(f"Inappropriate value: {arg} for base {base}.") from e


def is_valid_label(label: str) -> bool:
    return all(c.isalpha() or c.isdigit() or c == "_" for c in label)


def is_value(arg: str) -> bool:
    return (
        True
        if arg.startswith("x") or arg.startswith("#") or arg.startswith("b")
        else False
    )


def validate_directive(line: list[str], directive_key: Directive) -> int:
    if len(line) == 2:
        if line[0] != directive_key:
            raise SyntaxError(
                f"'{directive_key}' has to be first argument in the line."
            )
        return 2
    elif len(line) == 3:
        if line[1] != directive_key:
            raise SyntaxError(
                f"'{directive_key}' has to be second argument in the line."
            )
        if not is_valid_label(line[0]):
            raise TypeError(f"Invalid label for {directive_key} directive: {line[0]}")
        return 3
    else:
        raise SyntaxError(f"{directive_key} has only one argument and label optionally")
