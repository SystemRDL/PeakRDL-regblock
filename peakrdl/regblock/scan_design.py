from typing import TYPE_CHECKING
from collections import OrderedDict

from systemrdl.walker import RDLListener, RDLWalker
from systemrdl.node import AddrmapNode, SignalNode

if TYPE_CHECKING:
    from systemrdl.node import Node, RegNode, MemNode, FieldNode
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

        # Collections of signals that were actually referenced by the design
        self.in_hier_signal_paths = set()
        self.out_of_hier_signals = OrderedDict()

    def _get_out_of_hier_field_reset(self):
        current_node = self.exp.top_node.parent
        while current_node is not None:
            for signal in current_node.signals():
                if signal.get_property('field_reset'):
                    path = signal.get_path()
                    self.out_of_hier_signals[path] = signal
                    return
            current_node = current_node.parent

    def do_scan(self):
        # Collect cpuif reset, if any.
        cpuif_reset = self.exp.top_node.cpuif_reset
        if cpuif_reset is not None:
            path = cpuif_reset.get_path()
            rel_path = cpuif_reset.get_rel_path(self.exp.top_node)
            if rel_path.startswith("^"):
                self.out_of_hier_signals[path] = cpuif_reset
            else:
                self.in_hier_signal_paths.add(path)

        # collect out-of-hier field_reset, if any
        self._get_out_of_hier_field_reset()

        RDLWalker().walk(self.exp.top_node, self)
        if self.msg.had_error:
            self.msg.fatal(
                "Unable to export due to previous errors"
            )
            raise ValueError

    def enter_Reg(self, node: 'RegNode') -> None:
        # The CPUIF's bus width is sized according to the largest register in the design
        self.cpuif_data_width = max(self.cpuif_data_width, node.get_property('regwidth'))

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

        if node.get_property('field_reset'):
            path = node.get_path()
            self.in_hier_signal_paths.add(path)

    def enter_Field(self, node: 'FieldNode') -> None:
        for prop_name in node.list_properties():
            value = node.get_property(prop_name)
            if isinstance(value, SignalNode):
                path = value.get_path()
                rel_path = value.get_rel_path(self.exp.top_node)
                if rel_path.startswith("^"):
                    self.out_of_hier_signals[path] = value
                else:
                    self.in_hier_signal_paths.add(path)

    def enter_Mem(self, node: 'MemNode') -> None:
        self.msg.error(
            "Cannot export a register block that contains a memory",
            node.inst.inst_src_ref
        )
