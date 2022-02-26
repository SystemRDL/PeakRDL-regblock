from typing import TYPE_CHECKING

from systemrdl.node import FieldNode

from ..struct_generator import RDLFlatStructGenerator

if TYPE_CHECKING:
    from systemrdl.node import Node, SignalNode, RegNode
    from . import Hwif

class InputStructGenerator_Hier(RDLFlatStructGenerator):
    def __init__(self, hwif: 'Hwif') -> None:
        super().__init__()
        self.hwif = hwif
        self.top_node = hwif.top_node

    def get_typdef_name(self, node:'Node') -> str:
        base = node.get_rel_path(
            self.top_node.parent,
            hier_separator="__",
            array_suffix="x",
            empty_array_suffix="x"
        )
        return f'{base}__in_t'

    def enter_Signal(self, node: 'SignalNode') -> None:
        # only emit the signal if design scanner detected it is actually being used
        path = node.get_path()
        if path in self.hwif.in_hier_signal_paths:
            self.add_member(node.inst_name, node.width)

    def enter_Field(self, node: 'FieldNode') -> None:
        type_name = self.get_typdef_name(node)
        self.push_struct(type_name, node.inst_name)

        # Provide input to field's next value if it is writable by hw, and it
        # was not overridden by the 'next' property
        if node.is_hw_writable and node.get_property('next') is None:
            self.add_member("next", node.width)

        # Generate implied inputs
        for prop_name in ["we", "wel", "swwe", "swwel", "hwclr", "hwset"]:
            # if property is boolean and true, implies a corresponding input signal on the hwif
            if node.get_property(prop_name) is True:
                self.add_member(prop_name)

        # Generate any implied counter inputs
        if node.is_up_counter:
            if not node.get_property('incr'):
                # User did not provide their own incr component reference.
                # Imply an input
                self.add_member('incr')

            width = node.get_property('incrwidth')
            if width:
                # Implies a corresponding incrvalue input
                self.add_member('incrvalue', width)

        if node.is_down_counter:
            if not node.get_property('decr'):
                # User did not provide their own decr component reference.
                # Imply an input
                self.add_member('decr')

            width = node.get_property('decrwidth')
            if width:
                # Implies a corresponding decrvalue input
                self.add_member('decrvalue', width)

    def exit_Field(self, node: 'FieldNode') -> None:
        self.pop_struct()


class OutputStructGenerator_Hier(RDLFlatStructGenerator):
    def __init__(self, top_node: 'Node'):
        super().__init__()
        self.top_node = top_node

    def get_typdef_name(self, node:'Node') -> str:
        base = node.get_rel_path(
            self.top_node.parent,
            hier_separator="__",
            array_suffix="x",
            empty_array_suffix="x"
        )
        return f'{base}__out_t'

    def enter_Field(self, node: 'FieldNode') -> None:
        type_name = self.get_typdef_name(node)
        self.push_struct(type_name, node.inst_name)

        # Expose field's value if it is readable by hw
        if node.is_hw_readable:
            self.add_member("value", node.width)

        # Generate output bit signals enabled via property
        for prop_name in ["anded", "ored", "xored", "swmod", "swacc", "overflow", "underflow"]:
            if node.get_property(prop_name):
                self.add_member(prop_name)

        if node.get_property('incrthreshold') is not False: # (explicitly not False. Not 0)
            self.add_member('incrthreshold')
        if node.get_property('decrthreshold') is not False: # (explicitly not False. Not 0)
            self.add_member('decrthreshold')

    def exit_Field(self, node: 'FieldNode') -> None:
        self.pop_struct()

    def exit_Reg(self, node: 'RegNode') -> None:
        if node.is_interrupt_reg:
            self.add_member('intr')
            if node.is_halt_reg:
                self.add_member('halt')
        super().exit_Reg(node)

#-------------------------------------------------------------------------------
class InputStructGenerator_TypeScope(InputStructGenerator_Hier):
    def get_typdef_name(self, node:'Node') -> str:
        scope_path = node.inst.get_scope_path("__")
        if scope_path is None:
            # Unable to determine a reusable type name. Fall back to hierarchical path
            # Add prefix to prevent collision when mixing namespace methods
            scope_path = "xtern__" + super().get_typdef_name(node)

        if isinstance(node, FieldNode):
            extra_suffix = get_field_type_name_suffix(node)
        else:
            extra_suffix = ""

        return f'{scope_path}__{node.type_name}{extra_suffix}__in_t'

class OutputStructGenerator_TypeScope(OutputStructGenerator_Hier):
    def get_typdef_name(self, node:'Node') -> str:
        scope_path = node.inst.get_scope_path("__")
        if scope_path is None:
            # Unable to determine a reusable type name. Fall back to hierarchical path
            # Add prefix to prevent collision when mixing namespace methods
            scope_path = "xtern__" + super().get_typdef_name(node)

        if isinstance(node, FieldNode):
            extra_suffix = get_field_type_name_suffix(node)
        else:
            extra_suffix = ""

        return f'{scope_path}__{node.type_name}{extra_suffix}__out_t'


def get_field_type_name_suffix(field: FieldNode) -> str:
    """
    Fields may reuse the same type, but end up instantiating different widths
    Uniquify the type name further if the field width was overridden when instantiating
    """
    if field.inst.original_def is None:
        return ""

    if field.inst.original_def.type_name is None:
        # is an anonymous definition. No extra suffix needed
        return ""

    if "fieldwidth" in field.list_properties():
        # fieldwidth was explicitly set. This type name is already sufficiently distinct
        return ""

    if field.width == 1:
        # field width is the default. Skip suffix
        return ""

    return f"_w{field.width}"
