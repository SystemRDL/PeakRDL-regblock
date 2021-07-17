from typing import TYPE_CHECKING, List

from systemrdl.rdltypes import OnWriteType

from .bases import NextStateConditional

if TYPE_CHECKING:
    from systemrdl.node import FieldNode

class _OnWrite(NextStateConditional):
    onwritetype = None
    def is_match(self, field: 'FieldNode') -> bool:
        return field.get_property("onwrite") == self.onwritetype

    def get_conditional(self, field: 'FieldNode') -> str:
        strb = self.exporter.dereferencer.get_access_strobe(field)
        return f"decoded_req && decoded_req_is_wr && {strb}"

class WriteOneSet(_OnWrite):
    onwritetype = OnWriteType.woset

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = field_storage.{field_path} | decoded_wr_data;",
            f"field_combo.{field_path}.load_next = '1;",
        ]

class WriteOneClear(_OnWrite):
    onwritetype = OnWriteType.woclr

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = field_storage.{field_path} & ~decoded_wr_data;",
            f"field_combo.{field_path}.load_next = '1;",
        ]

class WriteOneToggle(_OnWrite):
    onwritetype = OnWriteType.wot

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = field_storage.{field_path} ^ decoded_wr_data;",
            f"field_combo.{field_path}.load_next = '1;",
        ]

class WriteZeroSet(_OnWrite):
    onwritetype = OnWriteType.wzs

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = field_storage.{field_path} | ~decoded_wr_data;",
            f"field_combo.{field_path}.load_next = '1;",
        ]

class WriteZeroClear(_OnWrite):
    onwritetype = OnWriteType.wzc

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = field_storage.{field_path} & decoded_wr_data;",
            f"field_combo.{field_path}.load_next = '1;",
        ]

class WriteZeroToggle(_OnWrite):
    onwritetype = OnWriteType.wzt

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = field_storage.{field_path} ^ ~decoded_wr_data;",
            f"field_combo.{field_path}.load_next = '1;",
        ]

class WriteClear(_OnWrite):
    onwritetype = OnWriteType.wclr

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = '0;",
            f"field_combo.{field_path}.load_next = '1;",
        ]

class WriteSet(_OnWrite):
    onwritetype = OnWriteType.wset

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = '1;",
            f"field_combo.{field_path}.load_next = '1;",
        ]

class Write(_OnWrite):
    onwritetype = None

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = decoded_wr_data;",
            f"field_combo.{field_path}.load_next = '1;",
        ]
