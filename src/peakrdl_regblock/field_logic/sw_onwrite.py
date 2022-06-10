from typing import TYPE_CHECKING, List

from systemrdl.rdltypes import OnWriteType

from .bases import NextStateConditional

if TYPE_CHECKING:
    from systemrdl.node import FieldNode

# TODO: implement sw=w1 "write once" fields

class _OnWrite(NextStateConditional):
    onwritetype = None
    def is_match(self, field: 'FieldNode') -> bool:
        return field.is_sw_writable and field.get_property('onwrite') == self.onwritetype

    def get_predicate(self, field: 'FieldNode') -> str:
        strb = self.exp.dereferencer.get_access_strobe(field)

        if field.get_property('swwe') or field.get_property('swwel'):
            # dereferencer will wrap swwel complement if necessary
            qualifier = self.exp.dereferencer.get_field_propref_value(field, 'swwe')
            return f"{strb} && decoded_req_is_wr && {qualifier}"

        return f"{strb} && decoded_req_is_wr"


    def _wr_data(self, field: 'FieldNode') -> str:
        if field.msb < field.lsb:
            # Field gets bitswapped since it is in [low:high] orientation
            value = f"{{<<{{decoded_wr_data[{field.high}:{field.low}]}}}}"
        else:
            value = f"decoded_wr_data[{field.high}:{field.low}]"
        return value

class WriteOneSet(_OnWrite):
    comment = "SW write 1 set"
    onwritetype = OnWriteType.woset

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        R = self.exp.field_logic.get_storage_identifier(field)
        return [
            f"next_c = {R} | {self._wr_data(field)};",
            "load_next_c = '1;",
        ]

class WriteOneClear(_OnWrite):
    comment = "SW write 1 clear"
    onwritetype = OnWriteType.woclr

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        R = self.exp.field_logic.get_storage_identifier(field)
        return [
            f"next_c = {R} & ~{self._wr_data(field)};",
            "load_next_c = '1;",
        ]

class WriteOneToggle(_OnWrite):
    comment = "SW write 1 toggle"
    onwritetype = OnWriteType.wot

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        R = self.exp.field_logic.get_storage_identifier(field)
        return [
            f"next_c = {R} ^ {self._wr_data(field)};",
            "load_next_c = '1;",
        ]

class WriteZeroSet(_OnWrite):
    comment = "SW write 0 set"
    onwritetype = OnWriteType.wzs

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        R = self.exp.field_logic.get_storage_identifier(field)
        return [
            f"next_c = {R} | ~{self._wr_data(field)};",
            "load_next_c = '1;",
        ]

class WriteZeroClear(_OnWrite):
    comment = "SW write 0 clear"
    onwritetype = OnWriteType.wzc

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        R = self.exp.field_logic.get_storage_identifier(field)
        return [
            f"next_c = {R} & {self._wr_data(field)};",
            "load_next_c = '1;",
        ]

class WriteZeroToggle(_OnWrite):
    comment = "SW write 0 toggle"
    onwritetype = OnWriteType.wzt

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        R = self.exp.field_logic.get_storage_identifier(field)
        return [
            f"next_c = {R} ^ ~{self._wr_data(field)};",
            "load_next_c = '1;",
        ]

class WriteClear(_OnWrite):
    comment = "SW write clear"
    onwritetype = OnWriteType.wclr

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        return [
            "next_c = '0;",
            "load_next_c = '1;",
        ]

class WriteSet(_OnWrite):
    comment = "SW write set"
    onwritetype = OnWriteType.wset

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        return [
            "next_c = '1;",
            "load_next_c = '1;",
        ]

class Write(_OnWrite):
    comment = "SW write"
    onwritetype = None

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        return [
            f"next_c = {self._wr_data(field)};",
            "load_next_c = '1;",
        ]
