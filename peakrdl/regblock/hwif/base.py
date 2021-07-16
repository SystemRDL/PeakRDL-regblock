from typing import TYPE_CHECKING, Union
from systemrdl.node import Node, SignalNode, FieldNode
from systemrdl.rdltypes import AccessType, PropertyReference

if TYPE_CHECKING:
    from ..exporter import RegblockExporter

class HwifBase:
    """
    Defines how the hardware input/output signals are generated:
    - Field outputs
    - Field inputs
    - Signal inputs (except those that are promoted to the top)
    """

    def __init__(self, exporter: 'RegblockExporter', top_node: Node, package_name: str):
        self.exporter = exporter
        self.top_node = top_node
        self.package_name = package_name


    def get_package_declaration(self) -> str:
        """
        If this hwif requires a package, generate the string
        """
        return ""


    @property
    def port_declaration(self) -> str:
        """
        Returns the declaration string for all I/O ports in the hwif group
        """
        raise NotImplementedError()

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
        # TODO: Extend this for signals and prop references?
        return obj.is_hw_readable


    def get_input_identifier(self, obj: Union[FieldNode, SignalNode, PropertyReference]) -> str:
        """
        Returns the identifier string that best represents the input object.

        if obj is:
            Field: the fields input value port
            Signal: signal input value
            Prop reference:
                could be an implied hwclr/hwset/swwe/swwel/we/wel input
                Raise a runtime error if an illegal prop ref is requested, or if
                the prop ref is not actually implied, but explicitly ref a component

        TODO: finish this
        raises an exception if obj is invalid
        """
        raise NotImplementedError()


    def get_output_identifier(self, obj: FieldNode) -> str:
        """
        Returns the identifier string that best represents the output object.

        if obj is:
            Field: the fields output value port
            Property ref: this is also part of the struct
            TODO: finish this

        raises an exception if obj is invalid
        """
        raise NotImplementedError()
