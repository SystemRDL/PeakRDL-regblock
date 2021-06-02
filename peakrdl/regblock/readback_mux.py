import re
from typing import TYPE_CHECKING, List

from systemrdl.node import Node, AddressableNode, RegNode


if TYPE_CHECKING:
    from .exporter import RegblockExporter

class ReadbackMux:
    def __init__(self, exporter:'RegblockExporter', top_node:AddressableNode):
        self.exporter = exporter
        self.top_node = top_node

        self._indent_level = 0


    def get_implementation(self) -> str:
        # TODO: Count the number of readable registers
        # TODO: Emit the declaration for the readback array
        # TODO: Always comb block to assign & mask all elements
        # TODO: Separate always_comb block to OR reduce down
        return "//TODO"


    #---------------------------------------------------------------------------
    @property
    def _indent(self) -> str:
        return "    " * self._indent_level
