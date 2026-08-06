from typing import TYPE_CHECKING, List, Optional

from systemrdl.rdltypes import OnWriteType

from .bases import NextStateConditional, SVLogic

if TYPE_CHECKING:
    from systemrdl.node import FieldNode


class _OnWrite(NextStateConditional):
    onwritetype: Optional[OnWriteType] = None
    def is_match(self, field: 'FieldNode') -> bool:
        return field.is_sw_writable and field.get_property('onwrite') == self.onwritetype

    def get_predicate(self, field: 'FieldNode') -> str:
        if field.parent.get_property('buffer_writes'):
            # Is buffered write. Use alternate strobe
            predicate = self.exp.write_buffering.get_write_strobe(field)
        else:
            # is regular register
            strb = self.exp.dereferencer.get_access_strobe(field)
            predicate = f"{strb} && decoded_req_is_wr"

        if field.get_property('swwe') or field.get_property('swwel'):
            # dereferencer will wrap swwel complement if necessary
            qualifier = self.exp.dereferencer.get_field_propref_value(field, 'swwe')
            predicate += f" && {qualifier}"

        if self.exp.field_logic.has_write_once(field):
            predicate += f" && {self.exp.field_logic.get_write_once_identifier(field)}"

        return predicate

    def get_extra_combo_signals(self, field: 'FieldNode') -> List[SVLogic]:
        """Get additional signals that need to be added to the combinatorial logic for this field.

        - Write-once fields require a write_once_clr signal to be added to the logic.
        """
        if self.exp.field_logic.has_write_once(field):
            return [SVLogic("write_once_clr", 1, "1'b0")]
        return []

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        accesswidth = field.parent.get_property("accesswidth")

        # Due to 10.6.1-f, it is impossible for a field with an onwrite action to
        # be split across subwords.
        # Therefore it is ok to get the subword idx from only one of the bit offsets
        sidx = field.low // accesswidth

        # field does not get split between subwords
        R = self.exp.field_logic.get_storage_identifier(field)
        D = self.exp.field_logic.get_wr_data(field, sidx)
        S = self.exp.field_logic.get_wr_biten(field, sidx)
        lines = [
            f"next_c = {self.get_onwrite_rhs(R, D, S)};",
            "load_next_c = '1;",
        ]
        if self.exp.field_logic.has_write_once(field):
            write_once_clr = self.exp.field_logic.get_field_combo_identifier(field, "write_once_clr")
            lines.append(f"{write_once_clr} = '1;")
        return lines

    def get_onwrite_rhs(self, reg: str, data: str, strb: str) -> str:
        raise NotImplementedError


#-------------------------------------------------------------------------------
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
