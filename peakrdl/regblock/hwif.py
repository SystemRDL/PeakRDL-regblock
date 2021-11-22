from typing import TYPE_CHECKING, Union, List

from systemrdl.node import AddrmapNode, Node, SignalNode, FieldNode, AddressableNode
from systemrdl.rdltypes import PropertyReference

from .utils import get_indexed_path

if TYPE_CHECKING:
    from .exporter import RegblockExporter

class Hwif:
    """
    Defines how the hardware input/output signals are generated:
    - Field outputs
    - Field inputs
    - Signal inputs (except those that are promoted to the top)
    """

    def __init__(self, exp: 'RegblockExporter', package_name: str):
        self.exp = exp
        self.package_name = package_name

        self.has_input_struct = None
        self.has_output_struct = None
        self._indent_level = 0

    @property
    def top_node(self) -> AddrmapNode:
        return self.exp.top_node


    def get_package_contents(self) -> str:
        """
        If this hwif requires a package, generate the string
        """
        lines = []

        self.has_input_struct = self._do_struct_addressable(lines, self.top_node, is_input=True)
        self.has_output_struct = self._do_struct_addressable(lines, self.top_node, is_input=False)

        return "\n".join(lines)


    @property
    def port_declaration(self) -> str:
        """
        Returns the declaration string for all I/O ports in the hwif group
        """

        # Assume get_package_declaration() is always called prior to this
        assert self.has_input_struct is not None
        assert self.has_output_struct is not None

        lines = []
        if self.has_input_struct:
            lines.append(f"input {self.package_name}::{self._get_struct_name(self.top_node, is_input=True)} hwif_in")
        if self.has_output_struct:
            lines.append(f"output {self.package_name}::{self._get_struct_name(self.top_node, is_input=False)} hwif_out")

        return ",\n".join(lines)


    #---------------------------------------------------------------------------
    # Struct generation functions
    #---------------------------------------------------------------------------
    @property
    def _indent(self) -> str:
        return "    " * self._indent_level

    def _get_node_array_suffix(self, node:AddressableNode) -> str:
        if node.is_array:
            return "".join([f'[{dim}]' for dim in node.array_dimensions])
        return ""

    def _get_struct_name(self, node:Node, is_input:bool = True) -> str:
        base = node.get_rel_path(
            self.top_node.parent,
            hier_separator="__",
            array_suffix="x",
            empty_array_suffix="x"
        )
        if is_input:
            return f'{base}__in_t'
        return f'{base}__out_t'

    def _do_struct_addressable(self, lines:list, node:AddressableNode, is_input:bool = True) -> bool:

        struct_children = []

        # Generate structs for children first
        for child in node.children():
            if isinstance(child, AddressableNode):
                if self._do_struct_addressable(lines, child, is_input):
                    struct_children.append(child)
            elif isinstance(child, FieldNode):
                if self._do_struct_field(lines, child, is_input):
                    struct_children.append(child)
            elif is_input and isinstance(child, SignalNode):
                # No child struct needed here
                # TODO: Skip if this is a top-level child
                struct_children.append(child)

        # Generate this addressable node's struct
        if struct_children:
            lines.append("")
            lines.append(f"{self._indent}// {node.get_rel_path(self.top_node.parent)}")
            lines.append(f"{self._indent}typedef struct {{")
            self._indent_level += 1
            for child in struct_children:
                if isinstance(child, AddressableNode):
                    lines.append(f"{self._indent}{self._get_struct_name(child, is_input)} {child.inst_name}{self._get_node_array_suffix(child)};")
                elif isinstance(child, FieldNode):
                    lines.append(f"{self._indent}{self._get_struct_name(child, is_input)} {child.inst_name};")
                elif isinstance(child, SignalNode):
                    if child.width == 1:
                        lines.append(f"{self._indent}logic {child.inst_name};")
                    else:
                        lines.append(f"{self._indent}logic [{child.msb}:{child.lsb}] {child.inst_name};")

            self._indent_level -= 1
            lines.append(f"{self._indent}}} {self._get_struct_name(node, is_input)};")

        return bool(struct_children)

    def _do_struct_field(self, lines:list, node:FieldNode, is_input:bool = True) -> bool:
        contents = []

        if is_input:
            contents = self._get_struct_input_field_contents(node)
        else:
            contents = self._get_struct_output_field_contents(node)

        if contents:
            lines.append("")
            lines.append(f"{self._indent}// {node.get_rel_path(self.top_node.parent)}")
            lines.append(f"{self._indent}typedef struct {{")
            self._indent_level += 1
            for member in contents:
                lines.append(self._indent + member)
            self._indent_level -= 1
            lines.append(f"{self._indent}}} {self._get_struct_name(node, is_input)};")

        return bool(contents)

    def _get_struct_input_field_contents(self, node:FieldNode) -> List[str]:
        contents = []

        # Provide input to field's value if it is writable by hw
        if self.has_value_input(node):
            if node.width == 1:
                contents.append("logic value;")
            else:
                contents.append(f"logic [{node.width-1}:0] value;")

        # Generate implied inputs
        for prop_name in ["we", "wel", "swwe", "swwel", "hwclr", "hwset"]:
            # if property is boolean and true, implies a corresponding input signal on the hwif
            if node.get_property(prop_name) is True:
                contents.append(f"logic {prop_name};")

        # Generate any implied counter inputs
        if node.get_property('counter'):
            if not node.get_property('incr'):
                # User did not provide their own incr component reference.
                # Imply an input
                contents.append("logic incr;")
            if not node.get_property('decr'):
                # User did not provide their own decr component reference.
                # Imply an input
                contents.append("logic decr;")

            width = node.get_property('incrwidth')
            if width:
                # Implies a corresponding incrvalue input
                contents.append(f"logic [{width-1}:0] incrvalue;")

            width = node.get_property('decrwidth')
            if width:
                # Implies a corresponding decrvalue input
                contents.append(f"logic [{width-1}:0] decrvalue;")

        # TODO:
        """
        signals!
            any signal instances instantiated in the scope
        """

        return contents

    def _get_struct_output_field_contents(self, node:FieldNode) -> List[str]:
        contents = []

        # Expose field's value if it is readable by hw
        if self.has_value_output(node):
            if node.width == 1:
                contents.append("logic value;")
            else:
                contents.append(f"logic [{node.width-1}:0] value;")

        # Generate output bit signals enabled via property
        for prop_name in ["anded", "ored", "xored", "swmod", "swacc"]:
            if node.get_property(prop_name):
                contents.append(f"logic {prop_name};")

        return contents

    #---------------------------------------------------------------------------
    # hwif utility functions
    #---------------------------------------------------------------------------
    def has_value_input(self, obj: Union[FieldNode, SignalNode]) -> bool:
        """
        Returns True if the object infers an input wire in the hwif
        """
        if isinstance(obj, FieldNode):
            return obj.is_hw_writable
        elif isinstance(obj, SignalNode):
            # Signals are implicitly always inputs
            return True
        else:
            raise RuntimeError


    def has_value_output(self, obj: FieldNode) -> bool:
        """
        Returns True if the object infers an output wire in the hwif
        """
        return obj.is_hw_readable


    def get_input_identifier(self, obj: Union[FieldNode, SignalNode, PropertyReference]) -> str:
        """
        Returns the identifier string that best represents the input object.

        if obj is:
            Field: the fields hw input value port
            Signal: signal input value
            Prop reference:
                could be an implied hwclr/hwset/swwe/swwel/we/wel input

        raises an exception if obj is invalid
        """
        if isinstance(obj, FieldNode):
            path = get_indexed_path(self.top_node, obj)
            return "hwif_in." + path + ".value"
        elif isinstance(obj, SignalNode):
            # TODO: Implement this
            raise NotImplementedError()
        elif isinstance(obj, PropertyReference):
            return self.get_implied_prop_input_identifier(obj.node, obj.name)

        raise RuntimeError("Unhandled reference to: %s", obj)


    def get_implied_prop_input_identifier(self, field: FieldNode, prop: str) -> str:
        assert prop in {'hwclr', 'hwset', 'swwe', 'swwel', 'we', 'wel'}
        path = get_indexed_path(self.top_node, field)
        return "hwif_in." + path + "." + prop


    def get_output_identifier(self, obj: Union[FieldNode, PropertyReference]) -> str:
        """
        Returns the identifier string that best represents the output object.

        if obj is:
            Field: the fields hw output value port
            Property ref: this is also part of the struct

        raises an exception if obj is invalid
        """
        if isinstance(obj, FieldNode):
            path = get_indexed_path(self.top_node, obj)
            return "hwif_out." + path + ".value"
        elif isinstance(obj, PropertyReference):
            # TODO: this might be dead code.
            # not sure when anything would call this function with a prop ref
            # when dereferencer's get_value is more useful here
            assert obj.node.get_property(obj.name)
            return self.get_implied_prop_output_identifier(obj.node, obj.name)

        raise RuntimeError("Unhandled reference to: %s", obj)


    def get_implied_prop_output_identifier(self, field: FieldNode, prop: str) -> str:
        assert prop in {"anded", "ored", "xored", "swmod", "swacc"}
        path = get_indexed_path(self.top_node, field)
        return "hwif_out." + path + "." + prop
