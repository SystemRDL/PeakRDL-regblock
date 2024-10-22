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

    For example, 30 is formatted as "1" & X"E".
    """
    def __init__(self, value: int, width: Optional[int] = None) -> None:
        self.value = value
        self.width = width
        if self.width is not None and self.value.bit_length() > self.width:
            raise ValueError(f"Can't represent {value} using only {width} bits")

    def __str__(self) -> str:
        width = self.width if self.width is not None else self.value.bit_length()
        num_hex_chars = width // 4
        num_bin_chars = width % 4

        hex_mask = (1 << (num_hex_chars * 4)) - 1
        hex_chars = f'X"{self.value & hex_mask:0{num_hex_chars}X}"'

        if num_bin_chars:
            bin_chars = f'"{self.value >> (num_hex_chars * 4):0{num_bin_chars}b}" & '
        else:
            bin_chars = ""

        return bin_chars + hex_chars


class SVInt:
    def __init__(self, value: int, width: Optional[int] = None) -> None:
        self.value = value
        self.width = width

    def __str__(self) -> str:
        if self.width is not None:
            # Explicit width
            return f"{self.width}'h{self.value:x}"
        elif self.value.bit_length() > 32:
            # SV standard only enforces that unsized literals shall be at least 32-bits
            # To support larger literals, they need to be sized explicitly
            return f"{self.value.bit_length()}'h{self.value:x}"
        else:
            return f"'h{self.value:x}"
