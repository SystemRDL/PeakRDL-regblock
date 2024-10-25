from typing import Optional


class VhdlInt:
    """VHDL literal integer formatted in hexadecimal

    For example, 30 is formatted as 16#1E#.
    """
    def __init__(self, value: int) -> None:
        self.value = value

    def __str__(self) -> str:
        return f"16#{self.value:X}#"


class VhdlVectorInt:
    """VHDL vector literal formatted in hexadecimal

    For example, 30 is formatted as `5x"1E"`. The zero and all-ones values
    are handled specifically to produce an aggregate `"(others => 'x')"`.

    If allow_std_logic is true and the width is 1, a std_logic literal will
    be produced (`'0'` or `'1'`)
    """
    def __init__(self, value: int, width: Optional[int] = None, allow_std_logic=False) -> None:
        self.value = value
        self.width = width
        self.allow_std_logic = allow_std_logic
        if self.width is not None and self.value.bit_length() > self.width:
            raise ValueError(f"Can't represent {value} using only {width} bits")

    def __str__(self) -> str:
        width = self.width if self.width is not None else self.value.bit_length()
        # handle std_logic
        if width == 1 and self.allow_std_logic:
            return f"'{self.value}'"

        # handle all zeros or all ones
        if self.value == 0:
            return "(others => '0')"
        elif self.value == (1 << width) - 1:
            return "(others => '1')"

        return f'{width}x"{self.value:X}"'
