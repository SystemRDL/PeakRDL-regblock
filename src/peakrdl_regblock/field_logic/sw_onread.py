from typing import TYPE_CHECKING, List

from systemrdl.rdltypes import OnReadType

from .bases import NextStateConditional
from ..vhdl_int import VhdlInt, VhdlIntType

if TYPE_CHECKING:
    from systemrdl.node import FieldNode

class _OnRead(NextStateConditional):
    onreadtype = None
    def is_match(self, field: 'FieldNode') -> bool:
        return field.get_property('onread') == self.onreadtype

    def get_predicate(self, field: 'FieldNode') -> str:
        if field.parent.get_property('buffer_reads'):
            # Is buffered read. Use alternate strobe
            rstrb = self.exp.read_buffering.get_trigger(field.parent)
            return rstrb
        else:
            # is regular register
            strb = self.exp.dereferencer.get_access_strobe(field)
            return f"{strb} and not decoded_req_is_wr"


class ClearOnRead(_OnRead):
    comment = "SW clear on read"
    onreadtype = OnReadType.rclr

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        zero = VhdlInt(0, field.width, VhdlIntType.AGGREGATE)
        return [
            f"next_c := {zero};",
            "load_next_c := '1';",
        ]


class SetOnRead(_OnRead):
    comment = "SW set on read"
    onreadtype = OnReadType.rset

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        ones = VhdlInt((1 << field.width) - 1, field.width, VhdlIntType.AGGREGATE)
        return [
            f"next_c := {ones};",
            "load_next_c := '1';",
        ]
