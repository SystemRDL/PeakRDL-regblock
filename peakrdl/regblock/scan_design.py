from typing import TYPE_CHECKING

from systemrdl.walker import RDLListener
from systemrdl.node import AddrmapNode

if TYPE_CHECKING:
    from systemrdl.node import Node, RegNode, SignalNode, MemNode
    from .exporter import RegblockExporter


class DesignScanner(RDLListener):
    """
    Scans through the register model and validates that any unsupported features
    are not present.

    Also collects any information that is required prior to the start of the export process.
    """
    def __init__(self, exp:'RegblockExporter'):
        self.exp = exp
        self.cpuif_data_width = 0
        self.msg = exp.top_node.env.msg

    def enter_Reg(self, node: 'RegNode') -> None:
        # The CPUIF's bus width is sized according to the largest register in the design
        self.cpuif_data_width = max(self.cpuif_data_width, node.get_property('regwidth'))

    # TODO: Collect any references to signals that lie outside of the hierarchy
    # These will be added as top-level signals

    def enter_Component(self, node: 'Node') -> None:
        if not isinstance(node, AddrmapNode) and node.external:
            self.msg.error(
                "Exporter does not support external components",
                node.inst.inst_src_ref
            )

    def enter_Signal(self, node: 'SignalNode') -> None:
        # If encountering a CPUIF reset that is nested within the register model,
        # warn that it will be ignored.
        # Only cpuif resets in the top-level node or above will be honored
        if node.get_property('cpuif_reset') and (node.parent != self.exp.top_node):
            self.msg.warning(
                "Only cpuif_reset signals that are instantiated in the top-level "
                + "addrmap or above will be honored. Any cpuif_reset signals nested "
                + "within children of the addrmap being exported will be ignored.",
                node.inst.inst_src_ref
            )

    def enter_Mem(self, node: 'MemNode') -> None:
        self.msg.error(
            "Cannot export a register block that contains a memory",
            node.inst.inst_src_ref
        )
