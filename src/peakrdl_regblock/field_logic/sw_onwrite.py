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

    def _wbus_bitslice(self, field: 'FieldNode', subword_idx: int) -> str:
        # Get the source bitslice range from the internal cpuif's data bus
        # For normal fields this ends up passing-through the field's low/high
        # values unchanged.
        # For fields within a wide register (accesswidth < regwidth), low/high
        # may be shifted down and clamped depending on which sub-word is being accessed
        accesswidth = field.parent.get_property('accesswidth')

        # Shift based on subword
        high = field.high - (subword_idx * accesswidth)
        low = field.low - (subword_idx * accesswidth)

        # clamp to accesswidth
        high = max(min(high, accesswidth), 0)
        low = max(min(low, accesswidth), 0)

        return f"[{high}:{low}]"

    def _wr_data(self, field: 'FieldNode', subword_idx: int=0) -> str:
        bslice = self._wbus_bitslice(field, subword_idx)

        if field.msb < field.lsb:
            # Field gets bitswapped since it is in [low:high] orientation
            value = f"{{<<{{decoded_wr_data{bslice}}}}}"
        else:
            value = f"decoded_wr_data{bslice}"
        return value

    def _wr_biten(self, field: 'FieldNode', subword_idx: int=0) -> str:
        bslice = self._wbus_bitslice(field, subword_idx)

        if field.msb < field.lsb:
            # Field gets bitswapped since it is in [low:high] orientation
            value = f"{{<<{{decoded_wr_biten{bslice}}}}}"
        else:
            value = f"decoded_wr_biten{bslice}"
        return value

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        accesswidth = field.parent.get_property("accesswidth")

        # Due to 10.6.1-f, it is impossible for a field with an onwrite action to
        # be split across subwords.
        # Therefore it is ok to get the subword idx from only one of the bit offsets
        sidx = field.low // accesswidth

        # field does not get split between subwords
        R = self.exp.field_logic.get_storage_identifier(field)
        D = self._wr_data(field, sidx)
        S = self._wr_biten(field, sidx)
        lines = [
            f"next_c = {self.get_onwrite_rhs(R, D, S)};",
            "load_next_c = '1;",
        ]
        return lines

    def get_onwrite_rhs(self, reg: str, data: str, strb: str) -> str:
        raise NotImplementedError


class WriteOneSet(_OnWrite):
    comment = "SW write 1 set"
    onwritetype = OnWriteType.woset

    def get_onwrite_rhs(self, reg: str, data: str, strb: str) -> str:
        return f"{reg} | ({data} & {strb})"

class WriteOneClear(_OnWrite):
    comment = "SW write 1 clear"
    onwritetype = OnWriteType.woclr

    def get_onwrite_rhs(self, reg: str, data: str, strb: str) -> str:
        return f"{reg} & ~({data} & {strb})"

class WriteOneToggle(_OnWrite):
    comment = "SW write 1 toggle"
    onwritetype = OnWriteType.wot

    def get_onwrite_rhs(self, reg: str, data: str, strb: str) -> str:
        return f"{reg} ^ ({data} & {strb})"

class WriteZeroSet(_OnWrite):
    comment = "SW write 0 set"
    onwritetype = OnWriteType.wzs

    def get_onwrite_rhs(self, reg: str, data: str, strb: str) -> str:
        return f"{reg} | (~{data} & {strb})"

class WriteZeroClear(_OnWrite):
    comment = "SW write 0 clear"
    onwritetype = OnWriteType.wzc

    def get_onwrite_rhs(self, reg: str, data: str, strb: str) -> str:
        return f"{reg} & ({data} | ~{strb})"

class WriteZeroToggle(_OnWrite):
    comment = "SW write 0 toggle"
    onwritetype = OnWriteType.wzt

    def get_onwrite_rhs(self, reg: str, data: str, strb: str) -> str:
        return f"{reg} ^ (~{data} & {strb})"

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

    def get_onwrite_rhs(self, reg: str, data: str, strb: str) -> str:
        return f"({reg} & ~{strb}) | ({data} & {strb})"
