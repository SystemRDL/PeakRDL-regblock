from typing import TYPE_CHECKING, List

from .bases import NextStateConditional

if TYPE_CHECKING:
    from systemrdl.node import FieldNode

class Singlepulse(NextStateConditional):
    is_unconditional = True
    comment = "singlepulse clears back to 0"
    def is_match(self, field: 'FieldNode') -> bool:
        return field.get_property('singlepulse')

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        if field.width == 1:
            next_c_assign = "next_c := '0';"
        else:
            next_c_assign = "next_c := (others => '0');"
        return [
            next_c_assign,
            "load_next_c := '1';",
        ]
