from typing import TYPE_CHECKING, Optional, List, Type

from systemrdl.node import FieldNode

from ..struct_generator import RDLFlatStructGenerator
from ..identifier_filter import kw_filter as kwf

if TYPE_CHECKING:
    from systemrdl.node import Node, SignalNode, RegNode
    from . import Hwif
    from systemrdl.rdltypes import UserEnum

class HWIFStructGenerator(RDLFlatStructGenerator):
    def __init__(self, hwif: 'Hwif', hwif_name: str) -> None:
        super().__init__()
        self.hwif = hwif
        self.top_node = hwif.top_node

        self.hwif_report_stack = [hwif_name]

    def push_struct(self, type_name: str, inst_name: str, array_dimensions: Optional[List[int]] = None) -> None: # type: ignore
        super().push_struct(type_name, inst_name, array_dimensions)

        if array_dimensions:
            array_suffix = "".join([f"[0:{dim-1}]" for dim in array_dimensions])
            segment = inst_name + array_suffix
        else:
            segment = inst_name
        self.hwif_report_stack.append(segment)

    def pop_struct(self) -> None:
        super().pop_struct()
        self.hwif_report_stack.pop()

    def add_member(self, name: str, width: int = 1) -> None: # type: ignore # pylint: disable=arguments-differ
        super().add_member(name, width)

        if width > 1:
            suffix = f"[{width-1}:0]"
        else:
            suffix = ""

        path = ".".join(self.hwif_report_stack)
        if self.hwif.hwif_report_file:
            self.hwif.hwif_report_file.write(f"{path}.{name}{suffix}\n")

#-------------------------------------------------------------------------------

class InputStructGenerator_Hier(HWIFStructGenerator):
    def __init__(self, hwif: 'Hwif') -> None:
        super().__init__(hwif, "hwif_in")

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
            self.add_member(kwf(node.inst_name), node.width)

    def enter_Field(self, node: 'FieldNode') -> None:
        type_name = self.get_typdef_name(node)
        self.push_struct(type_name, kwf(node.inst_name))

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


class OutputStructGenerator_Hier(HWIFStructGenerator):
    def __init__(self, hwif: 'Hwif') -> None:
        super().__init__(hwif, "hwif_out")

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
        self.push_struct(type_name, kwf(node.inst_name))

        # Expose field's value if it is readable by hw
        if node.is_hw_readable:
            self.add_member("value", node.width)

        # Generate output bit signals enabled via property
        for prop_name in ["anded", "ored", "xored", "swmod", "swacc", "overflow", "underflow", "rd_swacc", "wr_swacc"]:
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

#-------------------------------------------------------------------------------
class EnumGenerator:
    """
    Generator for user-defined enum definitions
    """

    def get_enums(self, user_enums: List[Type['UserEnum']]) -> Optional[str]:
        if not user_enums:
            return None

        lines = []
        for user_enum in user_enums:
            lines.append(self._enum_typedef(user_enum))

        return '\n\n'.join(lines)

    @staticmethod
    def _get_prefix(user_enum: Type['UserEnum']) -> str:
        scope = user_enum.get_scope_path("__")
        if scope:
            return f"{scope}__{user_enum.type_name}"
        else:
            return user_enum.type_name

    def _enum_typedef(self, user_enum: Type['UserEnum']) -> str:
        prefix = self._get_prefix(user_enum)

        lines = []
        for enum_member in user_enum:
            lines.append(f"    {prefix}__{enum_member.name} = 'd{enum_member.value}")

        return (
            "typedef enum {\n"
            + ",\n".join(lines)
            + f"\n}} {prefix}_e;"
        )


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
