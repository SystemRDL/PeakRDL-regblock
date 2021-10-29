from typing import TYPE_CHECKING, List

from systemrdl.rdltypes import OnWriteType

from .bases import NextStateConditional

if TYPE_CHECKING:
    from systemrdl.node import FieldNode

# TODO: implement sw=w1 "write once" fields

class _OnWrite(NextStateConditional):
    onwritetype = None
    def is_match(self, field: 'FieldNode') -> bool:
        return field.get_property("onwrite") == self.onwritetype

    def get_predicate(self, field: 'FieldNode') -> str:
        strb = self.exp.dereferencer.get_access_strobe(field)
        return f"decoded_req && decoded_req_is_wr && {strb}"

class WriteOneSet(_OnWrite):
    comment = "SW write 1 set"
    onwritetype = OnWriteType.woset

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = field_storage.{field_path} | decoded_wr_data;",
            f"field_combo.{field_path}.load_next = '1;",
        ]

class WriteOneClear(_OnWrite):
    comment = "SW write 1 clear"
    onwritetype = OnWriteType.woclr

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = field_storage.{field_path} & ~decoded_wr_data;",
            f"field_combo.{field_path}.load_next = '1;",
        ]

class WriteOneToggle(_OnWrite):
    comment = "SW write 1 toggle"
    onwritetype = OnWriteType.wot

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = field_storage.{field_path} ^ decoded_wr_data;",
            f"field_combo.{field_path}.load_next = '1;",
        ]

class WriteZeroSet(_OnWrite):
    comment = "SW write 0 set"
    onwritetype = OnWriteType.wzs

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = field_storage.{field_path} | ~decoded_wr_data;",
            f"field_combo.{field_path}.load_next = '1;",
        ]

class WriteZeroClear(_OnWrite):
    comment = "SW write 0 clear"
    onwritetype = OnWriteType.wzc

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = field_storage.{field_path} & decoded_wr_data;",
            f"field_combo.{field_path}.load_next = '1;",
        ]

class WriteZeroToggle(_OnWrite):
    comment = "SW write 0 toggle"
    onwritetype = OnWriteType.wzt

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = field_storage.{field_path} ^ ~decoded_wr_data;",
            f"field_combo.{field_path}.load_next = '1;",
        ]

class WriteClear(_OnWrite):
    comment = "SW write clear"
    onwritetype = OnWriteType.wclr

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = '0;",
            f"field_combo.{field_path}.load_next = '1;",
        ]

class WriteSet(_OnWrite):
    comment = "SW write set"
    onwritetype = OnWriteType.wset

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = '1;",
            f"field_combo.{field_path}.load_next = '1;",
        ]

class Write(_OnWrite):
    comment = "SW write"
    onwritetype = None

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = decoded_wr_data;",
            f"field_combo.{field_path}.load_next = '1;",
        ]
