from typing import TYPE_CHECKING, List

from .bases import NextStateConditional
from ..vhdl_int import VhdlInt, VhdlIntType

if TYPE_CHECKING:
    from systemrdl.node import FieldNode

class Singlepulse(NextStateConditional):
    is_unconditional = True
    comment = "singlepulse clears back to 0"
    def is_match(self, field: 'FieldNode') -> bool:
        return field.get_property('singlepulse')

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        zero = VhdlInt(0, field.width, VhdlIntType.AGGREGATE)
        return [
            f"next_c := {zero};",
            "load_next_c := '1';",
        ]
