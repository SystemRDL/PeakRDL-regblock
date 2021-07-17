from typing import TYPE_CHECKING

from systemrdl.node import AddrmapNode, FieldNode
from systemrdl.rdltypes import PropertyReference

from ..utils import get_indexed_path
from .field_builder import FieldBuilder, FieldStorageStructGenerator
from .field_builder import CombinationalStructGenerator, FieldLogicGenerator


if TYPE_CHECKING:
    from ..exporter import RegblockExporter

class FieldLogic:
    def __init__(self, exporter:'RegblockExporter'):
        self.exporter = exporter
        self.field_builder = FieldBuilder(exporter)

    @property
    def top_node(self) -> AddrmapNode:
        return self.exporter.top_node

    def get_storage_struct(self) -> str:
        struct_gen = FieldStorageStructGenerator()
        s = struct_gen.get_struct(self.top_node, "field_storage_t")

        # Only declare the storage struct if it exists
        if s is None:
            return ""

        return s + "\nfield_storage_t field_storage;"

    def get_combo_struct(self) -> str:
        struct_gen = CombinationalStructGenerator(self.field_builder)
        s = struct_gen.get_struct(self.top_node, "field_combo_t")

        # Only declare the storage struct if it exists
        if s is None:
            return ""

        return s + "\nfield_combo_t field_combo;"

    def get_implementation(self) -> str:
        gen = FieldLogicGenerator(self.field_builder)
        s = gen.get_content(self.top_node)
        if s is None:
            return ""
        return s

    #---------------------------------------------------------------------------
    # Field utility functions
    #---------------------------------------------------------------------------
    def get_storage_identifier(self, node: FieldNode) -> str:
        """
        Returns the Verilog string that represents the storage register element
        for the referenced field
        """
        assert node.implements_storage
        path = get_indexed_path(self.top_node, node)
        return "field_storage." + path

    def get_field_next_identifier(self, node: FieldNode) -> str:
        """
        Returns a Verilog string that represents the field's next-state.
        This is specifically for use in Field->next property references.
        """
        # TODO: Implement this
        raise NotImplementedError

    def get_counter_control_identifier(self, prop_ref: PropertyReference) -> str:
        """
        Return the Veriog string that represents the field's inferred incr/decr strobe signal.
        prop_ref will be either an incr or decr property reference, and it is already known that
        the incr/decr properties are not explicitly set by the user and are therefore inferred.
        """
        # TODO: Implement this
        raise NotImplementedError
