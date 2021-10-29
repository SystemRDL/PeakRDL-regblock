import re
from typing import TYPE_CHECKING, List

from systemrdl.node import AddrmapNode


if TYPE_CHECKING:
    from .exporter import RegblockExporter

class ReadbackMux:
    def __init__(self, exp:'RegblockExporter'):
        self.exp = exp

    @property
    def top_node(self) -> AddrmapNode:
        return self.exp.top_node

    def get_implementation(self) -> str:
        # TODO: Count the number of readable registers
        # TODO: Emit the declaration for the readback array
        # TODO: Always comb block to assign & mask all elements
        # TODO: Separate always_comb block to OR reduce down
        return "//TODO"
