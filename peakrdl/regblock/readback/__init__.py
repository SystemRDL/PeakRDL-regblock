from typing import TYPE_CHECKING

from .generators import ReadbackAssignmentGenerator
from ..utils import get_always_ff_event

if TYPE_CHECKING:
    from ..exporter import RegblockExporter
    from systemrdl.node import AddrmapNode

class Readback:
    def __init__(self, exp:'RegblockExporter'):
        self.exp = exp

    @property
    def top_node(self) -> 'AddrmapNode':
        return self.exp.top_node

    def get_implementation(self) -> str:
        gen = ReadbackAssignmentGenerator(self.exp)
        array_assignments = gen.get_content(self.top_node)

        context = {
            "array_assignments" : array_assignments,
            "array_size" : gen.current_offset,
            "get_always_ff_event": get_always_ff_event,
            "cpuif_reset": self.exp.cpuif_reset,
        }
        template = self.exp.jj_env.get_template(
            "readback/templates/readback.sv"
        )
        return template.render(context)
