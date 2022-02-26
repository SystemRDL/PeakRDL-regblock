from typing import TYPE_CHECKING, Union, List, Set, Dict

from systemrdl.node import AddrmapNode, Node, SignalNode, FieldNode, AddressableNode, RegNode
from systemrdl.rdltypes import PropertyReference

from ..utils import get_indexed_path

from .generators import InputStructGenerator_Hier, OutputStructGenerator_Hier
from .generators import InputStructGenerator_TypeScope, OutputStructGenerator_TypeScope

if TYPE_CHECKING:
    from ..exporter import RegblockExporter

class Hwif:
    """
    Defines how the hardware input/output signals are generated:
    - Field outputs
    - Field inputs
    - Signal inputs (except those that are promoted to the top)
    """

    def __init__(
        self, exp: 'RegblockExporter', package_name: str,
        in_hier_signal_paths: Set[str], out_of_hier_signals: Dict[str, SignalNode],
        reuse_typedefs: bool
    ):
        self.exp = exp
        self.package_name = package_name

        self.has_input_struct = False
        self.has_output_struct = False

        self.in_hier_signal_paths = in_hier_signal_paths
        self.out_of_hier_signals = out_of_hier_signals

        if reuse_typedefs:
            self._gen_in_cls = InputStructGenerator_TypeScope
            self._gen_out_cls = OutputStructGenerator_TypeScope
        else:
            self._gen_in_cls = InputStructGenerator_Hier
            self._gen_out_cls = OutputStructGenerator_Hier

    @property
    def top_node(self) -> AddrmapNode:
        return self.exp.top_node


    def get_package_contents(self) -> str:
        """
        If this hwif requires a package, generate the string
        """
        lines = []

        gen_in = self._gen_in_cls(self)
        structs_in = gen_in.get_struct(
            self.top_node,
            f"{self.top_node.inst_name}__in_t"
        )
        if structs_in is not None:
            self.has_input_struct = True
            lines.append(structs_in)
        else:
            self.has_input_struct = False

        gen_out = self._gen_out_cls(self)
        structs_out = gen_out.get_struct(
            self.top_node,
            f"{self.top_node.inst_name}__out_t"
        )
        if structs_out is not None:
            self.has_output_struct = True
            lines.append(structs_out)
        else:
            self.has_output_struct = False

        return "\n\n".join(lines)


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
            type_name = f"{self.top_node.inst_name}__in_t"
            lines.append(f"input {self.package_name}::{type_name} hwif_in")
        if self.has_output_struct:
            type_name = f"{self.top_node.inst_name}__out_t"
            lines.append(f"output {self.package_name}::{type_name} hwif_out")

        return ",\n".join(lines)

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
            next_value = obj.get_property('next')
            if next_value is not None:
                # 'next' property replaces the inferred input signal
                return self.exp.dereferencer.get_value(next_value)
            # Otherwise, use inferred
            path = get_indexed_path(self.top_node, obj)
            return "hwif_in." + path + ".next"
        elif isinstance(obj, SignalNode):
            if obj.get_path() in self.out_of_hier_signals:
                return obj.inst_name
            path = get_indexed_path(self.top_node, obj)
            return "hwif_in." + path
        elif isinstance(obj, PropertyReference):
            return self.get_implied_prop_input_identifier(obj.node, obj.name)

        raise RuntimeError(f"Unhandled reference to: {obj}")


    def get_implied_prop_input_identifier(self, field: FieldNode, prop: str) -> str:
        assert prop in {
            'hwclr', 'hwset', 'swwe', 'swwel', 'we', 'wel',
            'incr', 'decr', 'incrvalue', 'decrvalue'
        }
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

        raise RuntimeError(f"Unhandled reference to: {obj}")


    def get_implied_prop_output_identifier(self, node: Union[FieldNode, RegNode], prop: str) -> str:
        if isinstance(node, FieldNode):
            assert prop in {
                "anded", "ored", "xored", "swmod", "swacc",
                "incrthreshold", "decrthreshold", "overflow", "underflow",
            }
        elif isinstance(node, RegNode):
            assert prop in {
                "intr", "halt",
            }
        path = get_indexed_path(self.top_node, node)
        return "hwif_out." + path + "." + prop
