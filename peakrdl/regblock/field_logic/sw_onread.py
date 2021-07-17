from typing import TYPE_CHECKING, List

from systemrdl.rdltypes import OnReadType

from .bases import NextStateConditional

if TYPE_CHECKING:
    from systemrdl.node import FieldNode

class _OnRead(NextStateConditional):
    onreadtype = None
    def is_match(self, field: 'FieldNode') -> bool:
        return field.get_property("onread") == self.onreadtype

    def get_conditional(self, field: 'FieldNode') -> str:
        strb = self.exporter.dereferencer.get_access_strobe(field)
        return f"decoded_req && !decoded_req_is_wr && {strb}"

class ClearOnRead(_OnRead):
    onreadtype = OnReadType.rclr

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = '0;",
            f"field_combo.{field_path}.load_next = '1;",
        ]


class SetOnRead(_OnRead):
    onreadtype = OnReadType.rset

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = '1;",
            f"field_combo.{field_path}.load_next = '1;",
        ]
