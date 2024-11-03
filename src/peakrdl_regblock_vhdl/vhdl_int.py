from typing import Optional, Self
from enum import Enum


class VhdlIntType(Enum):
    # Integer literal '30'
    INTEGER = 1
    # Hexadecimal integer literal '16#1E#'
    INTEGER_HEX = 2
    # Hexadecimal bit string literal '5x"1E"'
    BIT_STRING = 3
    # Unsigned hexadecimal bit string literal '5Ux"1E"'
    BIT_STRING_UNSIGNED = 4
    # All ones or all zeros '(others => '0')'
    AGGREGATE = 5


class VhdlInt:
    """VHDL integer literal

    If width is not specified, the bit width required to represent the integer is used.

    If allow_std is True, BIT_STRING and AGGREGATE literals will be reduced to a std_logic
    literal if the width is 1 (e.g., '0').
    """
    def __init__(
            self,
            value: int,
            width: Optional[int] = None,
            kind: VhdlIntType = VhdlIntType.BIT_STRING,
            allow_std_logic: bool = True
        ) -> None:
        self.value = value
        self.kind = kind
        self.width = width
        self.allow_std_logic = allow_std_logic
        if self.value < 0:
            raise ValueError(f"Negative numbers can't be represented using VhdlInt (got {self.value})")
        if self.width is not None and self.value.bit_length() > self.width:
            raise ValueError(f"Can't represent {value} using only {width} bits")

    def __str__(self) -> str:
        width = max(1, self.width if self.width is not None else self.value.bit_length())

        if self.kind == VhdlIntType.INTEGER:
            return str(self.value)
        elif self.kind == VhdlIntType.INTEGER_HEX:
            return f"16#{self.value:X}#"
        elif self.kind == VhdlIntType.BIT_STRING:
            if width == 1 and self.allow_std_logic:
                return f"'{self.value}'"
            else:
                return f'{width}x"{self.value:X}"'
        elif self.kind == VhdlIntType.BIT_STRING_UNSIGNED:
            return f'{width}Ux"{self.value:X}"'
        elif self.kind == VhdlIntType.AGGREGATE:
            if self.width == 1 and self.allow_std_logic:
                return f"'{self.value}'"
            else:
                if self.value == 0:
                    return "(others => '0')"
                elif self.value == (1 << width) - 1:
                    return "(others => '1')"
                else:
                    raise ValueError(f"AGGREGATE type VhdlInt only supports all zeros or all ones (got {self.value}, width {self.width})")

    @classmethod
    def ones(cls, width: Optional[int] = None, allow_std_logic: bool = True) -> Self:
        """All ones aggregate "(others => '1')"

        May be reduced to '1' if allow_std_logic is True.
        """
        value = 2**width - 1 if width is not None else 1
        return cls(value, width, kind=VhdlIntType.AGGREGATE, allow_std_logic=allow_std_logic)

    @classmethod
    def zeros(cls, width: Optional[int] = None, allow_std_logic: bool = True) -> Self:
        """All zeros aggregate "(others => '0')"

        May be reduced to '0' if allow_std_logic is True.
        """
        return cls(0, width, kind=VhdlIntType.AGGREGATE, allow_std_logic=allow_std_logic)

    @classmethod
    def integer(cls, value: int) -> Self:
        """Decimal integer literal, such as "30"
        """
        return cls(value, kind=VhdlIntType.INTEGER)

    @classmethod
    def integer_hex(cls, value: int) -> Self:
        """Hexadecimal integer literal, such as "16#1E#"
        """
        return cls(value, kind=VhdlIntType.INTEGER_HEX)

    @classmethod
    def bit_string(cls, value: int, width: Optional[int] = None, allow_std_logic: bool = True) -> Self:
        """Bit string literal, such as 5x"1E"
        """
        return cls(value, width=width, kind=VhdlIntType.BIT_STRING, allow_std_logic=allow_std_logic)

    @classmethod
    def unsigned(cls, value: int, width: Optional[int] = None, allow_std_logic: bool = True) -> Self:
        """Unsigned string literal, such as 5Ux"1E"
        """
        return cls(value, width=width, kind=VhdlIntType.BIT_STRING_UNSIGNED, allow_std_logic=allow_std_logic)