from typing import TYPE_CHECKING, Set, Optional, Type, List
from collections import OrderedDict

from systemrdl.walker import RDLListener, RDLWalker, WalkerAction
from systemrdl.node import SignalNode, RegNode

if TYPE_CHECKING:
    from systemrdl.node import Node, FieldNode, AddressableNode
    from .exporter import RegblockExporter
    from systemrdl.rdltypes import UserEnum


class DesignScanner(RDLListener):
    """
    Scans through the register model and validates that any unsupported features
    are not present.

    Also collects any information that is required prior to the start of the export process.
    """
    def __init__(self, exp:'RegblockExporter') -> None:
        self.exp = exp
        self.cpuif_data_width = 0
        self.msg = exp.top_node.env.msg

        # Collections of signals that were actually referenced by the design
        self.in_hier_signal_paths = set() # type: Set[str]
        self.out_of_hier_signals = OrderedDict() # type: OrderedDict[str, SignalNode]

        self.has_writable_msb0_fields = False
        self.has_buffered_write_regs = False
        self.has_buffered_read_regs = False

        self.has_external_block = False
        self.has_external_addressable = False

        # Track any referenced enums
        self.user_enums = [] # type: List[Type[UserEnum]]

    def _get_out_of_hier_field_reset(self) -> None:
        current_node = self.exp.top_node.parent
        while current_node is not None:
            for signal in current_node.signals():
                if signal.get_property('field_reset'):
                    path = signal.get_path()
                    self.out_of_hier_signals[path] = signal
                    return
            current_node = current_node.parent

    def do_scan(self) -> None:
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

        # Ensure addrmap is not a bridge. This concept does not make sense for
        # terminal components.
        if self.exp.top_node.get_property('bridge'):
            self.msg.error(
                "Regblock generator does not support exporting bridge address maps",
                self.exp.top_node.inst.property_src_ref.get('bridge', self.exp.top_node.inst.inst_src_ref)
            )

        RDLWalker().walk(self.exp.top_node, self)
        if self.msg.had_error:
            self.msg.fatal(
                "Unable to export due to previous errors"
            )

    def enter_Component(self, node: 'Node') -> Optional[WalkerAction]:
        if node.external and (node != self.exp.top_node):
            # Do not inspect external components. None of my business
            return WalkerAction.SkipDescendants

        # Collect any signals that are referenced by a property
        for prop_name in node.list_properties():
            value = node.get_property(prop_name)
            if isinstance(value, SignalNode):
                path = value.get_path()
                rel_path = value.get_rel_path(self.exp.top_node)
                if rel_path.startswith("^"):
                    self.out_of_hier_signals[path] = value
                else:
                    self.in_hier_signal_paths.add(path)

            if prop_name == "encode":
                if value not in self.user_enums:
                    self.user_enums.append(value)

        return WalkerAction.Continue

    def enter_AddressableComponent(self, node: 'AddressableNode') -> None:
        if node.external and node != self.exp.top_node:
            self.has_external_addressable = True
            if not isinstance(node, RegNode):
                self.has_external_block = True

    def enter_Reg(self, node: 'RegNode') -> None:
        # The CPUIF's bus width is sized according to the largest accesswidth in the design
        accesswidth = node.get_property('accesswidth')
        self.cpuif_data_width = max(self.cpuif_data_width, accesswidth)

        self.has_buffered_write_regs = self.has_buffered_write_regs or bool(node.get_property('buffer_writes'))
        self.has_buffered_read_regs = self.has_buffered_read_regs or bool(node.get_property('buffer_reads'))

    def enter_Signal(self, node: 'SignalNode') -> None:
        if node.get_property('field_reset'):
            path = node.get_path()
            self.in_hier_signal_paths.add(path)

    def enter_Field(self, node: 'FieldNode') -> None:
        if node.is_sw_writable and (node.msb < node.lsb):
            self.has_writable_msb0_fields = True
