from typing import TYPE_CHECKING, Set, List
from collections import OrderedDict

from systemrdl.walker import RDLListener, RDLWalker
from systemrdl.node import SignalNode, AddressableNode

if TYPE_CHECKING:
    from systemrdl.node import Node, RegNode, FieldNode
    from .exporter import RegblockExporter


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

        # Keep track of max regwidth encountered in a given block
        self.max_regwidth_stack = [] # type: List[int]

        # Collections of signals that were actually referenced by the design
        self.in_hier_signal_paths = set() # type: Set[str]
        self.out_of_hier_signals = OrderedDict() # type: OrderedDict[str, SignalNode]

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
            raise ValueError

    def enter_Reg(self, node: 'RegNode') -> None:
        regwidth = node.get_property('regwidth')

        self.max_regwidth_stack[-1] = max(self.max_regwidth_stack[-1], regwidth)

        # The CPUIF's bus width is sized according to the largest register in the design
        # TODO: make this user-overridable once more flexible regwidth/accesswidths are supported
        self.cpuif_data_width = max(self.cpuif_data_width, regwidth)

        # TODO: remove this limitation eventually
        if regwidth != self.cpuif_data_width:
            self.msg.error(
                "register blocks with non-uniform regwidths are not supported yet",
                node.inst.property_src_ref.get('regwidth', node.inst.inst_src_ref)
            )

        # TODO: remove this limitation eventually
        if regwidth != node.get_property('accesswidth'):
            self.msg.error(
                "Registers that have an accesswidth different from the register width are not supported yet",
                node.inst.property_src_ref.get('accesswidth', node.inst.inst_src_ref)
            )

    def enter_AddressableComponent(self, node: AddressableNode) -> None:
        self.max_regwidth_stack.append(0)

    def exit_AddressableComponent(self, node: AddressableNode) -> None:
        max_block_regwidth = self.max_regwidth_stack.pop()
        if self.max_regwidth_stack:
            self.max_regwidth_stack[-1] = max(self.max_regwidth_stack[-1], max_block_regwidth)

        alignment = int(max_block_regwidth / 8)
        if (node.raw_address_offset % alignment) != 0:
            self.msg.error(
                f"Unaligned registers are not supported. Address offset of instance '{node.inst_name}' must be a multiple of {alignment}",
                node.inst.inst_src_ref
            )

        if node.is_array and (node.array_stride % alignment) != 0:
            self.msg.error(
                f"Unaligned registers are not supported. Address stride of instance array '{node.inst_name}' must be a multiple of {alignment}",
                node.inst.inst_src_ref
            )

    def enter_Component(self, node: 'Node') -> None:
        if node.external and (node != self.exp.top_node):
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
