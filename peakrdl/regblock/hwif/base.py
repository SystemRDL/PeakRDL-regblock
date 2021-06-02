from typing import TYPE_CHECKING, Union
from systemrdl.node import Node, SignalNode, FieldNode
from systemrdl.rdltypes import AccessType

if TYPE_CHECKING:
    from ..exporter import RegblockExporter

class HwifBase:
    """
    Defines how the hardware input/output signals are generated:
    - Field outputs
    - Field inputs
    - Signal inputs (except those that are promoted to the top)
    """

    def __init__(self, exporter:'RegblockExporter', top_node:'Node', package_name:str):
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
            return obj.get_property("hw") in {AccessType.rw, AccessType.w}
        elif isinstance(obj, SignalNode):
            raise NotImplementedError # TODO:
        else:
            raise RuntimeError


    def has_value_output(self, obj: FieldNode) -> bool:
        """
        Returns True if the object infers an output wire in the hwif
        """
        return obj.get_property("hw") in {AccessType.rw, AccessType.r}


    def get_input_identifier(self, obj) -> str:
        """
        Returns the identifier string that best represents the input object.

        if obj is:
            Field: the fields input value port
            Signal: signal input value
            TODO: finish this

        raises an exception if obj is invalid
        """
        raise NotImplementedError()


    def get_output_identifier(self, obj) -> str:
        """
        Returns the identifier string that best represents the output object.

        if obj is:
            Field: the fields output value port
            TODO: finish this

        raises an exception if obj is invalid
        """
        raise NotImplementedError()
