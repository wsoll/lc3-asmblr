def parse_assembly(line: str) -> list[str]:
    line_without_comment = line.split(";")[0]
    line_without_tabs = line_without_comment.replace("\t", "")

    return line_without_tabs.split()


def cast_value_argument(
    arg: str, allow_decimal: bool = True, allow_binary: bool = True
) -> int:
    if arg.startswith("x"):
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
