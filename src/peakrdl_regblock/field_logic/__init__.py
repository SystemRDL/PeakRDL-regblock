from typing import TYPE_CHECKING

from systemrdl.rdltypes import PrecedenceType, InterruptType

from .bases import AssignmentPrecedence, NextStateConditional
from . import sw_onread
from . import sw_onwrite
from . import sw_singlepulse
from . import hw_write
from . import hw_set_clr
from . import hw_interrupts

from ..utils import get_indexed_path

from .generators import CombinationalStructGenerator, FieldStorageStructGenerator, FieldLogicGenerator

if TYPE_CHECKING:
    from typing import Dict, List
    from systemrdl.node import AddrmapNode, FieldNode
    from ..exporter import RegblockExporter

class FieldLogic:
    def __init__(self, exp:'RegblockExporter'):
        self.exp = exp

        self._hw_conditionals = {} # type: Dict[int, List[NextStateConditional]]
        self._sw_conditionals = {} # type: Dict[int, List[NextStateConditional]]

        self.init_conditionals()

    @property
    def top_node(self) -> 'AddrmapNode':
        return self.exp.top_node

    def get_storage_struct(self) -> str:
        struct_gen = FieldStorageStructGenerator(self)
        s = struct_gen.get_struct(self.top_node, "field_storage_t")

        # Only declare the storage struct if it exists
        if s is None:
            return ""

        return s + "\nfield_storage_t field_storage;"

    def get_combo_struct(self) -> str:
        struct_gen = CombinationalStructGenerator(self)
        s = struct_gen.get_struct(self.top_node, "field_combo_t")

        # Only declare the storage struct if it exists
        if s is None:
            return ""

        return s + "\nfield_combo_t field_combo;"

    def get_implementation(self) -> str:
        gen = FieldLogicGenerator(self)
        s = gen.get_content(self.top_node)
        if s is None:
            return ""
        return s

    #---------------------------------------------------------------------------
    # Field utility functions
    #---------------------------------------------------------------------------
    def get_storage_identifier(self, field: 'FieldNode') -> str:
        """
        Returns the Verilog string that represents the storage register element
        for the referenced field
        """
        assert field.implements_storage
        path = get_indexed_path(self.top_node, field)
        return f"field_storage.{path}.value"

    def get_next_q_identifier(self, field: 'FieldNode') -> str:
        """
        Returns the Verilog string that represents the storage register element
        for the delayed 'next' input value
        """
        assert field.implements_storage
        path = get_indexed_path(self.top_node, field)
        return f"field_storage.{path}.next_q"

    def get_field_combo_identifier(self, field: 'FieldNode', name: str) -> str:
        """
        Returns a Verilog string that represents a field's internal combinational
        signal.
        """
        assert field.implements_storage
        path = get_indexed_path(self.top_node, field)
        return f"field_combo.{path}.{name}"

    def get_counter_incr_strobe(self, field: 'FieldNode') -> str:
        """
        Return the Verilog string that represents the field's incr strobe signal.
        """
        prop_value = field.get_property('incr')
        if prop_value:
            return self.exp.dereferencer.get_value(prop_value)

        # unset by the user, points to the implied input signal
        return self.exp.hwif.get_implied_prop_input_identifier(field, "incr")

    def get_counter_incrvalue(self, field: 'FieldNode') -> str:
        """
        Return the string that represents the field's increment value
        """
        incrvalue = field.get_property('incrvalue')
        if incrvalue is not None:
            return self.exp.dereferencer.get_value(incrvalue)
        if field.get_property('incrwidth'):
            return self.exp.hwif.get_implied_prop_input_identifier(field, "incrvalue")
        return "1'b1"

    def get_counter_incrsaturate_value(self, field: 'FieldNode') -> str:
        prop_value = field.get_property('incrsaturate')
        if prop_value is True:
            return self.exp.dereferencer.get_value(2**field.width - 1)
        return self.exp.dereferencer.get_value(prop_value)

    def counter_incrsaturates(self, field: 'FieldNode') -> bool:
        """
        Returns True if the counter saturates
        """
        return field.get_property('incrsaturate') is not False

    def get_counter_incrthreshold_value(self, field: 'FieldNode') -> str:
        prop_value = field.get_property('incrthreshold')
        if isinstance(prop_value, bool):
            # No explicit value set. use max
            return self.exp.dereferencer.get_value(2**field.width - 1)
        return self.exp.dereferencer.get_value(prop_value)

    def get_counter_decr_strobe(self, field: 'FieldNode') -> str:
        """
        Return the Verilog string that represents the field's incr strobe signal.
        """
        prop_value = field.get_property('decr')
        if prop_value:
            return self.exp.dereferencer.get_value(prop_value)

        # unset by the user, points to the implied input signal
        return self.exp.hwif.get_implied_prop_input_identifier(field, "decr")

    def get_counter_decrvalue(self, field: 'FieldNode') -> str:
        """
        Return the string that represents the field's decrement value
        """
        decrvalue = field.get_property('decrvalue')
        if decrvalue is not None:
            return self.exp.dereferencer.get_value(decrvalue)
        if field.get_property('decrwidth'):
            return self.exp.hwif.get_implied_prop_input_identifier(field, "decrvalue")
        return "1'b1"

    def get_counter_decrsaturate_value(self, field: 'FieldNode') -> str:
        prop_value = field.get_property('decrsaturate')
        if prop_value is True:
            return "'d0"
        return self.exp.dereferencer.get_value(prop_value)

    def counter_decrsaturates(self, field: 'FieldNode') -> bool:
        """
        Returns True if the counter saturates
        """
        return field.get_property('decrsaturate') is not False

    def get_counter_decrthreshold_value(self, field: 'FieldNode') -> str:
        prop_value = field.get_property('decrthreshold')
        if isinstance(prop_value, bool):
            # No explicit value set. use min
            return "'d0"
        return self.exp.dereferencer.get_value(prop_value)

    def get_swacc_identifier(self, field: 'FieldNode') -> str:
        """
        Asserted when field is software accessed (read or write)
        """
        buffer_reads = field.parent.get_property('buffer_reads')
        buffer_writes = field.parent.get_property('buffer_writes')
        if buffer_reads and buffer_writes:
            rstrb = self.exp.read_buffering.get_trigger(field.parent)
            wstrb = self.exp.write_buffering.get_write_strobe(field)
            return f"{rstrb} || {wstrb}"
        elif buffer_reads and not buffer_writes:
            strb = self.exp.dereferencer.get_access_strobe(field)
            rstrb = self.exp.read_buffering.get_trigger(field.parent)
            return f"{rstrb} || ({strb} && decoded_req_is_wr)"
        elif not buffer_reads and buffer_writes:
            strb = self.exp.dereferencer.get_access_strobe(field)
            wstrb = self.exp.write_buffering.get_write_strobe(field)
            return f"{wstrb} || ({strb} && !decoded_req_is_wr)"
        else:
            strb = self.exp.dereferencer.get_access_strobe(field)
            return strb

    def get_rd_swacc_identifier(self, field: 'FieldNode') -> str:
        """
        Asserted when field is software accessed (read)
        """
        buffer_reads = field.parent.get_property('buffer_reads')
        if buffer_reads:
            rstrb = self.exp.read_buffering.get_trigger(field.parent)
            return rstrb
        else:
            strb = self.exp.dereferencer.get_access_strobe(field)
            return f"{strb} && !decoded_req_is_wr"

    def get_wr_swacc_identifier(self, field: 'FieldNode') -> str:
        """
        Asserted when field is software accessed (write)
        """
        buffer_writes = field.parent.get_property('buffer_writes')
        if buffer_writes:
            wstrb = self.exp.write_buffering.get_write_strobe(field)
            return wstrb
        else:
            strb = self.exp.dereferencer.get_access_strobe(field)
            return f"{strb} && decoded_req_is_wr"

    def get_swmod_identifier(self, field: 'FieldNode') -> str:
        """
        Asserted when field is modified by software (written or read with a
        set or clear side effect).
        """
        w_modifiable = field.is_sw_writable
        r_modifiable = field.get_property('onread') is not None
        buffer_writes = field.parent.get_property('buffer_writes')
        buffer_reads = field.parent.get_property('buffer_reads')

        if w_modifiable and not r_modifiable:
            # assert swmod only on sw write
            if buffer_writes:
                # Write strobe arrives from buffer layer instead
                wstrb = self.exp.write_buffering.get_write_strobe(field)
                return wstrb
            else:
                # Unbuffered. Use decoder strobe directly
                astrb = self.exp.dereferencer.get_access_strobe(field)
                return f"{astrb} && decoded_req_is_wr"

        if w_modifiable and r_modifiable:
            # assert swmod on both sw read and write
            astrb = self.exp.dereferencer.get_access_strobe(field)
            if buffer_writes or buffer_reads:
                if buffer_reads:
                    rstrb = self.exp.read_buffering.get_trigger(field.parent)
                else:
                    rstrb = f"{astrb} && !decoded_req_is_wr"

                if buffer_writes:
                    wstrb = self.exp.write_buffering.get_write_strobe(field)
                else:
                    wstrb = f"{astrb} && decoded_req_is_wr"

                return f"{wstrb} || {rstrb}"
            else:
                # Unbuffered. Use decoder strobe directly
                astrb = self.exp.dereferencer.get_access_strobe(field)
                return astrb

        if not w_modifiable and r_modifiable:
            # assert swmod only on sw read
            astrb = self.exp.dereferencer.get_access_strobe(field)
            if buffer_reads:
                rstrb = self.exp.read_buffering.get_trigger(field.parent)
            else:
                rstrb = f"{astrb} && !decoded_req_is_wr"
            return rstrb

        # Not sw modifiable
        return "1'b0"


    def has_next_q(self, field: 'FieldNode') -> bool:
        """
        Some fields require a delayed version of their 'next' input signal in
        order to do edge-detection.

        Returns True if this is the case.
        """
        if field.get_property('intr type') in {
            InterruptType.posedge,
            InterruptType.negedge,
            InterruptType.bothedge
        }:
            return True

        return False


    #---------------------------------------------------------------------------
    # Field Logic Conditionals
    #---------------------------------------------------------------------------
    def add_hw_conditional(self, conditional: NextStateConditional, precedence: AssignmentPrecedence) -> None:
        """
        Register a NextStateConditional action for hardware-triggered field updates.
        Categorizing conditionals correctly by hw/sw ensures that the RDL precedence
        property can be reliably honored.

        The ``precedence`` argument determines the conditional assignment's priority over
        other assignments of differing precedence.

        If multiple conditionals of the same precedence are registered, they are
        searched sequentially and only the first to match the given field is used.
        """
        if precedence not in self._hw_conditionals:
            self._hw_conditionals[precedence] = []
        self._hw_conditionals[precedence].append(conditional)


    def add_sw_conditional(self, conditional: NextStateConditional, precedence: AssignmentPrecedence) -> None:
        """
        Register a NextStateConditional action for software-triggered field updates.
        Categorizing conditionals correctly by hw/sw ensures that the RDL precedence
        property can be reliably honored.

        The ``precedence`` argument determines the conditional assignment's priority over
        other assignments of differing precedence.

        If multiple conditionals of the same precedence are registered, they are
        searched sequentially and only the first to match the given field is used.
        """
        if precedence not in self._sw_conditionals:
            self._sw_conditionals[precedence] = []
        self._sw_conditionals[precedence].append(conditional)


    def init_conditionals(self) -> None:
        """
        Initialize all possible conditionals here.

        Remember: The order in which conditionals are added matters within the
        same assignment precedence.
        """

        self.add_sw_conditional(sw_onread.ClearOnRead(self.exp), AssignmentPrecedence.SW_ONREAD)
        self.add_sw_conditional(sw_onread.SetOnRead(self.exp), AssignmentPrecedence.SW_ONREAD)

        self.add_sw_conditional(sw_onwrite.Write(self.exp), AssignmentPrecedence.SW_ONWRITE)
        self.add_sw_conditional(sw_onwrite.WriteSet(self.exp), AssignmentPrecedence.SW_ONWRITE)
        self.add_sw_conditional(sw_onwrite.WriteClear(self.exp), AssignmentPrecedence.SW_ONWRITE)
        self.add_sw_conditional(sw_onwrite.WriteZeroToggle(self.exp), AssignmentPrecedence.SW_ONWRITE)
        self.add_sw_conditional(sw_onwrite.WriteZeroClear(self.exp), AssignmentPrecedence.SW_ONWRITE)
        self.add_sw_conditional(sw_onwrite.WriteZeroSet(self.exp), AssignmentPrecedence.SW_ONWRITE)
        self.add_sw_conditional(sw_onwrite.WriteOneToggle(self.exp), AssignmentPrecedence.SW_ONWRITE)
        self.add_sw_conditional(sw_onwrite.WriteOneClear(self.exp), AssignmentPrecedence.SW_ONWRITE)
        self.add_sw_conditional(sw_onwrite.WriteOneSet(self.exp), AssignmentPrecedence.SW_ONWRITE)

        self.add_sw_conditional(sw_singlepulse.Singlepulse(self.exp), AssignmentPrecedence.SW_SINGLEPULSE)

        self.add_hw_conditional(hw_interrupts.PosedgeStickybit(self.exp), AssignmentPrecedence.HW_WRITE)
        self.add_hw_conditional(hw_interrupts.NegedgeStickybit(self.exp), AssignmentPrecedence.HW_WRITE)
        self.add_hw_conditional(hw_interrupts.BothedgeStickybit(self.exp), AssignmentPrecedence.HW_WRITE)
        self.add_hw_conditional(hw_interrupts.PosedgeNonsticky(self.exp), AssignmentPrecedence.HW_WRITE)
        self.add_hw_conditional(hw_interrupts.NegedgeNonsticky(self.exp), AssignmentPrecedence.HW_WRITE)
        self.add_hw_conditional(hw_interrupts.BothedgeNonsticky(self.exp), AssignmentPrecedence.HW_WRITE)
        self.add_hw_conditional(hw_interrupts.Sticky(self.exp), AssignmentPrecedence.HW_WRITE)
        self.add_hw_conditional(hw_interrupts.Stickybit(self.exp), AssignmentPrecedence.HW_WRITE)
        self.add_hw_conditional(hw_write.WEWrite(self.exp), AssignmentPrecedence.HW_WRITE)
        self.add_hw_conditional(hw_write.WELWrite(self.exp), AssignmentPrecedence.HW_WRITE)
        self.add_hw_conditional(hw_write.AlwaysWrite(self.exp), AssignmentPrecedence.HW_WRITE)

        self.add_hw_conditional(hw_set_clr.HWClear(self.exp), AssignmentPrecedence.HWCLR)

        self.add_hw_conditional(hw_set_clr.HWSet(self.exp), AssignmentPrecedence.HWSET)


    def _get_X_conditionals(self, conditionals: 'Dict[int, List[NextStateConditional]]', field: 'FieldNode') -> 'List[NextStateConditional]':
        result = []
        precedences = sorted(conditionals.keys(), reverse=True)
        for precedence in precedences:
            for conditional in conditionals[precedence]:
                if conditional.is_match(field):
                    result.append(conditional)
                    break
        return result


    def get_conditionals(self, field: 'FieldNode') -> 'List[NextStateConditional]':
        """
        Get a list of NextStateConditional objects that apply to the given field.

        The returned list is sorted in priority order - the conditional with highest
        precedence is first in the list.
        """
        sw_precedence = field.get_property('precedence') == PrecedenceType.sw
        result = []

        if sw_precedence:
            result.extend(self._get_X_conditionals(self._sw_conditionals, field))

        result.extend(self._get_X_conditionals(self._hw_conditionals, field))

        if not sw_precedence:
            result.extend(self._get_X_conditionals(self._sw_conditionals, field))

        return result
