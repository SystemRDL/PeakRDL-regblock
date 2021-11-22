from typing import TYPE_CHECKING

from systemrdl.rdltypes import PropertyReference, PrecedenceType

from .bases import AssignmentPrecedence, NextStateConditional
from . import sw_onread
from . import sw_onwrite
from . import hw_write
from . import hw_set_clr

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
        struct_gen = FieldStorageStructGenerator()
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
    def get_storage_identifier(self, node: 'FieldNode') -> str:
        """
        Returns the Verilog string that represents the storage register element
        for the referenced field
        """
        assert node.implements_storage
        path = get_indexed_path(self.top_node, node)
        return f"field_storage.{path}"

    def get_field_next_identifier(self, node: 'FieldNode') -> str:
        """
        Returns a Verilog string that represents the field's next-state.
        This is specifically for use in Field->next property references.
        """
        assert node.implements_storage
        path = get_indexed_path(self.top_node, node)
        return f"field_combo.{path}.next"

    def get_counter_incr_identifier(self, field: 'FieldNode') -> str:
        """
        Return the Veriog string that represents the field's inferred incr/decr strobe signal.
        prop_ref will be either an incr or decr property reference, and it is already known that
        the incr/decr properties are not explicitly set by the user and are therefore inferred.
        """
        # TODO: Implement this
        raise NotImplementedError

    def get_counter_decr_identifier(self, field: 'FieldNode') -> str:
        """
        Return the Veriog string that represents the field's inferred incr/decr strobe signal.
        prop_ref will be either an incr or decr property reference, and it is already known that
        the incr/decr properties are not explicitly set by the user and are therefore inferred.
        """
        # TODO: Implement this
        raise NotImplementedError

    def get_swacc_identifier(self, field: 'FieldNode') -> str:
        """
        Asserted when field is software accessed (read)
        """
        strb = self.exp.dereferencer.get_access_strobe(field)
        return f"{strb} && !decoded_req_is_wr"

    def get_swmod_identifier(self, field: 'FieldNode') -> str:
        """
        Asserted when field is modified by software (written or read with a
        set or clear side effect).
        """
        w_modifiable = field.is_sw_writable
        r_modifiable = (field.get_property('onread') is not None)
        strb = self.exp.dereferencer.get_access_strobe(field)

        if w_modifiable and not r_modifiable:
            # assert swmod only on sw write
            return f"{strb} && decoded_req_is_wr"

        if w_modifiable and r_modifiable:
            # assert swmod on all sw actions
            return strb

        if not w_modifiable and r_modifiable:
            # assert swmod only on sw read
            return f"{strb} && !decoded_req_is_wr"

        # Not sw modifiable
        return "1'b0"


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
        Conditionals are searched in reverse order that they were registered.
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
        Conditionals are searched in reverse order that they were registered.
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

        # TODO: Add all the other things
        self.add_sw_conditional(sw_onread.ClearOnRead(self.exp), AssignmentPrecedence.SW_ONREAD)
        self.add_sw_conditional(sw_onread.SetOnRead(self.exp), AssignmentPrecedence.SW_ONREAD)

        self.add_sw_conditional(sw_onwrite.WriteOneSet(self.exp), AssignmentPrecedence.SW_ONWRITE)
        self.add_sw_conditional(sw_onwrite.WriteOneClear(self.exp), AssignmentPrecedence.SW_ONWRITE)
        self.add_sw_conditional(sw_onwrite.WriteOneToggle(self.exp), AssignmentPrecedence.SW_ONWRITE)
        self.add_sw_conditional(sw_onwrite.WriteZeroSet(self.exp), AssignmentPrecedence.SW_ONWRITE)
        self.add_sw_conditional(sw_onwrite.WriteZeroClear(self.exp), AssignmentPrecedence.SW_ONWRITE)
        self.add_sw_conditional(sw_onwrite.WriteZeroToggle(self.exp), AssignmentPrecedence.SW_ONWRITE)
        self.add_sw_conditional(sw_onwrite.WriteClear(self.exp), AssignmentPrecedence.SW_ONWRITE)
        self.add_sw_conditional(sw_onwrite.WriteSet(self.exp), AssignmentPrecedence.SW_ONWRITE)
        self.add_sw_conditional(sw_onwrite.Write(self.exp), AssignmentPrecedence.SW_ONWRITE)

        self.add_hw_conditional(hw_write.AlwaysWrite(self.exp), AssignmentPrecedence.HW_WRITE)
        self.add_hw_conditional(hw_write.WELWrite(self.exp), AssignmentPrecedence.HW_WRITE)
        self.add_hw_conditional(hw_write.WEWrite(self.exp), AssignmentPrecedence.HW_WRITE)

        self.add_hw_conditional(hw_set_clr.HWClear(self.exp), AssignmentPrecedence.HWCLR)

        self.add_hw_conditional(hw_set_clr.HWSet(self.exp), AssignmentPrecedence.HWSET)


    def _get_X_conditionals(self, conditionals: 'Dict[int, List[NextStateConditional]]', field: 'FieldNode') -> 'List[NextStateConditional]':
        result = []
        precedences = sorted(conditionals.keys(), reverse=True)
        for precedence in precedences:
            for conditional in conditionals[precedence]:
                if conditional.is_match(field):
                    result.append(conditional)
        return result


    def get_conditionals(self, field: 'FieldNode') -> 'List[NextStateConditional]':
        """
        Get a list of NextStateConditional objects that apply to the given field.

        The returned list is sorted in priority order - the conditional with highest
        precedence is first in the list.
        """
        sw_precedence = (field.get_property('precedence') == PrecedenceType.sw)
        result = []

        if sw_precedence:
            result.extend(self._get_X_conditionals(self._sw_conditionals, field))

        result.extend(self._get_X_conditionals(self._hw_conditionals, field))

        if not sw_precedence:
            result.extend(self._get_X_conditionals(self._sw_conditionals, field))

        return result
